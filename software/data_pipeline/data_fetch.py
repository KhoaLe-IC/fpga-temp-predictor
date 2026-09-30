from pathlib import Path
import json

import numpy as np
import pandas as pd
import requests

LATITUDE = 10.8231
LONGITUDE = 106.6297

base_dir = Path(__file__).resolve().parent
raw_dir = base_dir / "raw_data"
raw_dir.mkdir(exist_ok=True)

series = []

for year in range(2021, 2026):
    raw_file = raw_dir / f"power_{year}.json"

    # Lưu dữ liệu gốc để có thể chạy lại mà không tải lại.
    if raw_file.exists():
        payload = json.loads(raw_file.read_text(encoding="utf-8"))
    else:
        print(f"Đang tải năm {year}...")

        response = requests.get(
            "https://power.larc.nasa.gov/api/temporal/hourly/point",
            params={
                "parameters": "T2M",
                "community": "SB",
                "longitude": LONGITUDE,
                "latitude": LATITUDE,
                "start": f"{year}0101",
                "end": f"{year}1231",
                "format": "JSON",
                "time-standard": "UTC",
            },
            timeout=180,
        )
        response.raise_for_status()
        payload = response.json()

        # Kiểm tra có dữ liệu trước khi lưu.
        if "T2M" not in payload.get("properties", {}).get("parameter", {}):
            raise ValueError(f"Phản hồi không có T2M: {payload}")

        raw_file.write_text(
            json.dumps(payload),
            encoding="utf-8",
        )

    values = payload["properties"]["parameter"]["T2M"]
    s = pd.Series(values, dtype="float64")

    # Timestamp NASA có dạng YYYYMMDDHH.
    s.index = pd.to_datetime(
        s.index,
        format="%Y%m%d%H",
        utc=True,
    )

    # Đọc giá trị báo thiếu từ metadata.
    fill_value = payload.get("header", {}).get("fill_value", -999)
    s = s.mask(s == float(fill_value))
    s = s.where(np.isfinite(s))

    series.append(s)

temperature = pd.concat(series).sort_index()

if temperature.index.has_duplicates:
    raise ValueError("Dữ liệu có timestamp trùng.")

# Giữ đầy đủ trục giờ, kể cả các giờ không có dữ liệu.
timeline = pd.date_range(
    "2021-01-01 00:00",
    "2025-12-31 23:00",
    freq="h",
    tz="UTC",
)

temperature = temperature.reindex(timeline)
temperature.name = "temperature"
temperature.index.name = "timestamp"

temperature.to_csv(base_dir / "temperature.csv")

print("Đã lưu temperature.csv")
print("Tổng số giờ:", len(temperature))
print("Số giờ thiếu:", temperature.isna().sum())
print(temperature.describe())
