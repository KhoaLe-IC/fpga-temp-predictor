#!/usr/bin/env python3
"""RBF nho du bao nhiet do +3 gio: 12 inputs -> 16 Gaussian RBF -> 1 output.

Cai: python -m pip install numpy pandas scikit-learn
Chay: python Training_RBF.py --csv temperature.csv
Bien dich: g++ -std=c++17 -O2 C_model_RBF.cpp -o rbf
Du bao mau: ./rbf rbf_output/model_rbf.txt

Dung lai temperature.csv va split cua Training_1.py / Training_2.py.
T_hat(t+3) = T(t-21) + bias + sum_j w_j exp(-gamma ||z-center_j||^2).
StandardScaler va KMeans chi fit tren train. Chon gamma/alpha tren validation.
C++ doc model_rbf.txt duoc sinh sau khi train; khong can thu vien ML.
Day la floating-point reference, CHUA phai fixed-point/bit-exact RTL.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
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


def squared_distances(Z, centers):
    # Tinh truc tiep de tranh cancellation cua ||z||^2+||c||^2-2*z*c.
    return np.column_stack([np.sum((Z - c) ** 2, axis=1) for c in centers])


def export_model(path, scaler, centers, gamma, ridge):
    # Header: magic version input_count center_count gamma bias.
    # Tiep theo: mean[12], scale[12], centers[16][12], weights[16].
    with path.open('w', encoding='ascii') as f:
        f.write(f'RBF_TEMP 1 12 16 {gamma:.17g} {float(ridge.intercept_):.17g}\n')
        for values in [scaler.mean_, scaler.scale_, *centers, ridge.coef_]:
            f.write(' '.join(f'{float(v):.17g}' for v in values) + '\n')


def main():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, default=base / 'temperature.csv')
    parser.add_argument('--out-dir', type=Path, default=base / 'rbf_output')
    args = parser.parse_args()
    data = load_data(args.csv)
    validation_start = pd.Timestamp('2024-01-01', tz='UTC')
    test_start = pd.Timestamp('2025-01-01', tz='UTC')
    train = data[data['target_time'] < validation_start]
    validation = data[(data.index >= validation_start) & (data['target_time'] < test_start)]
    test = data[data.index >= test_start]
    if len(train) < 16 or validation.empty or test.empty:
        raise ValueError('Can train truoc 2024 (>=16 mau), validation 2024, test tu 2025.')
    print(f'Train={len(train)}, validation={len(validation)}, test={len(test)}', flush=True)
    scaler = StandardScaler().fit(train[FEATURES].to_numpy())
    Z_train = scaler.transform(train[FEATURES].to_numpy())
    Z_val = scaler.transform(validation[FEATURES].to_numpy())
    y_train = train['y'].to_numpy()
    centers = KMeans(n_clusters=16, n_init=10, random_state=42).fit(Z_train).cluster_centers_
    D_train, D_val = squared_distances(Z_train, centers), squared_distances(Z_val, centers)

    # Lua chon gioi han truoc; khong thay doi cau hinh dua tren test.
    alphas = (0.01, 0.1, 1.0, 10.0, 100.0, 1000.0)
    best, candidates = None, []
    for gamma in (0.01, 0.03, 0.1, 0.3, 1.0):
        Phi_train, Phi_val = np.exp(-gamma * D_train), np.exp(-gamma * D_val)
        for alpha in alphas:
            model = Ridge(alpha=alpha, solver='svd').fit(Phi_train, y_train)
            prediction = validation['anchor'].to_numpy() + model.predict(Phi_val)
            mae = metrics(validation['truth'], prediction)['MAE_C']
            candidates.append({'gamma': gamma, 'alpha': alpha, 'validation_MAE_C': mae})
            print(f'gamma={gamma:g}, alpha={alpha:g}: validation MAE={mae:.6f}', flush=True)
            if best is None or mae < best[0]:
                best = (mae, gamma, alpha, model)
    best_mae, gamma, alpha, rbf_model = best

    # Huan luyen lai hai mo hinh cu de so sanh cong bang tren cung split.
    old_weights = np.linalg.lstsq(old_X(train), y_train, rcond=None)[0]
    ridge_scaler = StandardScaler().fit(train[FEATURES[:6]].to_numpy())
    R_train = ridge_scaler.transform(train[FEATURES[:6]].to_numpy())
    R_val = ridge_scaler.transform(validation[FEATURES[:6]].to_numpy())
    best_ridge = None
    for a in alphas:
        model = Ridge(alpha=a, solver='svd').fit(R_train, y_train)
        prediction = validation['anchor'].to_numpy() + model.predict(R_val)
        mae = metrics(validation['truth'], prediction)['MAE_C']
        if best_ridge is None or mae < best_ridge[0]:
            best_ridge = (mae, a, model)
    _, ridge_alpha, ridge_model = best_ridge

    args.out_dir.mkdir(parents=True, exist_ok=True)
    export_model(args.out_dir / 'model_rbf.txt', scaler, centers, gamma, rbf_model)
    pd.DataFrame(candidates).to_csv(args.out_dir / 'validation_candidates.csv', index=False)
    scores = []
    for split, rows in [('validation', validation), ('test', test)]:
        Z = scaler.transform(rows[FEATURES].to_numpy())
        Phi = np.exp(-gamma * squared_distances(Z, centers))
        predictions = {
            'Persistence': rows['current'].to_numpy(),
            'Diurnal': rows['anchor'].to_numpy(),
            'Model1_OLS': rows['anchor'].to_numpy() + old_X(rows) @ old_weights,
            'Model2_Ridge6': rows['anchor'].to_numpy() + ridge_model.predict(
                ridge_scaler.transform(rows[FEATURES[:6]].to_numpy())),
            'RBF_12_16_1': rows['anchor'].to_numpy() + rbf_model.predict(Phi),
        }
        result = rows[['target_time', 'truth']].copy()
        for name, prediction in predictions.items():
            result[name] = prediction
            scores.append({'split': split, 'model': name, **metrics(rows['truth'], prediction)})
        result.to_csv(args.out_dir / f'{split}_predictions.csv', index_label='timestamp', float_format='%.17g')
        if split == 'test':
            inputs = rows[['hour_utc'] + [f't{lag}' for lag in TAPS]].to_numpy()
            np.savetxt(args.out_dir / 'test_inputs.txt', inputs, fmt=['%d'] + ['%.17g'] * len(TAPS))
            np.savetxt(args.out_dir / 'test_expected.txt', predictions['RBF_12_16_1'], fmt='%.17g')
    score_table = pd.DataFrame(scores)
    score_table.to_csv(args.out_dir / 'metrics.csv', index=False)
    metadata = {
        'architecture': [12, 16, 1], 'features': FEATURES,
        'formula': 'T(t-21) + bias + sum(w_j * exp(-gamma * squared_distance(z, center_j)))',
        'horizon_hours': 3, 'time_standard': 'UTC', 'numeric_type': 'float64',
        'gamma': gamma, 'alpha': alpha, 'ridge6_alpha': ridge_alpha, 'random_state': 42,
        'train_target_end_exclusive': str(validation_start),
        'validation_target_end_exclusive': str(test_start), 'test_origin_start': str(test_start),
        'counts': {'train': len(train), 'validation': len(validation), 'test': len(test)},
        'model_parameters': 210, 'normalization_values': 24,
    }
    (args.out_dir / 'training_info.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(f'\nSelected gamma={gamma}, alpha={alpha}; validation MAE={best_mae:.6f}')
    print(score_table.to_string(index=False))
    print(f'\nSaved: {args.out_dir / "model_rbf.txt"}')
    print('Evaluate actual test results; improvement over older models is not guaranteed.')


if __name__ == '__main__':
    main()
