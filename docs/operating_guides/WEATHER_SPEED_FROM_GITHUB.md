# Reproduce the weather speed design from GitHub

Procedure WS-DE2-02 · Revision 1 · 2 November 2026

This guide starts with an empty folder on your own computer. It explains how to clone the repository, obtain the supplied FPGA configurations, run the weather predictor on an original DE2 board, and capture a live waveform. Commands do not depend on the project author's username or installation directory.

Repository: <https://github.com/KhoaLe-IC/fpga-temp-predictor>

The hardware and recorded results were originally verified with Quartus II Web Edition 13.0 SP1 on Linux. Windows PowerShell instructions are provided for the same files and Quartus commands; a Windows board run has not been performed as part of this guide's preparation.

## Before starting

You need an **original Terasic DE2 with EP2C35F672C6**, its power supply, a USB-Blaster connection, and a Windows or Linux computer that can run Quartus II 13.0 SP1. A DE2-70 or DE2-115 is a different target. No serial adapter or weather sensor is required.

Install these tools:

| Tool | Purpose |
| --- | --- |
| Git | Download the repository and record its revision |
| Quartus II Web Edition 13.0 SP1 | Program the Cyclone II and operate its JTAG interfaces |
| Cyclone II device support and USB-Blaster driver | Recognize and access the target |
| Python 3.9 or later | Check saved CSV and SignalTap data using the standard library |
| `tar` | Extract the programming files from the supplied archive |

