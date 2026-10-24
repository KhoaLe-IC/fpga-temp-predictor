create_clock -name clk -period 20.000 [get_ports clk]
derive_clock_uncertainty
set_input_delay -clock clk -max 2.0 [get_ports {*_in[*] rst_n sample_valid}]
set_input_delay -clock clk -min 0.0 [get_ports {*_in[*] rst_n sample_valid}]
set_output_delay -clock clk -max 2.0 [get_ports {*_out[*] sample_ready forecast_valid direction_defined}]
set_output_delay -clock clk -min 0.0 [get_ports {*_out[*] sample_ready forecast_valid direction_defined}]
