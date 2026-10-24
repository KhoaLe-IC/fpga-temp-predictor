# Cyclone II implementation projects

Target: EP2C35F672C6, Quartus II 13.0 SP1, 50 MHz.

- `speed/`: temperature parallel arithmetic core.
- `resource/`: temperature multiplier-shared core.
- `de2_temperature/`: pinned original-DE2 UART wrapper (50 MHz, 115200 baud, 8-N-1).

Run `quartus_sh --flow compile predictor` inside either core directory, or `quartus_sh --flow compile temperature` inside `de2_temperature`.

Both static coefficient files must match `software/models_cpp/model.json`. Current quantized integers: 12214, 150, 0. Changing coefficients requires recompilation.

The board project uses CLOCK_50=N2, KEY0_N=G26, UART_RXD=C25, UART_TXD=B25. These are original-DE2 pin assignments from the Altera DE2 manual, not DE2-115 assignments. All unused pins are configured as input tri-stated. Core project pins are automatically placed solely for implementation measurements; do not program a core-only bitstream onto the board.

After programming the board wrapper, hold and release KEY0 before sending data. UART packets and checksums are documented in `hardware/speed_optimized/de2_temp_predictor_top.v`. The first 24 accepted temperatures fill history and produce no reply. From sample 25 onward, send one sample and wait for its complete reply before sending the next. The board's DB9 uses RS-232 electrical levels through MAX232; use a suitable serial adapter. USB-Blaster is for programming, not this data protocol.

Physical-board operation remains unverified until a connected board is programmed and its outputs are captured. See `docs/reports/IMPLEMENTATION_STATUS.md` for measured results and limitations.
