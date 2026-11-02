# USB-Blaster-only forecasting interface

These projects use the FPGA's existing JTAG connection through Quartus In-System Sources and Probes (ISSP). No RS-232 adapter, UART cable, CPU, or Nios system is required. The prediction cores are unchanged. LEDs, seven-segment displays, and LCD are not added by this interface.

## Board projects

Open the appropriate `.qpf` in Quartus II 13.0 SP1:

| Design | Project relative to repository root | Programming file |
| --- | --- | --- |
| Temperature speed | `hardware/quartus/de2_temperature_jtag/temperature.qpf` | Same directory: `output_files/temperature.sof` |
| Temperature resource | `hardware/quartus/de2_temperature_resource_jtag/temperature_resource.qpf` | Same directory: `output_files/temperature_resource.sof` |
| Weather parallel | `versions/weather_v2/quartus/de2_jtag_speed/weather_jtag.qpf` | Same directory: `output_files/weather_jtag.sof` |
| Weather shared | `versions/weather_v2/quartus/de2_jtag_resource/weather_jtag.qpf` | Same directory: `output_files/weather_jtag.sof` |

All target original DE2 / EP2C35F672C6 at 50 MHz. Only CLOCK_50=N2 and KEY0_N=G26 are external application pins. Quartus routes the ISSP node through the device's dedicated JTAG infrastructure. The compiler adds JTAG clock/clock-domain timing constraints; the fitted timing reports show an assumed 10 MHz JTAG TCK. Use a cable TCK no faster than that assumption. All four designs passed physical JTAG replay on 28 October 2026; see the implementation report and retained raw CSVs.

## Program and run

Power the board and connect its USB-Blaster programming interface to this computer. Confirm the original-DE2 board revision and pin map. From the repository root:

```bash
jtagconfig
quartus_pgm -m jtag -c 1 -o 'p;hardware/quartus/de2_temperature_jtag/output_files/temperature.sof'
quartus_stp -t scripts/replay_jtag.tcl temperature
```

Cable index 1 is an example; use the actual cable. Release KEY0 before replay; the script resets the predictor through JTAG itself. It sends 128 golden-vector samples and checks 104 forecasts after 24 warm-up inputs. The vectors are a directed/reference replay, not live sensor data. Forecasts are printed in physical units and saved with raw values, counters, and probe words in `docs/reports/physical_jtag_temperature.csv`.

For temperature resource:

```bash
quartus_pgm -m jtag -c 1 -o 'p;hardware/quartus/de2_temperature_resource_jtag/output_files/temperature_resource.sof'
quartus_stp -t scripts/replay_jtag.tcl temperature_resource
```

`temperature` is the legacy alias for `temperature_speed`; both select the speed core. The resource checker verifies the shared-architecture flag before replay.

For weather parallel:

```bash
quartus_pgm -m jtag -c 1 -o 'p;versions/weather_v2/quartus/de2_jtag_speed/output_files/weather_jtag.sof'
quartus_stp -t scripts/replay_jtag.tcl weather_speed
```

For weather shared:

```bash
quartus_pgm -m jtag -c 1 -o 'p;versions/weather_v2/quartus/de2_jtag_resource/output_files/weather_jtag.sof'
quartus_stp -t scripts/replay_jtag.tcl weather_resource
```

The script checks node identity and variant before sending data. When multiple cables/devices exist, supply their exact names after the variant rather than relying on automatic selection. CSV names are `physical_jtag_weather_speed.csv` and `physical_jtag_weather_resource.csv`. Scalar/component predictions must match the C++ vectors bit-for-bit. Weather angle tolerance is five Q8 degree units, with the correct undefined-vector flag.

## See the result inside Quartus

1. Open the JTAG project and compile if rebuilding, using **Processing → Start Compilation**.
2. Use **Tools → Programmer**, select USB-Blaster, add that project's `.sof`, enable Program/Configure, and program it.
3. Open **Tools → In-System Sources and Probes Editor**.
4. Select the same hardware/device and scan its instances. Expect node **FCST**, index **0**, with **128 source bits** and **256 probe bits**.
5. Use **Read Probe Data** to capture the persistent last forecast and counters. Use hexadecimal radix and the field map below. Add aliases/groups in the editor as useful for screenshots.

