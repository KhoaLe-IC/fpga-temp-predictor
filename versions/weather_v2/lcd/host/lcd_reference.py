"""Fixed-point reference for the 25-frame window / LCD variant.

Mirrors the deployed RTL bit for bit:
  inputs  : round-half-away-from-zero to signed 18-bit Q8 (same rule as make_vectors.py)
  lanes   : sum(x_q8 * w_q14) + bias_q8 * 2^14, floor-shift by 14, physical limits, 18-bit saturation
  angle   : wind_direction_cordic.v (16-step vectoring CORDIC, degrees Q8)
  LCD     : weather_lcd_text.v (two 16-character lines)

CLI:
  python3 lcd_reference.py window --end "2025-03-24 05:00" --out window.csv
      writes the 25 hourly frames ending at that UTC hour and prints the expected forecast and LCD text
  python3 lcd_reference.py expect window.csv
      prints the expected forecast and LCD text for any window CSV (no dataset needed)
  python3 lcd_reference.py tb --out <file> --end <ts> [--end <ts> ...]
      writes simulation vectors (payload words, expected result word, expected LCD lines)
  python3 lcd_reference.py selfcheck
      re-derives the verified board replay (hardware/jtag/vectors/weather.txt) from the model
"""
import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MODEL = json.loads((ROOT / "versions/weather_v2/models/model.json").read_text())
LAGS = MODEL["lags_hours"]
WQ = MODEL["weights_q14"]
BQ = MODEL["bias_q8"]
ATAN_Q16 = [2949120, 1740967, 919879, 466945, 234379, 117304, 58666, 29335, 14668, 7334, 3667, 1833, 917, 458, 229, 115]
MASK18 = (1 << 18) - 1


def q8(x):
    """Round half away from zero to Q8 (make_vectors.py rule)."""
    return int(math.copysign(math.floor(abs(x) * 256 + 0.5), x))


def frame_q8(t, p, rh, ws, wd_deg):
    r = math.radians(wd_deg)
    return [q8(t), q8(p), q8(rh), q8(ws), q8(math.cos(r)), q8(math.sin(r))]


def predict(window):
    """window: 25 frames of 6 Q8 ints, oldest first. Returns 6 lane outputs (signed Q8)."""
    assert len(window) == 25
    out = []
    for c in range(6):
        acc = BQ[c] * 16384
        for k, lag in enumerate(LAGS):
            acc += window[24 - lag][c] * WQ[c][k * 6 + c]
        v = acc >> 14  # arithmetic shift = floor division
        if c == 2:
            v = min(max(v, 0), 25600)
        if c == 3:
            v = max(v, 0)
        if c >= 4:
            v = min(max(v, -256), 256)
        out.append(min(max(v, -131072), 131071))
    return out


def cordic(cos_q8, sin_q8):
    """Bit-accurate copy of wind_direction_cordic.v -> (angle Q8 degrees, defined)."""
    if cos_q8 < 0:
        x, y, ang = -cos_q8 * 65536, -sin_q8 * 65536, (-11796480 if sin_q8 < 0 else 11796480)
    else:
        x, y, ang = cos_q8 * 65536, sin_q8 * 65536, 0
    for i in range(16):
        if y > 0:
            x, y, ang = x + (y >> i), y - (x >> i), ang + ATAN_Q16[i]
        elif y < 0:
            x, y, ang = x - (y >> i), y + (x >> i), ang - ATAN_Q16[i]
    defined = cos_q8 != 0 or sin_q8 != 0
    w = ang + 23592960 if ang < 0 else ang
    return ((w >> 8) & MASK18) if defined else 0, defined


def result_word(lanes, angle):
    word = 0
    for c, v in enumerate(lanes + [angle]):
        word |= (v & MASK18) << (18 * c)
    return word


def payload_word(frame):
    word = 0
    for c, v in enumerate(frame):
        word |= (v & MASK18) << (18 * c)
    return word


def lcd_lines(lanes, angle, defined):
    """Same rules as weather_lcd_text.v."""
    t, p, h, w = lanes[:4]
    neg = t < 0
    t10 = min((abs(t) * 10 + 128) >> 8, 999)
    p100 = (max(p, 0) * 100 + 128) >> 8
    hp = (max(h, 0) + 128) >> 8
    w10 = min((max(w, 0) * 10 + 128) >> 8, 999)
    deg = (angle + 128) >> 8
    deg = 0 if deg >= 360 else deg

    def pad(n, width):  # leading zeros -> spaces, keep the last digit
        return str(n).rjust(width)

    line1 = f"T{'-' if neg else '+'}{pad(t10 // 10, 2)}.{t10 % 10}C P{pad(p100 // 100, 3)}.{p100 % 100:02d}"
    line1 = line1.ljust(16)
    line2 = f"H{pad(hp, 3)}% W{pad(w10 // 10, 2)}.{w10 % 10} D{pad(deg, 3) if defined else '---'}"
    assert len(line1) == 16 and len(line2) == 16, (line1, line2)
    return line1, line2


