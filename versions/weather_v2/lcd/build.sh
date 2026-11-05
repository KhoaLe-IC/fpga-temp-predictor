#!/bin/bash
# Regenerate vectors and run the end-to-end simulation (Icarus Verilog).
set -e
cd "$(dirname "$0")"; R=../../..
mkdir -p build
python3 host/lcd_reference.py tb --out build/vectors.txt --end "2025-03-24 05:00" --end "2025-07-15 20:00" --end "2025-11-02 13:00"
iverilog -g2012 -s tb -o build/sim tb/tb.v tb/jtag_issp_sim.v rtl/*.v $R/hardware/jtag/jtag_mailbox.v \
 $R/hardware/speed_optimized/reset_sync.v ../rtl/weather_system_speed.v ../rtl/weather_predictor_speed.v \
 ../rtl/weather_ar_channel.v ../rtl/wind_direction_cordic.v
cd build && vvp -n sim
cd ..
python3 tb/make_format_cases.py build/format_cases.txt
iverilog -g2012 -s tb_format -o build/fmt tb/tb_format.v rtl/weather_lcd_text.v
cd build && vvp -n fmt
cd ..
iverilog -g2012 -s tb_powerup -o build/pwr tb/tb_powerup.v rtl/lcd_hd44780.v
cd build && vvp -n pwr
