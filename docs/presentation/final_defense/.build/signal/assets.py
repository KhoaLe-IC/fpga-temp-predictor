"""Data-driven artwork for the defense deck: every trace is real NASA POWER data."""
import csv, json, sys
import numpy as np
from PIL import Image

ROOT, OUT = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(f"{ROOT}/versions/weather_v2/data/weather.csv")))
T = np.array([float(r["T2M"]) for r in rows])
years = np.array([int(r["timestamp"][:4]) for r in rows])


def density(values, W, H, pad=0.08, sub=6):
    """Accumulate a polyline into a density raster (column = time)."""
    n = len(values)
    lo, hi = values.min(), values.max()
    t = np.linspace(0, n - 1, (n - 1) * sub + 1)
    v = np.interp(t, np.arange(n), values)
    x = (t / (n - 1) * (W - 1)).astype(int)
    y = ((1 - pad) - (v - lo) / (hi - lo) * (1 - 2 * pad)) * (H - 1)
    acc = np.zeros((H, W))
    np.add.at(acc, (y.astype(int), x), 1.0)
    return acc, t


def to_rgba(acc, rgb, gamma=0.55, gain=5.0):
    a = acc / np.percentile(acc[acc > 0], 99.5)
    a = np.clip(a * gain, 0, 1) ** gamma
    img = np.zeros(acc.shape + (4,), np.uint8)
    img[..., :3] = rgb
    img[..., 3] = (a * 255).astype(np.uint8)
    return img


# Printed-chart artwork: daily min-max band plus daily mean, drawn from all hourly samples
from PIL import ImageDraw
days = T[: len(T) // 24 * 24].reshape(-1, 24)
dmin, dmax, dmean = days.min(1), days.max(1), days.mean(1)
dyear = years[: len(days) * 24 : 24]


def band_chart(path, W, H, colour_of_day, pad=0.06, ss=2):
    W2, H2 = W * ss, H * ss
    lo, hi = dmin.min(), dmax.max()
    X = lambda i: i / (len(days) - 1) * (W2 - 1)
    Y = lambda v: ((1 - pad) - (v - lo) / (hi - lo) * (1 - 2 * pad)) * (H2 - 1)
    img = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(len(days) - 1):  # band, one quad per day
        r, g, b = colour_of_day(i)
        d.polygon([(X(i), Y(dmax[i])), (X(i + 1), Y(dmax[i + 1])), (X(i + 1), Y(dmin[i + 1])), (X(i), Y(dmin[i]))], fill=(r, g, b, 46))
    for i in range(len(days) - 1):  # mean line
        r, g, b = colour_of_day(i)
        d.line([(X(i), Y(dmean[i])), (X(i + 1), Y(dmean[i + 1]))], fill=(r, g, b, 255), width=3 * ss)
    img.resize((W, H), Image.LANCZOS).save(path)


NAVY = (30, 58, 95)
band_chart(f"{OUT}/trace_cover.png", 4000, 1100, lambda i: NAVY)
split_cols = {"train": (100, 116, 139), "val": NAVY, "test": (161, 98, 7)}
band_chart(f"{OUT}/trace_split.png", 3700, 640,
           lambda i: split_cols["train"] if dyear[i] < 2024 else split_cols["val"] if dyear[i] < 2025 else split_cols["test"])

# A real forecast window from the 2025 test period (12:00 ICT = 05:00 UTC)
m = json.load(open(f"{ROOT}/versions/weather_v2/models/model.json"))
w = [m["weights"][0][j * 6] for j in range(7)]
b = m["bias"][0]
idx = {r["timestamp"]: i for i, r in enumerate(rows)}
best = None
for d in range(60, 150):
    day = np.datetime64("2025-01-01") + np.timedelta64(d, "D")
    i = idx.get(f"{day} 05:00:00+00:00")
    if i is None:
        continue
    hist = T[i - 24:i + 1]
    pred = b + sum(wk * T[i - l] for wk, l in zip(w, m["lags_hours"]))
    err = abs(pred - T[i + 3])
    swing = hist.max() - hist.min()
    score = abs(err - 0.45) - 0.02 * swing
    if best is None or score < best[0]:
        best = (score, str(day), hist.tolist(), T[i + 1:i + 4].tolist(), float(pred))
_, day, hist, future, pred = best
json.dump({"day": day, "history": hist, "future": future, "pred": pred}, open(f"{OUT}/window.json", "w"))
print(day, hist[-1], "pred", round(pred, 2), "actual", future[-1])
