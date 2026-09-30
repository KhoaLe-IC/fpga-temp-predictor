#!/usr/bin/env python3
"""Du bao nhiet do +3 gio bang 32 shallow gradient-boosted regression trees.

Cai: python -m pip install numpy pandas scikit-learn
Chay: python Training_BoostedTrees.py --csv temperature.csv
Sau do: g++ -std=c++17 -O2 C_model_BoostedTrees.cpp -o boosted
        ./boosted boosted_output/model_boosted.txt

Dung lai CSV timestamp (UTC), temperature va cach chia tap cua Training_1/2.
Mo hinh: T_hat(t+3) = T(t-21) + base + sum(tree_leaf).
32 cay, do sau toi da 3; learning rate duoc gop vao gia tri la khi xuat.
Chi chon learning rate tren validation; test khong tham gia huan luyen/chon.
Day la floating-point reference, CHUA phai fixed-point/bit-exact RTL.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


# Sau dac trung dau giong Training_2.py; tong cong 12 dac trung.
FEATURES = [
    "x1", "x2", "x3", "x4", "x5", "x6", "current", "anchor",
    "delta6", "delta12", "sin_hour", "cos_hour",
]
TAPS = [0, 1, 2, 3, 6, 12, 21, 22, 23, 24]


def load_data(path):
    df = pd.read_csv(path)
    if not {"timestamp", "temperature"}.issubset(df.columns):
        raise ValueError("CSV phai co timestamp va temperature.")
    timestamp = pd.to_datetime(df["timestamp"], utc=True, errors="raise")
    if timestamp.isna().any() or timestamp.duplicated().any():
        raise ValueError("Timestamp thieu hoac trung.")
    if not timestamp.eq(timestamp.dt.floor("h")).all():
        raise ValueError("Timestamp phai nam dung dau gio.")
    values = pd.to_numeric(df["temperature"], errors="raise").to_numpy(float)
    T = pd.Series(values, index=pd.DatetimeIndex(timestamp)).sort_index().asfreq("h")
    T = T.where(np.isfinite(T) & T.ne(-999.0))

    data = pd.DataFrame(index=T.index)
    for lag in TAPS:
        data[f"t{lag}"] = T.shift(lag)
    data["x1"] = T - T.shift(24)
    data["x2"] = T - T.shift(1)
    data["x3"] = T.shift(1) - T.shift(2)
    data["x4"] = T.shift(2) - T.shift(3)
    data["x5"] = T.shift(21) - T.shift(22)
    data["x6"] = T.shift(22) - T.shift(23)
    data["current"] = T
    data["anchor"] = T.shift(21)
    data["delta6"] = T - T.shift(6)
    data["delta12"] = T - T.shift(12)
    data["hour_utc"] = data.index.hour
    angle = 2 * np.pi * data["hour_utc"] / 24
    data["sin_hour"] = np.sin(angle)
    data["cos_hour"] = np.cos(angle)
    data["truth"] = T.shift(-3)
    data["y"] = data["truth"] - data["anchor"]
    data["target_time"] = data.index + pd.Timedelta(hours=3)

    # Khong noi suy bang du lieu tuong lai. Can du 25 gio lich su lien tuc.
    history_ok = T.rolling(25, min_periods=25).count().eq(25)
    return data.loc[history_ok].dropna()


def metrics(truth, prediction):
    error = np.asarray(prediction) - np.asarray(truth)
    return {
        "MAE_C": float(np.mean(np.abs(error))),
        "RMSE_C": float(np.sqrt(np.mean(error ** 2))),
        "bias_C": float(np.mean(error)),
    }


def old_X(rows):
    return np.column_stack([
        rows["x1"], rows["t0"] - rows["t3"], np.ones(len(rows)),
    ])


def export_model(model, path):
    """Text format V1; C++ doc bang standard library, khong can JSON library.

    Header: magic version feature_count tree_count base
    Moi cay: node_count, roi cac dong feature threshold left right leaf_value.
    Node duoc danh so tu 0. Leaf: feature=-1, left=right=-1.
    Threshold giu float64, input cay duoc ep float32 nhu sklearn.
    """
    trees = model.estimators_.ravel()
    base = float(model.init_.constant_.ravel()[0])
    with path.open("w", encoding="ascii") as f:
        f.write(f"BOOSTED_TEMP 1 {len(FEATURES)} {len(trees)} {base:.17g}\n")
        for estimator in trees:
            tree = estimator.tree_
            f.write(f"{tree.node_count}\n")
            for i in range(tree.node_count):
                left, right = int(tree.children_left[i]), int(tree.children_right[i])
                if left == -1:
                    value = model.learning_rate * float(tree.value[i, 0, 0])
                    f.write(f"-1 0 -1 -1 {value:.17g}\n")
                else:
                    f.write(f"{int(tree.feature[i])} {tree.threshold[i]:.17g} "
                            f"{left} {right} 0\n")


def main():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=base / "temperature.csv")
    parser.add_argument("--out-dir", type=Path, default=base / "boosted_output")
    args = parser.parse_args()
    data = load_data(args.csv)

    validation_start = pd.Timestamp("2024-01-01", tz="UTC")
    test_start = pd.Timestamp("2025-01-01", tz="UTC")
    train = data[data["target_time"] < validation_start]
    validation = data[(data.index >= validation_start) & (data["target_time"] < test_start)]
    test = data[data.index >= test_start]
    if min(len(train), len(validation), len(test)) == 0:
        raise ValueError("Can train truoc 2024, validation 2024, test tu 2025.")
    print(f"Train={len(train)}, validation={len(validation)}, test={len(test)}")

    # Tree models khong can StandardScaler. Ep float32 ro rang cho C++ doi chieu.
    X_train = train[FEATURES].to_numpy(dtype=np.float32)
    X_val = validation[FEATURES].to_numpy(dtype=np.float32)
    y_train = train["y"].to_numpy()
    candidates = []
    best = None
    for learning_rate in (0.05, 0.1, 0.2):
        model = GradientBoostingRegressor(
            n_estimators=32, max_depth=3, min_samples_leaf=20,
            learning_rate=learning_rate, loss="squared_error",
            subsample=1.0, random_state=42,
        )
        model.fit(X_train, y_train)
        prediction = validation["anchor"].to_numpy() + model.predict(X_val)
        mae = metrics(validation["truth"], prediction)["MAE_C"]
        candidates.append({"learning_rate": learning_rate, "validation_MAE_C": mae})
        print(f"32 trees, depth<=3, learning_rate={learning_rate}: validation MAE={mae:.6f}")
        if best is None or mae < best[0]:
            best = (mae, model)
    best_mae, model = best

    # Huan luyen lai dung hai cong thuc cu de so sanh cung tap du lieu.
    old_weights = np.linalg.lstsq(old_X(train), y_train, rcond=None)[0]
    scaler = StandardScaler().fit(train[FEATURES[:6]].to_numpy())
    Z_train = scaler.transform(train[FEATURES[:6]].to_numpy())
    Z_val = scaler.transform(validation[FEATURES[:6]].to_numpy())
    best_ridge = None
    for alpha in (0.01, 0.1, 1.0, 10.0, 100.0, 1000.0):
        ridge = Ridge(alpha=alpha, solver="svd").fit(Z_train, y_train)
        prediction = validation["anchor"].to_numpy() + ridge.predict(Z_val)
        mae = metrics(validation["truth"], prediction)["MAE_C"]
        if best_ridge is None or mae < best_ridge[0]:
            best_ridge = (mae, ridge)
    ridge = best_ridge[1]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    export_model(model, args.out_dir / "model_boosted.txt")
    pd.DataFrame(candidates).to_csv(args.out_dir / "validation_candidates.csv", index=False)
    scores = []
    for split, rows in (("validation", validation), ("test", test)):
        predictions = {
            "Persistence": rows["current"].to_numpy(),
            "Diurnal": rows["anchor"].to_numpy(),
            "Model1_OLS": rows["anchor"].to_numpy() + old_X(rows) @ old_weights,
            "Model2_Ridge6": rows["anchor"].to_numpy() + ridge.predict(
                scaler.transform(rows[FEATURES[:6]].to_numpy())),
            "BoostedTrees32": rows["anchor"].to_numpy() + model.predict(
                rows[FEATURES].to_numpy(dtype=np.float32)),
        }
        result = rows[["target_time", "truth"]].copy()
        for name, prediction in predictions.items():
            result[name] = prediction
            scores.append({"split": split, "model": name, **metrics(rows["truth"], prediction)})
        result.to_csv(args.out_dir / f"{split}_predictions.csv",
                      index_label="timestamp", float_format="%.17g")
        if split == "test":
            # Dung: ./boosted boosted_output/model_boosted.txt --batch \
            #       < boosted_output/test_inputs.txt > cpp_predictions.txt
            inputs = rows[["hour_utc"] + [f"t{lag}" for lag in TAPS]].to_numpy()
            np.savetxt(args.out_dir / "test_inputs.txt", inputs, fmt=["%d"] + ["%.17g"] * len(TAPS))
            np.savetxt(args.out_dir / "test_expected.txt", predictions["BoostedTrees32"], fmt="%.17g")
    scores = pd.DataFrame(scores)
    scores.to_csv(args.out_dir / "metrics.csv", index=False)
    print(f"\nChosen learning_rate={model.learning_rate}, validation MAE={best_mae:.6f}")
    print(scores.to_string(index=False))
    print(f"\nModel saved: {args.out_dir / 'model_boosted.txt'}")
    print("No guarantee of improvement; compare measured test MAE with both old models.")


if __name__ == "__main__":
    main()
