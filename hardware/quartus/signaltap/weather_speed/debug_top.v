module de2_weather_jtag #(parameter SHARED=0)(input CLOCK_50,input KEY0_N);
 (* keep = "true" *) wire board_rst_n,core_rst_n,sample_valid,sample_ready,forecast_valid,defined;
 (* keep = "true" *) wire [127:0] source;(* keep = "true" *) wire [255:0] probe;(* keep = "true" *) wire [107:0] sample_data;
 (* keep = "true" *) wire signed [17:0] t,p,h,w,c,s;(* keep = "true" *) wire [17:0] angle;
 reset_sync reset_unit(.clk(CLOCK_50),.reset_n_in(KEY0_N),.reset_n_sync(board_rst_n));
 jtag_issp access_unit(.clk(CLOCK_50),.probe(probe),.source(source));
 jtag_mailbox #(.RESULT_WIDTH(126),.WEATHER(1),.SHARED(SHARED)) mailbox(
 .clk(CLOCK_50),.board_rst_n(board_rst_n),.source(source),.probe(probe),
 .core_rst_n(core_rst_n),.sample_valid(sample_valid),.sample_data(sample_data),
 .sample_ready(sample_ready),.forecast_valid(forecast_valid),
 .forecast_data({angle,s,c,w,h,p,t}),.direction_defined(defined));
 generate if(SHARED==0)begin:g_parallel
 weather_system_speed predictor(
 .clk(CLOCK_50),.rst_n(core_rst_n),.sample_valid(sample_valid),.sample_ready(sample_ready),
 .temperature_in(sample_data[17:0]),.pressure_in(sample_data[35:18]),.humidity_in(sample_data[53:36]),
 .wind_speed_in(sample_data[71:54]),.direction_cos_in(sample_data[89:72]),.direction_sin_in(sample_data[107:90]),
 .forecast_valid(forecast_valid),.temperature_out(t),.pressure_out(p),.humidity_out(h),.wind_speed_out(w),
 .direction_cos_out(c),.direction_sin_out(s),.wind_direction_out(angle),.direction_defined(defined));
 end else begin:g_shared
 weather_system_resource predictor(
 .clk(CLOCK_50),.rst_n(core_rst_n),.sample_valid(sample_valid),.sample_ready(sample_ready),
 .temperature_in(sample_data[17:0]),.pressure_in(sample_data[35:18]),.humidity_in(sample_data[53:36]),
 .wind_speed_in(sample_data[71:54]),.direction_cos_in(sample_data[89:72]),.direction_sin_in(sample_data[107:90]),
 .forecast_valid(forecast_valid),.temperature_out(t),.pressure_out(p),.humidity_out(h),.wind_speed_out(w),
 .direction_cos_out(c),.direction_sin_out(s),.wind_direction_out(angle),.direction_defined(defined));
 end endgenerate
endmodule
