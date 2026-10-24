create_clock -name CLOCK_50 -period 20.000 [get_ports CLOCK_50]
derive_clock_uncertainty
# Asynchronous board inputs terminate at the first synchronizer stage.
set_false_path -from [get_ports KEY0_N] -to [get_registers {*reset_unit|sync_ff[0]}]
set_false_path -from [get_ports UART_RXD] -to [get_registers {*receiver|rxd_ff1}]
# UART output is observed asynchronously, not by a CLOCK_50 synchronous receiver.
set_false_path -to [get_ports UART_TXD]
