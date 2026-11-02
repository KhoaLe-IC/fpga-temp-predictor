# USB-Blaster JTAG Interface Implementation Report

Date: 28 October 2026 (Asia/Ho_Chi_Minh).

Four separate JTAG board projects have been added for the original DE2, allowing sample input and persistent forecast readback using USB-Blaster alone. The UART projects and prediction cores are unchanged. This is an In-System Sources and Probes mailbox, not a UART emulation or a JTAG UART/Nios system.

## Measured fitted results

All target EP2C35F672C6 with CLOCK_50 at 20 ns. The vendor JTAG clock constraint is 10 MHz; the domains are asynchronous, using the IP's synchronized source and a held-data request/acknowledgement protocol. All four fits are successful, setup/hold slack is nonnegative, and there are zero unconstrained application input/output paths.

| Design | LE | Registers | Memory bits | 9-bit multiplier elements | Fmax MHz | Setup slack ns | Hold slack ns |
| --- | --- | --- | --- | --- | --- | --- | --- |
| temperature | 1130 | 1016 | 336 | 4 | 190.48 | 14.750 | 0.215 |
| temperature_resource | 1541 | 1352 | 0 | 2 | 139.37 | 12.825 | 0.215 |
| weather_speed | 6253 | 4571 | 0 | 12 | 79.74 | 7.459 | 0.215 |
| weather_resource | 5598 | 4192 | 0 | 2 | 79.23 | 7.378 | 0.215 |

## Verification performed

- Four RTL integration replays passed 128 inputs / 104 forecasts each, followed by reset cancellation and a 25-input fresh-history replay. The real predictor and mailbox are tested; only the vendor scan transport is mocked.
- Held request bits do not create duplicate samples; forecasts remain latched for host/GUI reads.
- Native Quartus Tcl host tests passed for all four variants under explicitly mocked JTAG APIs; corrupted temperature and weather outputs were correctly rejected. Mock CSVs are isolated from physical evidence.
- All four designs were programmed on the actual DE2 through USB-Blaster and passed physical JTAG replay: 128 accepted inputs, 104 checked forecasts per design. Temperature and six weather-channel outputs match fixed-point references exactly; wind-angle tolerance is 5 Q8 units. Raw CSVs and programming/replay logs are retained. UART physical operation has not been tested.
- These new wrappers have not undergone full SDF simulation of the JTAG IP. The prior four predictor-core SDF passes remain evidence for the unchanged cores, not a substitute for full interface hardware validation.

## Files and operation

See [JTAG interface guide](../../hardware/jtag/README.md) for project paths, GUI steps, source/probe bit maps, programming commands, and the host checker. Results can be read in **Quartus → Tools → In-System Sources and Probes Editor**, node **FCST**, or through `quartus_stp -t scripts/replay_jtag.tcl <variant>`.

The board needs only power and USB-Blaster; KEY0 must be released. JTAG reset is implemented, so a physical reset-button press is optional. The interface does not add LEDs, seven-segment output, or LCD output. The computer receives raw Q8 values and converted physical values; the Quartus editor can display and group the raw source/probe fields.

Physical acceptance passed separately for temperature speed, temperature resource, weather speed, and weather resource. CSVs are `physical_jtag_temperature.csv` (speed), `physical_jtag_temperature_resource.csv`, `physical_jtag_weather_speed.csv`, and `physical_jtag_weather_resource.csv`. The canonical speed alias also has `physical_jtag_temperature_speed.csv`. Source/configuration and programming-file hashes are retained in [JTAG artifact manifest](JTAG_ARTIFACT_MANIFEST.json).

## Interpretation and limits

These totals include the predictor, mailbox and vendor JTAG IP. They are separate from core-only results and from the additional SignalTap debug builds. Temperature resource halves embedded multiplier elements (4 to 2), but uses more LEs (1,130 to 1,541) and registers; sharing a multiplier does not guarantee lower total area. Weather resource reduces multiplier elements from 12 to 2 and reduces LEs. Fmax is a TimeQuest estimate; physical operation was tested at 50 MHz. JTAG replay tests functional arithmetic and communication, not forecast accuracy against future observations. The temperature replay uses directed synthetic vectors; historical accuracy is established separately by the model evaluation reports.

SignalTap capture evidence is documented separately in the defense-session report. SignalTap hardware changes fitted utilization, so its resource totals must not replace the uninstrumented comparison above.
