# Weather window → LCD (DE2)

One host command sends a 25-frame hourly window to the board. The FPGA computes the single +3 h forecast and the 16×2 LCD holds it.

This variant is developed from `versions/weather_v2/quartus/de2_jtag_speed`. It reuses the verified JTAG mailbox (`hardware/jtag/jtag_mailbox.v`), the ISSP node, the reset synchroniser and the parallel predictor (`weather_system_speed`, `wind_direction_cordic`) **unchanged**. After a JTAG reset, the mailbox treats frames 1–24 as history fill and frame 25 as the forecast request. A 25-frame window therefore produces exactly one forecast. The only new hardware is the LCD view.

**New to the board?** Follow the step-by-step teammate guide for Windows and Linux: [docs/operating_guides/WEATHER_LCD_DE2_GUIDE.md](../../../docs/operating_guides/WEATHER_LCD_DE2_GUIDE.md).

## Files

| Path | Purpose |
|---|---|
| `../quartus/de2_jtag_lcd/weather_lcd.qpf` | Quartus II 13.0 SP1 project (EP2C35F672C6) |
| `rtl/de2_weather_lcd.v` | Top level: existing mailbox and predictor, plus the latched LCD view |
| `rtl/weather_lcd_text.v` | Builds the two 16-character lines (Q8 → decimal, rounding as in the reference) |
| `rtl/lcd_hd44780.v` | Write-only HD44780 driver: 20 ms power-up, init, continuous refresh |
| `host/send_window.tcl` | **The one host command** (USB-Blaster/JTAG) |
| `host/lcd_reference.py` | Fixed-point golden model: makes window CSVs (`window`), prints the expected forecast and LCD text for any CSV (`expect`) |
| `host/windows/*.csv` | Three ready-made 2025 windows (the simulated ones), usable without the gitignored dataset |
| `tb/`, `build.sh` | Self-checking simulations (Icarus Verilog) |

## Use on the board

1. Open `versions/weather_v2/quartus/de2_jtag_lcd/weather_lcd.qpf` and compile, or use the existing `output_files/weather_lcd.sof`.
2. Program the board with the USB-Blaster: Tools → Programmer, or from the repository root:

   ```bash
   quartus_pgm -m jtag -c 1 -o 'p;versions/weather_v2/quartus/de2_jtag_lcd/output_files/weather_lcd.sof'
   ```

   The LCD shows `Weather +3h FPGA` / `Send 25 frames`.
3. Make a window. This takes the 25 hours ending at a UTC timestamp from the dataset:

   ```bash
   python3 versions/weather_v2/lcd/host/lcd_reference.py window --end "2025-03-24 05:00" --out window.csv
   ```

   Any CSV with a header and 25 rows `timestamp,T2M,PS,RH2M,WS10M,WD10M` (°C, kPa, %, m/s, degrees; oldest first) works. The script also prints the forecast and LCD text that the board should show.
4. Send it. This is the one command:

   ```bash
   quartus_stp -t versions/weather_v2/lcd/host/send_window.tcl window.csv
   ```

   The script resets the predictor history through JTAG, sends the 25 frames, checks for 25 accepted frames and exactly 1 forecast, and prints the forecast plus the text now on the LCD. While frames arrive, the LCD briefly shows `Receiving window` / `Frame nn of 25`.

The LCD keeps the forecast until the next window's result replaces it. A JTAG reset for the next window does not clear it. Only KEY0 returns the LCD to the idle screen.

## LCD format

```
T+37.0C P100.14      temperature °C, pressure kPa
H 28% W 2.5 D 65     humidity %, wind m/s, direction ° (clockwise from north)
```

Values are rounded from the Q8 outputs: tenths for temperature and wind, hundredths for pressure, whole numbers for humidity and degrees. Temperature and wind are clamped to ±99.9 on the display only. `D---` means an undefined direction (zero vector).

## Verification done

- `host/lcd_reference.py selfcheck` reproduces all 104 forecasts of the verified board replay (`hardware/jtag/vectors/weather.txt`).
- `./build.sh` runs three simulations:
  - **End to end** at 50 MHz: three real 2025 windows through the mailbox and predictor. The forecast word equals the golden model, and an HD44780 model rebuilds the screen from the LCD pins. Checks cover the idle screen, loading progress, each forecast, holding across the next JTAG reset, KEY0 back to idle, E-pulse width and busy times (808 bus writes).
  - **Formatter:** 309 edge and random cases against the Python text rules.
  - **Power-up:** the LCD starts correctly without any reset pulse.
- The host script's payload encoding and LCD text were cross-checked against the Python reference under Quartus's Tcl 8.5.
- Quartus II 13.0 SP1 compile (`../quartus/de2_jtag_lcd/build_compile.log`): successful, no critical warnings, all 15 pins on the DE2 locations. 7,284 LEs (22 %), 4,867 registers, 14 / 70 nine-bit multipliers (12 for the predictor, 2 for display scaling), 0 memory bits. Timing at 50 MHz: slow-model setup slack 4.451 ns (Fmax estimate 64.31 MHz), hold slack 0.391 ns slow / 0.215 ns fast. The 13 remaining warnings are benign:
  - `LCD_RW` tied low and `LCD_ON`/`LCD_BLON` tied high, by design.
  - Unconnected ports inside Altera's source-probe IP, also present in the original project.
  - Width truncations in BCD arithmetic and the column index, all intended.
  - Licence and jitter-analysis notices.
- Power-up: the LCD driver's registers have explicit power-up values, which Quartus implements as "power-up high". The 20 ms LCD power-on wait therefore runs straight after configuration, with no reset needed. `tb/tb_powerup.v` checks this: first E pulse at 20.0 ms.
- `send_window.tcl` rejects non-numeric values and values that do not fit 18-bit Q8 (for example pressure in Pa instead of kPa), instead of sending a wrapped value.

**Not yet done:** running it on the physical board. The first board run should match the "Expected LCD" printed by step 3.
