"""Image assets for the Claude revision deck.

Everything is derived from project data or native screenshots:
- split_chart.png: daily min/max band + daily mean of the NASA POWER hourly temperature record,
  coloured by chronological role (train / validation / test).
- cover_signaltap.png: grayscale crop of the native weather_speed SignalTap waveform screenshot,
  used only as a decorative cover image (evidence slides use the unmodified files).
- window.json: a real 2025 test-set window and the deployed temperature lane's float forecast.
Usage: python3 assets.py <project_root> <out_dir>
"""
import csv
import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT, OUT = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(f"{ROOT}/versions/weather_v2/data/weather.csv")))
T = np.array([float(r["T2M"]) for r in rows])
years = np.array([int(r["timestamp"][:4]) for r in rows])

# --- chronological split chart -------------------------------------------------------------
days = T[: len(T) // 24 * 24].reshape(-1, 24)
dmin, dmax, dmean = days.min(1), days.max(1), days.mean(1)
dyear = years[: len(days) * 24: 24]
COL = {"train": (35, 34, 34), "val": (128, 128, 128), "test": (255, 107, 0)}


def role(y):
    return "train" if y < 2024 else "val" if y < 2025 else "test"


W, H, ss, pad = 3600, 760, 2, 0.06
W2, H2 = W * ss, H * ss
lo, hi = dmin.min(), dmax.max()
X = lambda i: i / (len(days) - 1) * (W2 - 1)
Y = lambda v: ((1 - pad) - (v - lo) / (hi - lo) * (1 - 2 * pad)) * (H2 - 1)
img = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
d = ImageDraw.Draw(img, "RGBA")
for i in range(len(days) - 1):
    r, g, b = COL[role(dyear[i])]
    d.polygon([(X(i), Y(dmax[i])), (X(i + 1), Y(dmax[i + 1])), (X(i + 1), Y(dmin[i + 1])), (X(i), Y(dmin[i]))], fill=(r, g, b, 50))
for i in range(len(days) - 1):
    r, g, b = COL[role(dyear[i])]
    d.line([(X(i), Y(dmean[i])), (X(i + 1), Y(dmean[i + 1]))], fill=(r, g, b, 255), width=3 * ss)
img.resize((W, H), Image.LANCZOS).save(f"{OUT}/split_chart.png")

# --- decorative cover crop of the native SignalTap screenshot ------------------------------
st = Image.open(f"{ROOT}/docs/reports/defense_session/screenshots/weather_speed_signaltap_waveform.png").convert("RGB")
crop = st.crop((660, 95, 1660, 450))  # waveform area only: buses and the forecast_valid pulse
crop = ImageOps.autocontrast(ImageOps.grayscale(crop), cutoff=1)
w, h = crop.size
crop = crop.resize((w * 2, h * 2), Image.LANCZOS)
crop.save(f"{OUT}/cover_signaltap.png")

# --- real forecast window (12:00 ICT = 05:00 UTC) ------------------------------------------
m = json.load(open(f"{ROOT}/versions/weather_v2/models/model.json"))
wts = [m["weights"][0][j * 6] for j in range(7)]
b = m["bias"][0]
idx = {r["timestamp"]: i for i, r in enumerate(rows)}
i = idx["2025-03-24 05:00:00+00:00"]
hist = T[i - 24: i + 1].tolist()
pred = b + sum(wk * T[i - l] for wk, l in zip(wts, m["lags_hours"]))
json.dump({"day": "2025-03-24", "history": hist, "future": T[i + 1: i + 4].tolist(), "pred": float(pred),
           "weights": wts, "weights_q14": m["weights_q14"][0][:42:6] if isinstance(m["weights_q14"][0], list) else m["weights_q14"][:7],
           "bias_q8": m["bias_q8"]}, open(f"{OUT}/window.json", "w"), indent=1)
print("assets ok", round(pred, 2), T[i + 3])
