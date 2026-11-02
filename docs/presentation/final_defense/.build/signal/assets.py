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


def to_rgba(acc, rgb, gamma=0.45, gain=2.0):
    a = acc / np.percentile(acc[acc > 0], 99.5)
    a = np.clip(a * gain, 0, 1) ** gamma
    img = np.zeros(acc.shape + (4,), np.uint8)
    img[..., :3] = rgb
    img[..., 3] = (a * 255).astype(np.uint8)
    return img


# Cover: all five years, one luminous ribbon
W, H = 4000, 1100
acc, _ = density(T, W, H)
Image.fromarray(to_rgba(acc, (94, 234, 212))).save(f"{OUT}/trace_cover.png")

# Split strip coloured by chronological role
W, H = 3700, 640
acc, t = density(T, W, H)
img = np.zeros((H, W, 4), np.uint8)
cols = {"train": (203, 213, 225), "val": (94, 234, 212), "test": (251, 191, 36)}
yr_at_col = np.interp(np.arange(W), np.linspace(0, W - 1, len(T)), years)
for name, mask in [("train", yr_at_col < 2024), ("val", (yr_at_col >= 2024) & (yr_at_col < 2025)), ("test", yr_at_col >= 2025)]:
    part = acc * mask[None, :]
    layer = to_rgba(part, cols[name], gain=2.0)
    sel = layer[..., 3] > img[..., 3]
    img[sel] = layer[sel]
Image.fromarray(img).save(f"{OUT}/trace_split.png")

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
