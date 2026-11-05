"""Edge and random cases for weather_lcd_text.v, expected text from lcd_reference.lcd_lines."""
import random, sys
sys.path.insert(0, __file__.rsplit("/tb/", 1)[0] + "/host")
from lcd_reference import lcd_lines, MASK18

cases = [  # temperature, pressure, humidity, wind, angle, defined (raw Q8)
    (6770, 25736, 17829, 841, 1392, 1), (0, 0, 0, 0, 0, 1), (-1, 0, 0, 0, 0, 0), (-1307, 25600, 25600, 2560, 92031, 1),
    (-131072, 131071, 25600, 131071, 92159, 1), (131071, 25700, 25472, 2547, 91999, 1), (25599, 128, 127, 12, 128, 1),
    (-25599, 25727, 25599, 25599, 127, 0), (2559, 25562, 12800, 63, 46080, 1)]
random.seed(1)
for _ in range(300):
    cases.append((random.randint(-131072, 131071), random.randint(-1000, 131071), random.randint(0, 25600),
                  random.randint(0, 131071), random.randint(0, 92159), random.randint(0, 1)))
with open(sys.argv[1], "w") as f:
    f.write(f"{len(cases)}\n")
    for t, p, h, w, a, d in cases:
        word = (t & MASK18) | (p & MASK18) << 18 | (h & MASK18) << 36 | (w & MASK18) << 54 | (a & MASK18) << 108
        l1, l2 = lcd_lines([t, p, h, w, 0, 0], a, bool(d))
        f.write(f"{word:032x} {d} {(l1 + l2).encode().hex()}\n")
