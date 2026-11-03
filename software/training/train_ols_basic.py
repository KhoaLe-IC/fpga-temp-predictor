import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Đọc dữ liệu ----------
df = pd.read_csv("temperature.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
df = df.set_index("timestamp").sort_index()

if df.index.has_duplicates:
    raise ValueError("Timestamp bị trùng.")

T = df["temperature"].astype(float).asfreq("h")
T = T.where(np.isfinite(T))

# ---------- Tạo các tap ----------
data = pd.DataFrame(index=T.index)

data["t_now"] = T
data["t_minus_3"] = T.shift(3)
data["t_minus_21"] = T.shift(21)
data["t_minus_24"] = T.shift(24)

data["x1"] = data["t_now"] - data["t_minus_24"]
data["x2"] = data["t_now"] - data["t_minus_3"]

data["truth"] = T.shift(-3)
data["y"] = data["truth"] - data["t_minus_21"]
data["target_time"] = data.index + pd.Timedelta(hours=3)

# Chính sách đơn giản: cần đủ 25 giờ lịch sử liên tục.
history_ok = T.rolling(25, min_periods=25).count().eq(25)
data = data.loc[history_ok].dropna()

# ---------- Chia tập theo thời gian ----------
validation_start = pd.Timestamp("2024-01-01", tz="UTC")
test_start = pd.Timestamp("2025-01-01", tz="UTC")

# Nhãn train không được lấn sang validation.
train = data[data["target_time"] < validation_start]

validation = data[
    (data.index >= validation_start)
    & (data["target_time"] < test_start)
]

test = data[data.index >= test_start]

if min(len(train), len(validation), len(test)) == 0:
    raise ValueError("Có tập dữ liệu rỗng.")

print("Số mẫu train:", len(train))
print("Số mẫu validation:", len(validation))
print("Số mẫu test:", len(test))

def make_X(rows):
    return np.column_stack([
        rows["x1"].to_numpy(),
        rows["x2"].to_numpy(),
        np.ones(len(rows)),
    ])

# ---------- Huấn luyện OLS ----------
X_train = make_X(train)
y_train = train["y"].to_numpy()

weights, _, rank, _ = np.linalg.lstsq(
    X_train,
    y_train,
    rcond=None,
)

if rank < 3:
    raise ValueError("Không xác định được duy nhất ba hệ số.")

a, b, c = weights

print("\nHệ số đã học:")
print(f"a = {a:.12g}")
print(f"b = {b:.12g}")
print(f"c = {c:.12g}")

# ---------- Đánh giá ----------
def evaluate(rows, name):
    result = rows.copy()

    result["prediction"] = (
        rows["t_minus_21"].to_numpy()
        + make_X(rows) @ weights
    )

    predictions = {
        "Persistence": result["t_now"],
        "Diurnal": result["t_minus_21"],
        "Linear model": result["prediction"],
    }

    scores = []

    for model_name, prediction in predictions.items():
        error = prediction.to_numpy() - result["truth"].to_numpy()

        scores.append({
            "model": model_name,
            "MAE_C": np.mean(np.abs(error)),
            "RMSE_C": np.sqrt(np.mean(error ** 2)),
            "bias_C": np.mean(error),
        })

    scores = pd.DataFrame(scores)

    print(f"\n{name}")
    print(scores.to_string(index=False))

    return result, scores

validation_result, validation_scores = evaluate(
    validation, "VALIDATION"
)

# Chỉ sử dụng kết quả test cuối cùng sau khi chốt thiết kế.
test_result, test_scores = evaluate(test, "TEST")

# ---------- Xuất mô hình ----------
model = {
    "a": float(a),
    "b": float(b),
    "c": float(c),
    "horizon_hours": 3,
    "time_standard": "UTC",
    "train_target_end_exclusive": "2024-01-01T00:00:00Z",
}

with open("model.json", "w", encoding="utf-8") as f:
    json.dump(model, f, indent=2)

# Vector để đối chiếu C++.
test_result[[
    "target_time",
    "t_now",
    "t_minus_3",
    "t_minus_21",
    "t_minus_24",
    "truth",
    "prediction",
]].to_csv("test_vectors_float.csv", float_format="%.17g")

validation_scores.to_csv("validation_metrics.csv", index=False)
test_scores.to_csv("test_metrics.csv", index=False)

# ---------- Vẽ một tuần validation ----------
week = validation_result.loc[
    validation_result.index
    < validation_result.index[0] + pd.Timedelta(days=7)
]

plt.figure(figsize=(12, 4))
plt.plot(week["target_time"], week["truth"], label="Thực tế")
plt.plot(week["target_time"], week["prediction"], label="Dự báo +3 giờ")
plt.xlabel("Thời điểm cần dự báo — UTC")
plt.ylabel("Nhiệt độ (°C)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("validation_forecast.png", dpi=150)
plt.show()