Obtain Quartus from the official [Windows download page](https://www.altera.com/downloads/fpga-development-tools/quartus-ii-web-edition-design-software-version-13-0sp1-windows) or [Linux download page](https://www.altera.com/downloads/fpga-development-tools/quartus-ii-web-edition-design-software-version-13-0sp1-linux). Install the software and matching Cyclone II support. The validated tool version is 13.0.1 Build 232. ModelSim is unnecessary for this physical replay.

Install [Git](https://git-scm.com/downloads) and [Python](https://www.python.org/downloads/) if they are missing. Python packages from `requirements.txt` are **not needed** for this procedure: training and vector generation have already been completed.

On Windows, use native **PowerShell**, not Command Prompt, Git Bash, or a WSL terminal for the Windows blocks. On Linux, use **Bash**. Do not combine commands from the two setup sections. A macOS host needs a suitable Windows/Linux environment with working USB access; these instructions do not establish native macOS support or virtual-machine USB operation.

The usual route is Sections 1 through 8. Section 9 covers rebuilding from source. Troubleshooting and the two small verification utilities follow the main procedure.

## 1 Clone the repository

1. Open PowerShell on Windows or Bash on Linux. Start in a writable location where you want the project directory to be created. Avoid a synchronized network folder for the rehearsal.
2. Check Git:

   ```text
   git --version
   ```

3. Clone using HTTPS, then enter the downloaded directory. These two commands are the same in PowerShell and Bash:

   ```text
   git clone https://github.com/KhoaLe-IC/fpga-temp-predictor.git
   cd fpga-temp-predictor
   ```

   This URL does not require the author's SSH key. A public clone does not require access to the author's computer.

4. Check the repository revision and its root folder:

   ```text
   git rev-parse HEAD
   git rev-parse --show-toplevel
   ```

   The second command prints **your** checkout location. The repository inspected when preparing this guide was `a476b32e42db90a7c68c94c941427b44cd9a65a2`. Later commits can include this guide without changing the supplied model or FPGA files.

5. Keep this terminal open. All later commands start from the repository root unless a step explicitly changes directory.

If you downloaded GitHub's ZIP instead, extract it first, open a terminal inside the extracted top-level folder, and confirm that it contains `hardware`, `scripts`, and `versions`. The `git rev-parse` commands will not work in a ZIP copy; record the downloaded branch or commit separately. The remaining file-based operations can still be followed.

## 2 Set up the tools on your computer

Follow either Section 2.1 or Section 2.2. The examples derive the checkout path from the terminal's current directory. The only installation location you may need to provide is **your own Quartus directory**.

### 2.1 Windows PowerShell

1. Confirm that you are still inside the cloned directory:

   ```powershell
   if (-not (Test-Path 'scripts/replay_jtag.tcl')) {
       throw 'Open PowerShell inside the cloned fpga-temp-predictor folder.'
   }
   $ProjectRoot = (Get-Location).Path
   ```

2. Locate Quartus. If `quartus_sh.exe` is already on PATH, the following block uses it. Otherwise, it prompts for the full path to that executable:

   ```powershell
   $QuartusCommand = Get-Command quartus_sh.exe -ErrorAction SilentlyContinue
   if ($null -eq $QuartusCommand) {
       $QuartusExe = Read-Host 'Paste the full path to quartus_sh.exe without quotation marks'
       if (-not (Test-Path -LiteralPath $QuartusExe -PathType Leaf)) {
           throw 'That executable does not exist. Locate quartus_sh.exe in your Quartus installation.'
       }
       $QuartusBin = Split-Path -LiteralPath $QuartusExe
   } else {
       $QuartusBin = Split-Path -LiteralPath $QuartusCommand.Source
   }
   $env:Path = "$QuartusBin;$env:Path"
   ```

   To find the executable, open File Explorer and browse to the installed Quartus folder, then its `bin` or `bin64` directory. Search there for `quartus_sh.exe`. Copy that file's full path. For example, an installation can be under `C:\altera\13.0sp1`; its actual location is chosen during installation. Do not enter that example unless it exists on your computer.

3. Check the commands and version:

   ```powershell
   Get-Command quartus_sh, quartus_pgm, quartus_stp, jtagconfig, tar -ErrorAction Stop
   quartus_sh --version
   py -3 --version
   ```

   Confirm Quartus 13.0 SP1 and Python 3.9 or later. If the Python launcher `py` is missing, repair the Python installation before using the `py -3` commands below.

4. Create a new results directory and record its location:

   ```powershell
   $RunDir = Join-Path $ProjectRoot ('build/reproduction/weather_speed_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
   New-Item -ItemType Directory -Path $RunDir -Force | Out-Null
   Write-Output $RunDir
   git rev-parse HEAD | Set-Content (Join-Path $RunDir 'commit.txt')
   quartus_sh --version 2>&1 | Out-File (Join-Path $RunDir 'quartus_version.txt')
   ```

Proceed to Section 3. These variables belong to this PowerShell session. Opening another window does not copy them automatically.

### 2.2 Linux Bash

1. Confirm that you are still inside the cloned directory:

   ```bash
   test -f scripts/replay_jtag.tcl || {
     printf '%s\n' 'Open Bash inside the cloned fpga-temp-predictor folder.'
     exit 1
   }
   ProjectRoot="$PWD"
   ```

2. Locate Quartus. The block uses an existing PATH entry or asks for the directory containing `quartus_sh`:

   ```bash
   if command -v quartus_sh >/dev/null 2>&1; then
     QuartusBin="$(dirname "$(command -v quartus_sh)")"
   else
     read -r -p 'Paste the full directory containing quartus_sh: ' QuartusBin
   fi
   test -x "$QuartusBin/quartus_sh" || {
     printf '%s\n' 'quartus_sh was not found in that directory.'
     exit 1
   }
   export PATH="$QuartusBin:$PATH"
   ```

   Find the installation in your file manager if necessary. Paste its absolute `quartus/bin` directory, without quotation marks. Do not copy a path containing another person's username.

3. Check the commands and version:

   ```bash
   command -v quartus_sh quartus_pgm quartus_stp jtagconfig tar python3
   quartus_sh --version
   python3 --version
   ```

   Confirm that all commands exist, Quartus is 13.0 SP1, and Python is 3.9 or later. Resolve startup or missing-library errors before connecting the board.

4. Create a new results directory and record its location:

   ```bash
   RunDir="$ProjectRoot/build/reproduction/weather_speed_$(date +%Y%m%d_%H%M%S)"
   mkdir -p "$RunDir"
   printf '%s\n' "$RunDir"
   git rev-parse HEAD > "$RunDir/commit.txt"
   quartus_sh --version > "$RunDir/quartus_version.txt" 2>&1
   set -o pipefail
   ```

Proceed to Section 3. Use the same terminal so that `ProjectRoot` and `RunDir` remain available.

## 3 Extract the supplied programming files

A fresh clone normally has **no standalone SOF files**. The repository ignores generated programming outputs, but it tracks an archive containing the validated configurations. This procedure extracts that archive into the new results directory and leaves the source checkout unchanged.

### 3.1 Extract on Windows

Run in the PowerShell session prepared above:

```powershell
$PackageDir = Join-Path $RunDir 'packaged'
New-Item -ItemType Directory -Path $PackageDir -Force | Out-Null
tar -xzf docs/reports/defense_evidence_2026-10-28.tar.gz -C "$PackageDir"
if ($LASTEXITCODE -ne 0) { throw 'Archive extraction failed.' }
$OrdinarySof = Join-Path $PackageDir 'versions/weather_v2/quartus/de2_jtag_speed/output_files/weather_jtag.sof'
$CaptureSof = Join-Path $PackageDir 'hardware/quartus/signaltap/weather_speed/output_files/capture.sof'
$CaptureSetup = Join-Path $PackageDir 'hardware/quartus/signaltap/weather_speed/capture.stp'
Get-Item $OrdinarySof, $CaptureSof, $CaptureSetup, 'hardware/jtag/vectors/weather.txt' -ErrorAction Stop
Get-FileHash -Algorithm SHA256 $OrdinarySof, $CaptureSof
```

### 3.2 Extract on Linux

Run in the Bash session prepared above:

```bash
PackageDir="$RunDir/packaged"
mkdir -p "$PackageDir"
tar -xzf docs/reports/defense_evidence_2026-10-28.tar.gz -C "$PackageDir"
OrdinarySof="$PackageDir/versions/weather_v2/quartus/de2_jtag_speed/output_files/weather_jtag.sof"
CaptureSof="$PackageDir/hardware/quartus/signaltap/weather_speed/output_files/capture.sof"
CaptureSetup="$PackageDir/hardware/quartus/signaltap/weather_speed/capture.stp"
ls -l "$OrdinarySof" "$CaptureSof" "$CaptureSetup" hardware/jtag/vectors/weather.txt
sha256sum "$OrdinarySof" "$CaptureSof"
```

### 3.3 Check the extracted configurations

The archived files inspected for this guide have these SHA-256 hashes:

| Configuration | SHA-256 |
| --- | --- |
| Ordinary weather speed SOF | `6983677cd3563baaa6f7b06cdc5ddacb70f3843e729ea46484f09897e7752f96` |
| Instrumented weather speed SOF | `aec8714829982c4a139070690d5997693d20b050e928850e031f523202880027` |

The ordinary SOF is used for checked replay. The instrumented SOF also includes SignalTap capture circuitry. Both implement the speed-oriented weather system.

The archive has older report and status files as well. Their presence is not evidence of a new run on your board. New evidence will be saved beside `packaged/` in your current results directory.

If the archive is absent, check that the clone/download completed and that you are in the correct directory. Section 9 describes compiling from source. Do not substitute a SOF from `de2_jtag_resource`, a UART project, or a core-only project merely because its filename looks similar.

## 4 Connect and program the DE2

### 4.1 Establish the JTAG connection

1. With board power off, set the original DE2's RUN/PROG switch to **RUN**.
2. Connect its external power supply and USB-Blaster programming connection to the computer.
3. Switch the board on and release KEY0, which is the application reset button.
4. In the prepared terminal, run:

   ```text
   jtagconfig
   ```

5. Confirm that an EP2C35 device with ID `020B40DD` appears below USB-Blaster. For example:

   ```text
   1) USB-Blaster [1-1]
     020B40DD   EP2C35 (IR=10)
   ```

   The cable address can differ. Record its cable number; the programming command below assumes **1**.

If Windows detects an unknown USB device, install the matching USB-Blaster driver through Device Manager using the driver directory in your Quartus installation. Consult the [vendor driver instructions](https://www.altera.com/developers/software/cables-and-adapter-drivers-installation-guide). On Linux, follow the vendor's device-permission instructions. Continue only when `jtagconfig` sees the FPGA, not merely the cable.

### 4.2 Program the ordinary design

This command works in either prepared shell because both define `OrdinarySof`:

```text
quartus_pgm -m jtag -c 1 -o "p;$OrdinarySof"
```

Replace `1` with the actual cable number. Wait for successful configuration, including the message `Configuration succeeded` or a successful Programmer completion.

For a GUI demonstration, open Quartus > Tools > Programmer, select the USB-Blaster under Hardware Setup, choose JTAG mode, add the file identified by `OrdinarySof`, enable Program/Configure, and select Start. To display that path in either prepared shell, enter:

```text
echo $OrdinarySof
```

Save a screenshot showing the selected device, file, and successful completion. Programming loads SRAM configuration; it must be repeated after the board is powered off.

## 5 Run and check the weather replay

The supplied replay resets the core through JTAG, sends 128 recorded input frames, and checks 104 forecasts after a 24-frame warm-up. It uses `hardware/jtag/vectors/weather.txt`, already present in the clone.

Close manual source/probe writers before replay. They must not change the mailbox while the script is sending data.

### 5.1 Replay on Windows

```powershell
$env:FPGA_JTAG_CSV = Join-Path $RunDir 'ordinary_replay.csv'
quartus_stp -t scripts/replay_jtag.tcl weather_speed 2>&1 |
    Tee-Object -FilePath (Join-Path $RunDir 'ordinary_replay.log')
if ($LASTEXITCODE -ne 0) { throw 'Replay failed. Read ordinary_replay.log.' }
```

### 5.2 Replay on Linux

```bash
FPGA_JTAG_CSV="$RunDir/ordinary_replay.csv" \
  quartus_stp -t scripts/replay_jtag.tcl weather_speed \
  2>&1 | tee "$RunDir/ordinary_replay.log"
```

### 5.3 Confirm completion

The output must identify `Variant: weather_speed` and source/probe node `{0 128 256 FCST}`, then finish with:

```text
PASS PHYSICAL JTAG weather_speed: inputs=128 forecasts=104; CSV=...
```

The CSV location should be inside your new run directory. Without the output override above, the replay replaces the repository's older `docs/reports/physical_jtag_weather_speed.csv`.

Each forecast line contains temperature in °C, pressure in kPa, relative humidity in %, wind speed in m/s, direction cosine, direction sine, and angle in degrees, in that order. The first result is `sample=24`, meaning the 25th accepted frame because the index starts at zero.

With unchanged supplied vectors, the retained first result is:

```text
sample=24 forecast=26.445312 100.531250 69.644531 3.285156 0.902344 0.085938 5.437500 match=True
```

The FPGA computes the prediction; the computer supplies observations and compares the returned result with the reference. The replay demonstrates hardware agreement. Historical forecasting accuracy against later observations is a separate evaluation.

### 5.4 Verify the saved CSV

Create `verify_weather_run.py` in your run directory by copying the code in Appendix B into a text editor. Save it as a plain-text Python file. On Windows, select All files when saving so the filename does not become `verify_weather_run.py.txt`.

On Windows:

```powershell
py -3 "$RunDir/verify_weather_run.py" "$RunDir/ordinary_replay.csv"
if ($LASTEXITCODE -ne 0) { throw 'CSV validation failed.' }
```

On Linux:

```bash
python3 "$RunDir/verify_weather_run.py" "$RunDir/ordinary_replay.csv"
```

Expected result: `PASS CSV: 128 inputs, 24 warm-up rows, 104 matching forecasts`.

## 6 Capture a live waveform

Complete the ordinary replay before changing configuration. Save the logs already produced.

### 6.1 Load the capture configuration

1. In either prepared shell, program the instrumented SOF:

   ```text
   quartus_pgm -m jtag -c 1 -o "p;$CaptureSof"
   ```

2. Copy the matching STP into the run directory.

   Windows:

   ```powershell
   Copy-Item -LiteralPath $CaptureSetup -Destination (Join-Path $RunDir 'weather_speed_live.stp')
   ```

   Linux:

   ```bash
   cp "$CaptureSetup" "$RunDir/weather_speed_live.stp"
   ```

3. Open Quartus > Tools > SignalTap II Logic Analyzer. Open this copied `weather_speed_live.stp`, not a historical captured file.
4. In JTAG Chain Configuration, select your connected USB-Blaster and EP2C35. The archived setup contains the original computer's cable name, so this selection must be checked on every new computer.
5. Browse to the file identified by `CaptureSof` if SignalTap's SOF field has a stale relative path.
6. Confirm instance `auto_signaltap_0`, clock `CLOCK_50`, acquisition depth 512, center trigger position, and a rising-edge trigger on `jtag_mailbox:mailbox|forecast_valid`. Save the copied STP and close the SignalTap window.

Changing the cable selection does not change the prediction model. Changing probe or trigger configuration may require rebuilding the instrumented design. Keep the supplied acquisition configuration for this reproduction.

### 6.2 Create the capture command file

In a text editor, save the following as `acquire_weather_speed.tcl` inside your run directory. This file works with either operating system and avoids writing to the original evidence directory.

```tcl
package require ::quartus::stp
set args $quartus(args)
if {[llength $args] != 1} {
    error "Supply the full path to weather_speed_live.stp"
}
set capture_file [file normalize [lindex $args 0]]
open_session -name $capture_file
puts "CAPTURE ARMED: run weather_speed replay in the other terminal"
flush stdout
run -instance auto_signaltap_0 \
    -signal_set signal_set_1 \
    -trigger trigger_1 \
    -data_log live_capture \
    -timeout 120
close_session
puts "CAPTURE SAVED: $capture_file"
```

On Windows, confirm that the file is named `.tcl`, not `.tcl.txt`.

### 6.3 Prepare a second terminal

1. Open the **same shell type** as the first terminal.
2. Open a terminal in the same clone folder, or use `cd` to enter it. A simple option on Windows is File Explorer > the clone folder > Open in Terminal. On Linux, use the file manager's Open Terminal Here action if available.
3. Copy the actual `RunDir` and `QuartusBin` values from the first terminal. Both shells display them with:

   ```text
   echo $RunDir
   echo $QuartusBin
   ```

4. Set those same values in the second terminal. Replace the prompts below with the paths just printed; no username is prescribed.

   Windows:

   ```powershell
   $RunDir = Read-Host 'Paste the existing run directory without quotation marks'
   $QuartusBin = Read-Host 'Paste the Quartus executable directory without quotation marks'
   $env:Path = "$QuartusBin;$env:Path"
   if (-not (Test-Path 'scripts/replay_jtag.tcl')) { throw 'Enter the clone root first.' }
   ```

   Linux:

   ```bash
   read -r -p 'Paste the existing run directory: ' RunDir
   read -r -p 'Paste the Quartus executable directory: ' QuartusBin
   export PATH="$QuartusBin:$PATH"
   test -f scripts/replay_jtag.tcl || exit 1
   set -o pipefail
   ```

The first terminal will acquire the waveform. The second will provide stimulus. They must use the same FPGA and results directory.

### 6.4 Acquire and replay

1. In the **first terminal**, run this common command:

   ```text
   quartus_stp -t "$RunDir/acquire_weather_speed.tcl" "$RunDir/weather_speed_live.stp"
   ```

2. Wait for `CAPTURE ARMED` and SignalTap's pre-trigger state, described as `PRE` in the retained log. The command blocks while acquisition waits.
3. In the **second terminal**, run the instrumented replay.

   Windows:

   ```powershell
   $env:FPGA_JTAG_CSV = Join-Path $RunDir 'capture_replay.csv'
   quartus_stp -t scripts/replay_jtag.tcl weather_speed 2>&1 |
       Tee-Object -FilePath (Join-Path $RunDir 'capture_replay.log')
   if ($LASTEXITCODE -ne 0) { throw 'Instrumented replay failed.' }
   ```

   Linux:

   ```bash
   FPGA_JTAG_CSV="$RunDir/capture_replay.csv" \
     quartus_stp -t scripts/replay_jtag.tcl weather_speed \
     2>&1 | tee "$RunDir/capture_replay.log"
   ```

4. Confirm the replay's 128-input and 104-forecast PASS line.
5. Return to the first terminal and confirm `CAPTURE SAVED`. SignalTap should have reached `DONE`.
6. Run the verifier against both new records from the clone root.

   Windows:

   ```powershell
   py -3 "$RunDir/verify_weather_run.py" "$RunDir/capture_replay.csv" --stp "$RunDir/weather_speed_live.stp" --vectors hardware/jtag/vectors/weather.txt
   if ($LASTEXITCODE -ne 0) { throw 'Capture validation failed.' }
   ```

   Linux:

   ```bash
   python3 "$RunDir/verify_weather_run.py" "$RunDir/capture_replay.csv" \
     --stp "$RunDir/weather_speed_live.stp" \
     --vectors hardware/jtag/vectors/weather.txt
   ```

Expected results include both `PASS CSV` and `PASS CAPTURE`. The original capture accepts the frame at index 215 and shows forecast-valid at index 256, giving a raw separation of 41 samples. The documented post-edge RTL latency is 40 cycles; the acquisition samples before the register updates used by the RTL scoreboard's observation convention.

If capture times out, leave the failed records intact. Recheck the loaded SOF, matching STP, selected device, and trigger. Repeat Section 6.4 with acquisition armed before replay.

## 7 Display the result in Quartus

1. After both terminal processes finish, open `weather_speed_live.stp` in SignalTap.
2. Select the completed live data log and display the acquired waveform.
3. Locate `core_rst_n`, `sample_valid`, `sample_ready`, and `forecast_valid`. Show acceptance where valid and ready are both high, then the valid forecast.
4. Save a screenshot with the signal names, scale, and transaction visible. The saved file must belong to this run directory.
5. Optional: close the STP, then group its captured bits for easier reading.

   Windows:

   ```powershell
   py -3 scripts/format_signaltap.py "$RunDir/weather_speed_live.stp"
   ```

   Linux:

   ```bash
   python3 scripts/format_signaltap.py "$RunDir/weather_speed_live.stp"
   ```

6. Reopen the STP and save a second screenshot of the grouped weather buses. The formatter requires completed acquisition data and changes presentation, not the recorded bits.

Signed scalar and component outputs use eight fractional bits: decode the signed integer, then divide by 256. The direction-angle field is unsigned Q8 degrees. Values during cycles with `forecast_valid = 0` are not additional predictions.

The last forecast is also readable in Tools > In-System Sources and Probes Editor at instance FCST. Read it only after replay finishes; do not write source data while a replay is active. The result does not appear on the DE2's LEDs, seven-segment displays, or LCD in this implementation.

## 8 Save the reproduction record

Keep the following in your new run directory:

- `commit.txt` and `quartus_version.txt`.
- `ordinary_replay.log` and `ordinary_replay.csv`.
- `capture_replay.log` and `capture_replay.csv`.
- `weather_speed_live.stp` with acquired data.
- Programmer and waveform screenshots from the current run.
- The extracted ordinary and instrumented SOFs, or a record of their hashes.

Save the verifier output to a text file if required. In PowerShell, append `| Tee-Object -FilePath "$RunDir/validation.txt"` to a verifier command. In Bash, append `| tee "$RunDir/validation.txt"`. Keep the original pass/fail status in mind when using pipelines.

Copy the complete folder to another storage location. The board may be switched off once acquisition and saving have finished. Reload a SOF for the next live run; power cycling clears the FPGA's volatile configuration.

`build/` is ignored by Git. Copying the run folder preserves evidence; a normal `git push` does not publish those generated results automatically.

## 9 Rebuild from the cloned source

This route regenerates FPGA configurations. It does not require a training dataset, internet access after installation, or Python packages. The selected weather coefficients are already included in the RTL.

### 9.1 Compile the ordinary project

1. In Quartus, select File > Open Project and browse **inside your clone** to:

   ```text
   versions/weather_v2/quartus/de2_jtag_speed/weather_jtag.qpf
   ```

2. Confirm EP2C35F672C6, top-level entity `de2_weather_jtag`, revision `weather_jtag`, and parameter `SHARED = 0`.
3. Confirm `CLOCK_50 = PIN_N2`, `KEY0_N = PIN_G26`, and a 20 ns application clock constraint.
4. Select Processing > Start Compilation. Wait for successful completion and review errors or critical warnings.
5. Use that project's generated `output_files/weather_jtag.sof` in place of the extracted ordinary file.

Terminal alternative, beginning at the clone root:

```text
cd versions/weather_v2/quartus/de2_jtag_speed
quartus_sh --flow compile weather_jtag
cd ../../../..
```

After this sequence the terminal is back at the clone root. Set the programming-file variable to the new output.

Windows:

```powershell
$OrdinarySof = Join-Path $ProjectRoot 'versions/weather_v2/quartus/de2_jtag_speed/output_files/weather_jtag.sof'
```

Linux:

```bash
OrdinarySof="$ProjectRoot/versions/weather_v2/quartus/de2_jtag_speed/output_files/weather_jtag.sof"
```

### 9.2 Compile the instrumented project

1. Open `hardware/quartus/signaltap/weather_speed/capture.qpf` inside your clone.
2. Confirm revision `capture` and the enabled `capture.stp` file.
3. Compile. Review the map report for successfully connected SignalTap nodes. Investigate disconnected-node warnings, including Critical Warning 35025.
4. Use the generated `output_files/capture.sof` **with this source project's `capture.stp`**. Do not mix the new SOF with an unrelated archived acquisition setup.

Terminal alternative from the clone root:

```text
cd hardware/quartus/signaltap/weather_speed
quartus_sh --flow compile capture
cd ../../../..
```

Update the two variables, then repeat Section 6.

Windows:

```powershell
$CaptureSof = Join-Path $ProjectRoot 'hardware/quartus/signaltap/weather_speed/output_files/capture.sof'
$CaptureSetup = Join-Path $ProjectRoot 'hardware/quartus/signaltap/weather_speed/capture.stp'
```

Linux:

```bash
CaptureSof="$ProjectRoot/hardware/quartus/signaltap/weather_speed/output_files/capture.sof"
CaptureSetup="$ProjectRoot/hardware/quartus/signaltap/weather_speed/capture.stp"
```

All source and clock-file references used by these two projects were checked against Git-tracked files. Their paths are relative to the project files, so moving the whole clone does not require editing the author's original home directory.

### 9.3 Inspect the implementation results

Use the ordinary project's Compilation Report for the resource comparison. The retained ordinary JTAG build reports:

| Item | Retained result |
| --- | --- |
| Logic elements | 6,253 |
| Registers | 4,571 |
| Memory bits | 0 |
| Embedded multiplier 9-bit elements | 12 |
| CLOCK_50 slow-model Fmax | 79.74 MHz |
| Operating clock used for physical replay | 50 MHz |

Fmax is a timing-tool estimate; the board replay does not measure the physical maximum clock frequency. The SignalTap build includes extra capture circuitry, so its resource counts differ. New fitted results may vary with source, compiler settings, tool version, or fitting choices; retain the actual reports from the rebuild.

## 10 Troubleshooting

| Symptom | Action |
| --- | --- |
| `git` is not recognized | Install Git, open a new terminal, and repeat the version check. |
| `quartus_sh` is not recognized | Repeat the appropriate tool-location section. Use the directory containing the executable on this computer. |
| Missing SOF immediately after cloning | Follow Section 3. Generated SOFs are packaged in the tracked archive. |
| Windows rejects a pasted `export` command | Use the PowerShell blocks. Bash `export` syntax is not PowerShell syntax. |
| USB-Blaster appears but EP2C35 does not | Check board power, RUN mode, and the USB-Blaster connection. |
| No hardware appears in `jtagconfig` | Check driver/device permissions, cable connection, and selected Quartus installation. |
| FCST is not found | Program a weather JTAG configuration, not a core-only or UART SOF. |
| Identity mismatch | Confirm weather speed rather than weather resource; use replay argument `weather_speed`. |
| Timeout waiting for acknowledgement | Release KEY0, verify clock/reset pin assignments, and close competing source writers. |
| SignalTap configuration mismatch | Use SOF and STP from the same instrumented build. |
| Capture waits forever | Arm before replay; check forecast-valid trigger, acquisition clock, selected device, and instrumented SOF. |
| Data checker fails | Preserve the logs and retry with unchanged matching vectors/model/SOF. Do not edit expected values to hide the failure. |
| A new terminal has no run variables | Repeat Section 6.3 using the existing run directory, not a new timestamp. |

With multiple JTAG cables or devices, the replay refuses to guess. Its syntax is:

```text
quartus_stp -t scripts/replay_jtag.tcl weather_speed "HARDWARE_NAME" "DEVICE_NAME"
```

Replace the two uppercase placeholders with exact Quartus names for your connected cable and EP2C35. Select the same names in SignalTap. The programming command's cable index must also refer to that device.

## Appendix A What this demonstration establishes

The FPGA predicts from recorded hourly observations. The host does not collect live weather data from the DE2. The first 24 frames fill history; subsequent frames produce predictions three hours beyond the latest observation's timestamp.

A complete run checks 128 inputs and 104 forecasts. Component results are compared bit for bit with the fixed-point reference; the angle check allows five Q8 degree counts, or 0.01953125°, using circular distance. The zero-vector direction flag is checked by the existing replay script.

The full-system speed design has a documented post-edge latency of 40 clocks and an initiation interval of 23 clocks after warm-up. Its six arithmetic lanes operate in parallel, with each lane reusing a multiplier across seven lag terms. JTAG communication is slower than these core schedules.

The software forecasting metrics and historical native captures are available under `docs/reports/`. They support the earlier experiment; identify them as historical when displaying them. New CSVs and a new STP establish the reproduction performed on your connected board.

## Appendix B Saved-result verifier

Save the following as `verify_weather_run.py` inside the run directory. It uses only Python's standard library and reads its input files without modifying the repository or captured data.

```python
import argparse
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('csv_file', type=Path)
parser.add_argument('--stp', type=Path)
parser.add_argument('--vectors', type=Path,
                    default=Path('hardware/jtag/vectors/weather.txt'))
args = parser.parse_args()

with args.csv_file.open(newline='') as stream:
    records = list(csv.DictReader(stream))
assert len(records) == 128, f'Expected 128 rows, got {len(records)}'
for index, row in enumerate(records):
    assert int(row['sample_index']) == index
    assert int(row['accepted_count']) == index + 1
    assert int(row['forecast_count']) == max(0, index - 23)
    expected = 'warmup' if index < 24 else 'True'
    assert row['match'] == expected, (index, row['match'])
print('PASS CSV: 128 inputs, 24 warm-up rows, 104 matching forecasts')
print('First forecast:', records[24]['forecast_physical'])
print('Last forecast: ', records[-1]['forecast_physical'])

if args.stp is not None:
    root = ET.parse(args.stp).getroot()
    signal_set = root.find('instance/signal_set')
    assert signal_set is not None, 'Missing SignalTap signal set'
    data = signal_set.find('trigger/log/data')
    assert data is not None, 'No acquired data saved in this STP'
    count = int(data.get('sample_depth', '-1'))
    trigger = int(data.get('trigger_position', '-1'))
    names = [wire.get('name') for wire in
             signal_set.find('signal_vec/data_input_vec')]
    bits = ''.join((data.text or '').split())
    assert count == 512 and trigger == 256, (count, trigger)
    assert len(bits) == count * len(names), 'Incorrect data length'
    assert set(bits) <= {'0', '1'}, 'Nonbinary acquisition data'
    samples = [bits[i * len(names):(i + 1) * len(names)]
               for i in range(count)]
    positions = {name: index for index, name in enumerate(names)}
    prefix = 'jtag_mailbox:mailbox|'

    def bit(index, name):
        return int(samples[index][positions[prefix + name]])

    def bus(index, name, width):
        return sum(bit(index, f'{name}[{b}]') << b
                   for b in range(width))

    accepts = [i for i in range(count)
               if bit(i, 'sample_valid') and bit(i, 'sample_ready')]
    valids = [i for i in range(count) if bit(i, 'forecast_valid')]
    assert len(accepts) == 1 and len(valids) == 1, (accepts, valids)
    assert all(bit(i, 'core_rst_n') for i in range(count))
    accept, valid = accepts[0], valids[0]
    assert valid - accept == 41, (accept, valid)
    fields = args.vectors.read_text().splitlines()[24].split()
    expected_input = (int(fields[1], 16) >> 2) & ((1 << 108) - 1)
    expected_output = int(fields[4], 16)
    actual_input = bus(accept, 'sample_data', 108)
    actual_output = bus(valid, 'forecast_data', 126)
    mask = (1 << 108) - 1
    assert actual_input == expected_input, 'Captured input mismatch'
    assert (actual_output & mask) == (expected_output & mask), \
        'Captured component mismatch'
    delta = abs((actual_output >> 108) - (expected_output >> 108))
    delta = min(delta, 92160 - delta)
    assert delta <= 5, ('Direction difference', delta)
    print('PASS CAPTURE: 512 samples; input and output match reference')
    print('Accepted index:', accept, 'Forecast-valid index:', valid)
    print('Raw sample separation:', valid - accept)
    print('Forecast word:', hex(actual_output))
```

A changed model, vector file, RTL schedule, trigger, or probe setup is a different experiment. This verifier deliberately checks the supplied reproduction configuration.

## Appendix C References and maintenance

- [Quartus II Web Edition 13.0 SP1 for Windows](https://www.altera.com/downloads/fpga-development-tools/quartus-ii-web-edition-design-software-version-13-0sp1-windows).
- [Quartus II Web Edition 13.0 SP1 for Linux](https://www.altera.com/downloads/fpga-development-tools/quartus-ii-web-edition-design-software-version-13-0sp1-linux).
- [Vendor programming-cable driver instructions](https://www.altera.com/developers/software/cables-and-adapter-drivers-installation-guide).
- [Original DE2 User Manual](https://www-ug.eecg.toronto.edu/msl/manuals/DE2_User_Manual.pdf).
- [JTAG protocol and board-project reference](../../hardware/jtag/README.md).
- [Checked replay implementation](../../scripts/replay_jtag.tcl).
- [Retained physical acquisition checks](../reports/defense_session/SIGNALTAP_CAPTURE_CHECK.json).

The instruction structure follows the [Microsoft procedure-writing guidance](https://learn.microsoft.com/en-us/style-guide/procedures-instructions/writing-step-by-step-instructions) and [Google procedure-writing guidance](https://developers.google.com/style/procedures): state the starting location, perform an action, and check its result.

Keep this guide in Git with the source. If the replay interface or packaged bitstreams change, update the paths, hashes, and expected results together. Do not add a developer's personal filesystem path as a required command.


Procedure validation: on 2 November 2026, a fresh HTTPS clone of commit `a476b32e42db90a7c68c94c941427b44cd9a65a2` was used to check archive extraction, programming-file hashes, and source-file availability. The Appendix B verifier passed the retained replay and acquisition records and rejected a deliberately mismatched CSV row. Bash blocks were syntax-checked. No new physical FPGA run or Windows execution was performed during this documentation check.