Do not run Tcl replay and manual editor writes simultaneously: both control the same request/reset bits. Finish the replay session before reading the result manually. The latest forecast stays latched until another forecast or reset; GUI polling will not miss a one-clock valid pulse.

For a simple manual temperature demonstration, write source hex `2` then `0` to reset. Write alternating `6401` and `6400` to submit the constant temperature 25°C (raw Q8 = `1900`) repeatedly; read the probe after each write and confirm the acknowledgement follows source bit 0. After 25 requests, accepted_count is 25, forecast_count is 1, result_valid is set, and the forecast is raw `1900` = 25°C. This is a constant-input functional example, not a weather-accuracy experiment.

## Source fields: host to FPGA

| Bits | Meaning |
| --- | --- |
| 0 | Request toggle: invert once for each new sample/frame |
| 1 | Reset/clear level: hold at 1 to reset core, counters, history, and last forecast |
| 17:2 (temperature project) | Signed 16-bit temperature Q8 |
| 109:2 (weather projects) | Six signed 18-bit Q8 channels, temperature in the least significant 18 bits, followed by pressure, humidity, wind speed, cosine, sine |
| Remaining source bits | Reserved; write zero |

The automated host first stages payload with the old request bit, waits, then commits the new request bit. The IP synchronizes source outputs to CLOCK_50. The mailbox waits additional settling clocks before capturing the complete payload. Hold the payload/request unchanged until acknowledgement; only one transaction may be outstanding.

## Probe fields: FPGA to host

| Bits | Meaning |
| --- | --- |
| 15:0 (temperature) | Last signed temperature forecast Q8 |
| 17:0 (weather) | Temperature forecast Q8 |
| 35:18 | Pressure Q8, kPa |
| 53:36 | Humidity Q8, percent |
| 71:54 | Wind speed Q8, m/s |
| 89:72 | Direction cosine Q8 |
| 107:90 | Direction sine Q8 |
| 125:108 | Unsigned direction angle, degrees Q8 |
| 143:128 | Accepted-sample counter, modulo 65536 |
| 159:144 | Forecast counter, modulo 65536 |
| 160 | Completion acknowledgement toggle |
| 161 | Mailbox busy |
| 162 | Last result valid; stays asserted until reset |
| 163 | Direction defined (weather); zero for temperature |
| 164 | Core sample_ready |
| 165 | Reset active |
| 166 | Weather design flag |
| 167 | Shared weather architecture flag |
| 223:168 | Reserved zero |
| 255:224 | Design signature `46504741` hexadecimal |

Convert signed Q8 raw integers to physical values by dividing by 256. Warm-up requests are acknowledged without a forecast. After warm-up, acknowledgement is delayed until the predictor result is captured. The host verifies a stable complete probe word after acknowledgement to avoid interpreting an asynchronously captured transition as a coherent result. Hardware reset/JTAG reset cancels pending work; a full new warm-up is required.

## Local verification and limitations

```bash
python3 scripts/make_jtag_vectors.py
python3 scripts/run_jtag_tests.py
python3 scripts/test_jtag_host.py
python3 scripts/build_jtag_report.py
```

The RTL test replaces only the proprietary scan transport with a controllable source register. It instantiates the real mailbox, reset synchronizer, and production predictor cores, checks 128 inputs / 104 forecasts, held-request duplicate protection, reset cancellation, and a fresh 25-input warm-up after reset. The host tests mock the hardware API and explicitly redirect their CSVs into an ignored mock directory; they cannot count as physical evidence.

Three board projects have been fitted and statically timed. This work does not claim full SDF simulation of the proprietary JTAG transport, USB-Blaster driver operation on a physical board, or actual hardware replay. Previous core-level SDF results apply to the unchanged predictor cores; these new complete JTAG wrappers have their own static timing results and RTL integration tests.

Vendor references: [ISSP Tcl API](https://www.intel.com/content/www/us/en/docs/programmable/683819/25-1/tcl-interface-for-the-in-system-sources.html) and [Quartus II scripting reference](https://cdrdv2-public.intel.com/654662/tclscriptrefmnl.pdf). The installed Quartus 13 megafunction declaration supplies the actual parameters used in `jtag_issp.v`.
