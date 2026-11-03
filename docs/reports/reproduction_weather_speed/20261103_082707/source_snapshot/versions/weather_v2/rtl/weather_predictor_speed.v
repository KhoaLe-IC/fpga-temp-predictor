module weather_predictor_speed(input clk,input rst_n,input sample_valid,output sample_ready,
 input signed [17:0] temperature_in,pressure_in,humidity_in,wind_speed_in,direction_cos_in,direction_sin_in,
 output forecast_valid,output signed [17:0] temperature_out,pressure_out,humidity_out,wind_speed_out,direction_cos_out,direction_sin_out);
wire [5:0] ready,valid;assign sample_ready=&ready;assign forecast_valid=&valid;
weather_ar_channel #(.CHANNEL(0)) c0(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid && sample_ready),.sample_ready(ready[0]),.sample_in(temperature_in),.forecast_valid(valid[0]),.forecast_out(temperature_out));
weather_ar_channel #(.CHANNEL(1)) c1(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid && sample_ready),.sample_ready(ready[1]),.sample_in(pressure_in),.forecast_valid(valid[1]),.forecast_out(pressure_out));
weather_ar_channel #(.CHANNEL(2)) c2(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid && sample_ready),.sample_ready(ready[2]),.sample_in(humidity_in),.forecast_valid(valid[2]),.forecast_out(humidity_out));
weather_ar_channel #(.CHANNEL(3)) c3(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid && sample_ready),.sample_ready(ready[3]),.sample_in(wind_speed_in),.forecast_valid(valid[3]),.forecast_out(wind_speed_out));
weather_ar_channel #(.CHANNEL(4)) c4(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid && sample_ready),.sample_ready(ready[4]),.sample_in(direction_cos_in),.forecast_valid(valid[4]),.forecast_out(direction_cos_out));
weather_ar_channel #(.CHANNEL(5)) c5(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid && sample_ready),.sample_ready(ready[5]),.sample_in(direction_sin_in),.forecast_valid(valid[5]),.forecast_out(direction_sin_out));
endmodule
