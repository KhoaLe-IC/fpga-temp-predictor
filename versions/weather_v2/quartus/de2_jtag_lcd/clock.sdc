create_clock -name CLOCK_50 -period 20.000 [get_ports CLOCK_50]
derive_clock_uncertainty
set_false_path -from [get_ports KEY0_N] -to [get_registers {*reset_unit|sync_ff[0]}]
# HD44780 bus: microsecond-scale set-up/hold is guaranteed by the driver's counters, not by STA.
set_false_path -to [get_ports {LCD_DATA[*] LCD_RS LCD_EN LCD_RW LCD_ON LCD_BLON}]