def load_rows():
    with open(ROOT / "versions/weather_v2/data/weather.csv") as f:
        return list(csv.DictReader(f))


def window_at(rows, end):
    key = end if "+" in end else end + (":00" if end.count(":") == 1 else "") + "+00:00"
    idx = {r["timestamp"]: i for i, r in enumerate(rows)}
    if key not in idx:
        raise SystemExit(f"timestamp not found: {key}")
    i = idx[key]
    if i < 24:
        raise SystemExit("need 24 earlier hours")
    return rows[i - 24: i + 1]


def evaluate(frames_q8):
    lanes = predict(frames_q8)
    angle, defined = cordic(lanes[4], lanes[5])
    return lanes, angle, defined


def describe(lanes, angle, defined):
    names = ["temperature C", "pressure kPa", "humidity %", "wind speed m/s", "direction cos", "direction sin"]
    s = [f"  {n:<15} {v / 256:10.4f}   (raw {v})" for n, v in zip(names, lanes)]
    s.append(f"  {'direction deg':<15} {angle / 256 if defined else float('nan'):10.4f}   (raw {angle}, defined={int(defined)})")
    return "\n".join(s)


def print_expected(rows):
    frames = [frame_q8(*(float(r[k]) for k in ("T2M", "PS", "RH2M", "WS10M", "WD10M"))) for r in rows]
    lanes, angle, defined = evaluate(frames)
    l1, l2 = lcd_lines(lanes, angle, defined)
    print("Expected fixed-point forecast for +3 h:")
    print(describe(lanes, angle, defined))
    print(f"Expected LCD:\n  |{l1}|\n  |{l2}|")


def cmd_window(a):
    rows = window_at(load_rows(), a.end)
    with open(a.out, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["timestamp", "T2M", "PS", "RH2M", "WS10M", "WD10M"])
        for r in rows:
            wr.writerow([r["timestamp"], r["T2M"], r["PS"], r["RH2M"], r["WS10M"], r["WD10M"]])
    print(f"Wrote {a.out}: 25 frames {rows[0]['timestamp']} .. {rows[-1]['timestamp']}")
    print_expected(rows)


def cmd_expect(a):
    with open(a.csv, newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 25:
        raise SystemExit(f"window must have exactly 25 frames, found {len(rows)}")
    print(f"{a.csv}: 25 frames {rows[0]['timestamp']} .. {rows[-1]['timestamp']}")
    print_expected(rows)


def cmd_tb(a):
    rows = load_rows()
    with open(a.out, "w") as f:
        f.write(f"{len(a.end)}\n")
        for end in a.end:
            win = window_at(rows, end)
            frames = [frame_q8(*(float(r[k]) for k in ("T2M", "PS", "RH2M", "WS10M", "WD10M"))) for r in win]
            lanes, angle, defined = evaluate(frames)
            l1, l2 = lcd_lines(lanes, angle, defined)
            for fr in frames:
                f.write(f"{payload_word(fr):027x}\n")
            f.write(f"{result_word(lanes, angle):032x} {int(defined)}\n")
            f.write((l1 + l2).encode().hex() + "\n")
            print(end, f"|{l1}|{l2}|")


def cmd_selfcheck(_a):
    """Feed the first 25 payloads of the verified replay through this reference."""
    lines = (ROOT / "hardware/jtag/vectors/weather.txt").read_text().split("\n")
    frames, checked = [], 0
    for ln in lines:
        if not ln.strip():
            continue
        stage, _commit, _cnt, fc, result = ln.split()
        payload = (int(stage, 16) >> 2) & ((1 << 108) - 1)
        fr = []
        for c in range(6):
            v = (payload >> (18 * c)) & MASK18
            fr.append(v - (1 << 18) if v & (1 << 17) else v)
        frames.append(fr)
        if int(fc) > 0:
            lanes, angle, _ = evaluate(frames[-25:])
            exp = int(result, 16)
            assert result_word(lanes, 0) & ((1 << 108) - 1) == exp & ((1 << 108) - 1), f"lane mismatch at {len(frames)}"
            ea = (exp >> 108) & MASK18
            d = abs(angle - ea)
            assert min(d, 92160 - d) <= 5, f"angle mismatch at {len(frames)}"
            checked += 1
    print(f"selfcheck PASS: {checked} forecasts from {len(frames)} frames match the verified replay vectors")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("window"); w.add_argument("--end", required=True); w.add_argument("--out", default="window.csv")
    t = sub.add_parser("tb"); t.add_argument("--end", action="append", required=True); t.add_argument("--out", required=True)
    e = sub.add_parser("expect"); e.add_argument("csv")
    sub.add_parser("selfcheck")
    a = ap.parse_args()
    {"window": cmd_window, "expect": cmd_expect, "tb": cmd_tb, "selfcheck": cmd_selfcheck}[a.cmd](a)
