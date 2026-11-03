import json

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

# ---------- Đọc dữ liệu ----------
df = pd.read_csv("temperature.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
df = df.set_index("timestamp").sort_index()

if df.index.has_duplicates:
    raise ValueError("Timestamp bị trùng.")

T = df["temperature"].astype(float).asfreq("h")
T = T.where(np.isfinite(T))

# ---------- Tạo đặc trưng ----------
data = pd.DataFrame(index=T.index)

data["x1"] = T - T.shift(24)
data["x2"] = T - T.shift(1)
data["x3"] = T.shift(1) - T.shift(2)
data["x4"] = T.shift(2) - T.shift(3)
data["x5"] = T.shift(21) - T.shift(22)
data["x6"] = T.shift(22) - T.shift(23)

data["anchor"] = T.shift(21)
data["current"] = T
data["truth"] = T.shift(-3)
data["y"] = data["truth"] - data["anchor"]
data["target_time"] = data.index + pd.Timedelta(hours=3)

history_ok = T.rolling(25, min_periods=25).count().eq(25)
data = data.loc[history_ok].dropna()

validation_start = pd.Timestamp("2024-01-01", tz="UTC")
test_start = pd.Timestamp("2025-01-01", tz="UTC")

train = data[data["target_time"] < validation_start]

validation = data[
    (data.index >= validation_start)
    & (data["target_time"] < test_start)
]

if train.empty or validation.empty:
    raise ValueError("Không đủ dữ liệu train hoặc validation.")

features = ["x1", "x2", "x3", "x4", "x5", "x6"]

X_train = train[features].to_numpy()
X_val = validation[features].to_numpy()
y_train = train["y"].to_numpy()

truth = validation["truth"].to_numpy()
anchor = validation["anchor"].to_numpy()

def mae(prediction):
    return np.mean(np.abs(prediction - truth))

# ---------- Huấn luyện lại mô hình cũ để so sánh ----------
def old_X(rows):
    return np.column_stack([
        rows["x1"],
        rows["x2"] + rows["x3"] + rows["x4"],
        np.ones(len(rows)),
    ])

old_weights = np.linalg.lstsq(
    old_X(train), y_train, rcond=None
)[0]

old_prediction = anchor + old_X(validation) @ old_weights
old_mae = mae(old_prediction)

print(f"Persistence MAE: {mae(validation['current'].to_numpy()):.6f}")
print(f"Diurnal MAE:     {mae(anchor):.6f}")
print(f"Mô hình cũ MAE: {old_mae:.6f}")

# ---------- Chuẩn hóa chỉ bằng dữ liệu train ----------
scaler = StandardScaler()
Z_train = scaler.fit_transform(X_train)
Z_val = scaler.transform(X_val)

# ---------- Chọn alpha trên validation ----------
best = None

for alpha in [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]:
    model = Ridge(alpha=alpha, solver="svd")
    model.fit(Z_train, y_train)

    prediction = anchor + model.predict(Z_val)
    score = mae(prediction)

    print(f"Ridge alpha={alpha:7g}: MAE={score:.6f}")

    if best is None or score < best["mae"]:
        best = {
            "alpha": alpha,
            "mae": score,
            "model": model,
        }

# ---------- Gộp chuẩn hóa vào hệ số ----------
# FPGA sẽ dùng trực tiếp x1...x6, không cần StandardScaler.
model = best["model"]

weights = model.coef_ / scaler.scale_
intercept = model.intercept_ - np.dot(weights, scaler.mean_)

# Kiểm tra công thức sau khi gộp.
prediction_direct = anchor + X_val @ weights + intercept
prediction_scaled = anchor + model.predict(Z_val)

np.testing.assert_allclose(
    prediction_direct,
    prediction_scaled,
    rtol=1e-12,
    atol=1e-10,
)

print("\nCấu hình được chọn:")
print("alpha =", best["alpha"])
print("MAE validation =", best["mae"])
print(
    "Mức giảm MAE so với mô hình cũ: "
    f"{100 * (old_mae - best['mae']) / old_mae:.2f}%"
)

for name, weight in zip(features, weights):
    print(f"{name}: {weight:.12g}")
print(f"c: {intercept:.12g}")

# ---------- Xuất hệ số để dùng trong C++ ----------
output = {
    "model": "diurnal_anchor_ridge_6_features",
    "features": features,
    "weights": weights.tolist(),
    "intercept": float(intercept),
    "alpha": float(best["alpha"]),
    "validation_mae_C": float(best["mae"]),
    "horizon_hours": 3,
}

with open("model_ridge6.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

validation_output = validation.copy()
validation_output["prediction_old"] = old_prediction
validation_output["prediction_ridge6"] = prediction_direct

validation_output.to_csv(
    "validation_ridge6.csv",
    float_format="%.17g",
)