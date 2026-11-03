create_clock -name clk -period 20.000 [get_ports {clk}]
derive_clock_uncertainty
set_input_delay -clock clk -max 2.0 [get_ports {rst_n sample_valid temp_in[*]}]
set_input_delay -clock clk -min 0.0 [get_ports {rst_n sample_valid temp_in[*]}]
set_output_delay -clock clk -max 2.0 [get_ports {sample_ready forecast_valid forecast_out[*]}]
set_output_delay -clock clk -min 0.0 [get_ports {sample_ready forecast_valid forecast_out[*]}]
