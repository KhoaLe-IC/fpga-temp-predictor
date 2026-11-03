# Defense hardware-session evidence status

USB-Blaster is connected and visible to Linux as Altera USB device `09fb:6001`. Quartus detects `USB-Blaster variant [1-1]`, but its chain scan reports:

```text
Unable to lock chain (Hardware not attached)
```

This identifies a current chain-access failure; it does not by itself prove whether the cause is board power, the board-side cable connection, configuration, or another hardware/driver issue. Board power and programming-port connection need to be checked before programming can proceed. No FPGA IDCODE was obtained in this session.

The temperature JTAG project was launched in Quartus. A running application process confirms the launch, but no native Quartus screenshot has been captured, so a screenshot-backed GUI claim is not made.

## Evidence currently available

- [USB enumeration](defense_session/usb_devices.txt)
- [Quartus chain scan](defense_session/jtag_detection.txt)
- [Current completion audit](defense_session/completion_audit.txt)
- [Session manifest](defense_session/session_status.json)
- [Fitted JTAG projects and local verification](JTAG_IMPLEMENTATION_REPORT.md)

The passing fitted and simulated results predate this physical connection attempt. They remain implementation evidence, not proof of successful programming or physical inference.

## Defense capture checklist

| Capture | What it must show | Current state |
| --- | --- | --- |
| Quartus project/device | Correct JTAG project, top-level entity, EP2C35F672C6 | Project launched; screenshot missing |
| Compilation report | Successful flow and measured resource use for each design | Saved reports available; GUI screenshots missing |
| TimeQuest | CLOCK_50 = 20 ns, nonnegative setup/hold slack | Saved reports available; GUI screenshots missing |
| RTL/Technology Map Viewer | Implemented forecast/interface structure | Screenshot missing |
| Programmer | Detected FPGA, correct .sof, completed Program/Configure | Blocked by inaccessible FPGA chain |
| In-System Sources and Probes | FCST node, changing counters, latched forecast | Blocked until programming succeeds |
| Physical replay | 128 accepted inputs and 104 checked forecasts per design | Not run on hardware |
| Board photograph/video | Actual board, power, cable, and visible test context | Not captured |

## Remaining work

1. Restore access to the powered FPGA JTAG chain and record the actual device identity.
2. Program and replay temperature, parallel weather, and shared weather JTAG designs; retain real CSV/log evidence.
3. Capture genuine Quartus GUI screenshots and explain the scope of each image.
4. Update the physical-verification reports only after the tests actually pass.

The available computer-use surface currently exposes no native Quartus window for screenshot/control. The existing browser surface cannot capture the Quartus application. GUI evidence remains missing; no generated or simulated image is substituted for a real application screenshot.
