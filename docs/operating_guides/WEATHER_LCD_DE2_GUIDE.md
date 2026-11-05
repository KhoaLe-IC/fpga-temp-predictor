# Running the weather LCD demo on the DE2

This guide is for a teammate who starts from a fresh clone on **Windows or Linux**. You send one 25-hour weather window from the PC over the USB-Blaster cable. The FPGA computes the +3 h forecast, and the board's 16×2 LCD keeps showing it.

```
PC (window.csv) ──USB-Blaster/JTAG──► DE2: predictor ──► LCD  T+37.0C P100.14
                                                              H 28% W 2.5 D 65
```

The design lives in `versions/weather_v2/lcd/` (RTL, host scripts, tests) and `versions/weather_v2/quartus/de2_jtag_lcd/` (Quartus project). The technical details are in [the variant README](../../versions/weather_v2/lcd/README.md).

> Status: every step below was checked on Linux with Quartus II 13.0 SP1, in simulation and with the Quartus tools. The design has **not yet been run on a physical board**, and the Windows commands have not been tried on a Windows PC. If something differs from this guide, note what you saw and tell the group.

## What you need

| Item | Notes |
|---|---|
| Terasic **DE2** board (chip **EP2C35F672C6**), its power adapter and USB cable | DE2-70 and DE2-115 use other chips, so this design will not load on them. |
| **Quartus II Web Edition 13.0 SP1** with Cyclone II support | Newer Quartus versions dropped Cyclone II. Downloads: [Windows](https://www.altera.com/downloads/fpga-development-tools/quartus-ii-web-edition-design-software-version-13-0sp1-windows), [Linux](https://www.altera.com/downloads/fpga-development-tools/quartus-ii-web-edition-design-software-version-13-0sp1-linux). ModelSim is not needed. |
| USB-Blaster driver | Ships with Quartus; see step 4. |
| Git | To clone the repository. |
| Python 3.9 or newer | Optional: only prints the expected result. Standard library only, nothing to `pip install`. |

Use **PowerShell** on Windows (not Command Prompt, Git Bash or WSL) and **Bash** on Linux. Run every command from the **repository root**, the folder that contains `hardware/`, `scripts/` and `versions/`. Commands shown once, in a plain block, work the same in both shells.

## 1 Get the repository

```
git clone https://github.com/KhoaLe-IC/fpga-temp-predictor.git
cd fpga-temp-predictor
```

Check that the LCD variant is there:

```
git log -1 --oneline
ls versions/weather_v2/lcd/host
```

You should see `send_window.tcl`, `lcd_reference.py` and a `windows/` folder. If `versions/weather_v2/lcd` is missing, your clone is older than the LCD variant: run `git pull`.

## 2 Put the Quartus tools on your PATH

The commands below only last for the current terminal window. Repeat them in every new window.

**Windows (PowerShell).** Replace the folder with your own install location. The default is `C:\altera\13.0sp1\quartus\bin64`. Use `bin` if your installation has no `bin64` folder.

```powershell
$env:Path = "C:\altera\13.0sp1\quartus\bin64;$env:Path"
Get-Command quartus_sh, quartus_pgm, quartus_stp, jtagconfig
py -3 --version
```

**Linux (Bash).** Again, replace the folder with your own install location.

```bash
export PATH="$HOME/altera/13.0sp1/quartus/bin:$PATH"
command -v quartus_sh quartus_pgm quartus_stp jtagconfig
python3 --version
```

Then, in either shell:

```
quartus_sh --version
```

It must report `Version 13.0.1 Build 232 ... SP1`.

## 3 Build the FPGA configuration (.sof)

Git ignores Quartus output, so a fresh clone has **no `weather_lcd.sof`**. Building it takes about 2 minutes:

```
quartus_sh --flow compile versions/weather_v2/quartus/de2_jtag_lcd/weather_lcd
```

Wait for `Quartus II Full Compilation was successful. 0 errors`. Warnings are expected (about 17). They are explained in the variant README.

The result is `versions/weather_v2/quartus/de2_jtag_lcd/output_files/weather_lcd.sof`.

Prefer the GUI? Open `versions/weather_v2/quartus/de2_jtag_lcd/weather_lcd.qpf` in Quartus, then choose Processing → Start Compilation.

If a teammate sends you their `.sof` instead, check that it is the verified build:

- **Windows:** `Get-FileHash -Algorithm SHA256 path\to\weather_lcd.sof`
- **Linux:** `sha256sum path/to/weather_lcd.sof`

The verified build's hash is `b31d60b295794e64304e767c69c48c3a948865b706c2ae812a8f1a1bb811ed15`. Your own compile may give a different hash, and that is fine.

## 4 Connect the board

1. With the power off, set the **RUN/PROG** switch on the left edge of the DE2 to **RUN**.
2. Plug in the power adapter. Connect the USB cable to the **USB-Blaster** port, the one next to the power jack (not the USB host/device ports).
3. Turn the board on, then run:

   ```
   jtagconfig
   ```

   Expected output (your cable number or port may differ):

   ```
   1) USB-Blaster [1-1]
     020B40DD   EP2C35 (IR=10)
   ```

If no cable shows up, or the chip line is missing:

- **Windows:** Device Manager shows an unknown "USB-Blaster" device. Right-click it, choose Update driver → Browse my computer, and point it at `C:\altera\13.0sp1\quartus\drivers\usb-blaster` (adjust to your install). Then run `jtagconfig` again.
- **Linux:** normal users need permission to access the cable. Create a udev rule once, then unplug and replug the cable:

  ```bash
  echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6001", MODE="0666"' | sudo tee /etc/udev/rules.d/51-usbblaster.rules
  sudo udevadm control --reload-rules && sudo udevadm trigger
  killall jtagd 2>/dev/null; jtagconfig
  ```

  `lsusb` should list `09fb:6001 Altera Blaster`.

Only continue when `jtagconfig` shows the **EP2C35** line, not just the cable name.

## 5 Program the FPGA

```
quartus_pgm -m jtag -c 1 -o "p;versions/weather_v2/quartus/de2_jtag_lcd/output_files/weather_lcd.sof"
```

If `jtagconfig` listed a different number for your cable, use it instead of `1`. Wait for `Configuration succeeded`.

The GUI route is Tools → Programmer: Hardware Setup → USB-Blaster, Mode JTAG, Add File → `weather_lcd.sof`, tick Program/Configure, then Start.

The LCD should now show:

```
Weather +3h FPGA
Send 25 frames
```

The configuration lives in on-chip RAM, so it is lost when the board is powered off. Repeat this step after every power-up.

## 6 Send a window and read the forecast

Three ready-made windows from the 2025 dataset are in `versions/weather_v2/lcd/host/windows/`:

| File | Window ends (UTC) | LCD should show |
|---|---|---|
| `2025-03-24_0500.csv` | 2025-03-24 05:00 | `T+37.0C P100.14 ` / `H 28% W 2.5 D 65` |
| `2025-07-15_2000.csv` | 2025-07-15 20:00 | `T+25.9C P100.23 ` / `H 94% W 2.5 D230` |
| `2025-11-02_1300.csv` | 2025-11-02 13:00 | `T+24.5C P100.47 ` / `H 96% W 2.1 D303` |

1. (Optional) Print what the board *should* show. This does not use the board.

   - **Windows:** `py -3 versions/weather_v2/lcd/host/lcd_reference.py expect versions/weather_v2/lcd/host/windows/2025-03-24_0500.csv`
   - **Linux:** `python3 versions/weather_v2/lcd/host/lcd_reference.py expect versions/weather_v2/lcd/host/windows/2025-03-24_0500.csv`

2. Send it to the board. This is the one command:

   ```
   quartus_stp -t versions/weather_v2/lcd/host/send_window.tcl versions/weather_v2/lcd/host/windows/2025-03-24_0500.csv
   ```

   It takes a few seconds. While the frames arrive, the LCD briefly shows `Receiving window` / `Frame nn of 25`. Expected end of the output:

   ```
   Window: 2025-03-23 05:00:00+00:00 .. 2025-03-24 05:00:00+00:00  (forecast for +3 h)
     temperature C      36.9883   (raw 9469)
     pressure kPa      100.1406   (raw 25636)
     humidity %         28.2344   (raw 7228)
     wind speed m/s      2.4727   (raw 633)
     direction cos       0.1289   (raw 33)
     direction sin       0.2734   (raw 70)
     direction deg      64.7578   (raw 16578, defined=1)
   LCD now holds:
     |T+37.0C P100.14 |
     |H 28% W 2.5 D 65|
   ```

3. Check that the **physical LCD** matches the `LCD now holds` lines and the table above. This is the real test. The script reads the forecast back from the FPGA, so matching numbers in the terminal prove the predictor works, and a matching LCD proves the display path works.

Send another window with the same command and a different file. The new forecast replaces the old one. Press **KEY0** (the rightmost push button) to return the LCD to the idle screen.

### Reading the LCD

```
T+37.0C P100.14      temperature °C, pressure kPa
H 28% W 2.5 D 65     humidity %, wind speed m/s, wind direction ° (clockwise from north)
```

- All values are the forecast for **3 hours after the last row** of the window.
- `D---` means the predicted wind vector is zero, so it has no direction.

## 7 Use your own window

Any CSV with this header and **exactly 25 data rows, oldest first, one per hour** works:

```
timestamp,T2M,PS,RH2M,WS10M,WD10M
2025-03-23 05:00:00+00:00,37.48,100.47,27.13,0.72,290.5
...
```

| Column | Meaning | Unit |
|---|---|---|
| `timestamp` | Label only; the board does not use it | any text without commas |
| `T2M` | Air temperature at 2 m | °C |
| `PS` | Surface pressure | **kPa** (about 100, not 100000 Pa) |
| `RH2M` | Relative humidity | % |
| `WS10M` | Wind speed at 10 m | m/s |
| `WD10M` | Wind direction, where the wind comes from | degrees, 0 = north |

The script stops with an error if a row is malformed, a value is not a number, or a value cannot fit the 18-bit format, for example pressure in Pa. Nothing is sent in that case. Run `lcd_reference.py expect your.csv` first to see the expected LCD text.

If you have the full dataset, `versions/weather_v2/data/weather.csv`, the reference script can cut a window for any hour. That file is not in Git; ask for a copy.

- **Windows:** `py -3 versions/weather_v2/lcd/host/lcd_reference.py window --end "2025-03-24 05:00" --out my_window.csv`
- **Linux:** `python3 versions/weather_v2/lcd/host/lcd_reference.py window --end "2025-03-24 05:00" --out my_window.csv`

## 8 Troubleshooting

| Symptom | What to do |
|---|---|
| `quartus_sh` / `quartus_stp` not found | Step 2 again in this terminal window. On Windows, check whether your install uses `bin64` or `bin`. |
| `jtagconfig` shows no cable | Driver (Windows) or udev rule (Linux), step 4. Try another USB port and cable. |
| Cable shown but no `EP2C35` line | Board is off, or RUN/PROG is not on RUN. |
| `FCST source/probe node not found. Program weather_lcd.sof first.` | The FPGA holds another design or was power-cycled. Step 5. |
| `JTAG design identity mismatch` | A different weather design is loaded (for example `weather_jtag.sof`). Program `weather_lcd.sof`. |
| `Expected exactly one USB-Blaster` or `Select the EP2C35 device explicitly` | More than one cable or device is visible. Add the names `jtagconfig` printed: `quartus_stp -t ...send_window.tcl window.csv "USB-Blaster [1-1]" "@1: EP2C35 (0x020B40DD)"` |
| `JTAG timeout waiting for acknowledgement` | Make sure KEY0 is not held down, then re-program (step 5) and retry. |
| `Window must have exactly 25 frames` / `Not a number` / `does not fit signed 18-bit Q8` | Fix the CSV (step 7). Check the units, especially kPa. |
| Script succeeds but the LCD is blank or shows black boxes | Press KEY0 and wait a second, then re-program. If the terminal values are right, the predictor works and only the display path needs checking. Report it with a photo. |
| Script succeeds but the LCD text differs from `LCD now holds` | Take a photo and save the full terminal output. This is a display bug worth reporting. |

The quartus_stp command also prints an `Info:` banner. Only the lines at the end and any `FAIL:` line matter. A `FAIL:` line always ends the run with an error status.
