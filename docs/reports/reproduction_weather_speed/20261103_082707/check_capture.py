import csv
import os
import xml.etree.ElementTree as ET
from pathlib import Path

run_dir = Path(os.environ['RUN_DIR'])
path = run_dir / 'weather_speed_live.stp'
root = ET.parse(path).getroot()
signal_set = root.find('instance/signal_set')
assert signal_set is not None, 'SignalTap signal set is missing'
data = signal_set.find('trigger/log/data')
assert data is not None, 'No acquired data is saved in this STP'
count = int(data.get('sample_depth', '-1'))
trigger = int(data.get('trigger_position', '-1'))
names = [wire.get('name') for wire in
         signal_set.find('signal_vec/data_input_vec')]
bits = ''.join((data.text or '').split())
assert count == 512, ('Unexpected depth', count)
assert trigger == 256, ('Unexpected center trigger', trigger)
assert len(bits) == count * len(names), 'Acquisition data length is wrong'
assert set(bits) <= {'0', '1'}, 'Acquisition contains nonbinary data'
rows = [bits[i * len(names):(i + 1) * len(names)] for i in range(count)]
prefix = 'jtag_mailbox:mailbox|'
positions = {name: index for index, name in enumerate(names)}

def bit(index, name):
    return int(rows[index][positions[prefix + name]])

def bus(index, name, width):
    return sum(bit(index, f'{name}[{b}]') << b for b in range(width))

accepts = [i for i in range(count)
           if bit(i, 'sample_valid') and bit(i, 'sample_ready')]
valids = [i for i in range(count) if bit(i, 'forecast_valid')]
assert len(accepts) == 1 and len(valids) == 1, (accepts, valids)
assert all(bit(i, 'core_rst_n') for i in range(count))
accept, valid = accepts[0], valids[0]
assert valid - accept == 41, ('Unexpected capture separation', accept, valid)
vector_path = Path('hardware/jtag/vectors/weather.txt')
fields = vector_path.read_text().splitlines()[24].split()
expected_input = (int(fields[1], 16) >> 2) & ((1 << 108) - 1)
expected_output = int(fields[4], 16)
actual_input = bus(accept, 'sample_data', 108)
actual_output = bus(valid, 'forecast_data', 126)
assert actual_input == expected_input, 'Captured input differs from vector 25'
assert (actual_output & ((1 << 108) - 1)) == \
       (expected_output & ((1 << 108) - 1)), 'Forecast component mismatch'
angle = actual_output >> 108
expected_angle = expected_output >> 108
assert 0 <= angle < 92160, ('Actual angle outside [0,360)', angle)
assert 0 <= expected_angle < 92160, ('Expected angle outside [0,360)', expected_angle)
delta = abs(angle - expected_angle)
delta = min(delta, 92160 - delta)
assert delta <= 5, ('Direction tolerance exceeded', delta)
output = run_dir / 'weather_speed_live_decoded.csv'
with output.open('w', newline='') as stream:
    writer = csv.writer(stream)
    writer.writerow(['capture_index', 'relative_to_trigger', 'time_ns',
                     'core_rst_n', 'sample_valid', 'sample_ready',
                     'forecast_valid', 'sample_data_hex', 'forecast_data_hex'])
    for i in range(count):
        writer.writerow([i, i - trigger, (i - trigger) * 20,
                         bit(i, 'core_rst_n'), bit(i, 'sample_valid'),
                         bit(i, 'sample_ready'), bit(i, 'forecast_valid'),
                         hex(bus(i, 'sample_data', 108)),
                         hex(bus(i, 'forecast_data', 126))])
print('PASS CAPTURE: 512 samples; input and forecast match the reference')
print('Accepted input index:', accept)
print('Forecast-valid index:', valid)
print('Raw sample separation:', valid - accept)
print('Forecast word:', hex(actual_output))
print('Decoded CSV:', output)
