module weather_system_speed(input clk,input rst_n,input sample_valid,output sample_ready,
input signed [17:0] temperature_in,pressure_in,humidity_in,wind_speed_in,direction_cos_in,direction_sin_in,
output forecast_valid,output reg signed [17:0] temperature_out,pressure_out,humidity_out,wind_speed_out,direction_cos_out,direction_sin_out,
output [17:0] wind_direction_out,output direction_defined);
wire core_valid;
wire signed [17:0] temperature_core,pressure_core,humidity_core,wind_speed_core,direction_cos_core,direction_sin_core;
weather_predictor_speed core(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid),.sample_ready(sample_ready),.forecast_valid(core_valid),
.temperature_in(temperature_in),.temperature_out(temperature_core),
.pressure_in(pressure_in),.pressure_out(pressure_core),
.humidity_in(humidity_in),.humidity_out(humidity_core),
.wind_speed_in(wind_speed_in),.wind_speed_out(wind_speed_core),
.direction_cos_in(direction_cos_in),.direction_cos_out(direction_cos_core),
.direction_sin_in(direction_sin_in),.direction_sin_out(direction_sin_core));
wind_direction_cordic angle_unit(.clk(clk),.rst_n(rst_n),.in_valid(core_valid),.cos_in(direction_cos_core),.sin_in(direction_sin_core),.out_valid(forecast_valid),.angle_out(wind_direction_out),.angle_defined(direction_defined));
always @(posedge clk) begin
if(!rst_n) begin
temperature_out<=0;
pressure_out<=0;
humidity_out<=0;
wind_speed_out<=0;
direction_cos_out<=0;
direction_sin_out<=0;
end else if(core_valid) begin
temperature_out<=temperature_core;
pressure_out<=pressure_core;
humidity_out<=humidity_core;
wind_speed_out<=wind_speed_core;
direction_cos_out<=direction_cos_core;
direction_sin_out<=direction_sin_core;
end
end
endmodule
