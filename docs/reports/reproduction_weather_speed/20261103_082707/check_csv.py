import csv
import os
from pathlib import Path

path = Path(os.environ['RUN_DIR']) / os.environ.get('CSV_NAME', 'ordinary_replay.csv')
with path.open(newline='') as stream:
    rows = list(csv.DictReader(stream))
assert len(rows) == 128, f'Expected 128 rows, got {len(rows)}'
for index, row in enumerate(rows):
    assert int(row['sample_index']) == index
    assert int(row['accepted_count']) == index + 1
    assert int(row['forecast_count']) == max(0, index - 23)
    expected = 'warmup' if index < 24 else 'True'
    assert row['match'] == expected, (index, row['match'])
print('PASS CSV: 128 inputs, 24 warm-up rows, 104 matching forecasts')
print('First forecast:', rows[24]['forecast_physical'])
print('Last forecast: ', rows[-1]['forecast_physical'])
print('CSV:', path)

vectors = Path('hardware/jtag/vectors/weather.txt').read_text().splitlines()
for i, row in enumerate(rows[24:],24):
    actual = (int(row['probe_hex'],16) >> 108) & 262143
    expected = (int(vectors[i].split()[4],16) >> 108) & 262143
    assert 0 <= actual < 92160 and 0 <= expected < 92160, (i, actual, expected)
    delta = abs(actual - expected)
    assert min(delta,92160-delta) <= 5
print('PASS ANGLE DOMAIN AND CIRCULAR TOLERANCE: 104 forecasts, tolerance 5 Q8')
