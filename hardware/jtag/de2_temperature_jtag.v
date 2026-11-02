module de2_temperature_jtag(input CLOCK_50,input KEY0_N);
 wire board_rst_n,core_rst_n,sample_valid,sample_ready,forecast_valid;
 wire [127:0] source;wire [255:0] probe;wire [107:0] sample_data;
 wire signed [15:0] forecast_out;
 reset_sync reset_unit(.clk(CLOCK_50),.reset_n_in(KEY0_N),.reset_n_sync(board_rst_n));
 jtag_issp access_unit(.clk(CLOCK_50),.probe(probe),.source(source));
 jtag_mailbox mailbox(.clk(CLOCK_50),.board_rst_n(board_rst_n),.source(source),.probe(probe),
 .core_rst_n(core_rst_n),.sample_valid(sample_valid),.sample_data(sample_data),
 .sample_ready(sample_ready),.forecast_valid(forecast_valid),.forecast_data(forecast_out),.direction_defined(1'b0));
 temp_predictor_speed predictor(.clk(CLOCK_50),.rst_n(core_rst_n),.sample_valid(sample_valid),
 .sample_ready(sample_ready),.temp_in(sample_data[15:0]),.forecast_valid(forecast_valid),.forecast_out(forecast_out));
endmodule
