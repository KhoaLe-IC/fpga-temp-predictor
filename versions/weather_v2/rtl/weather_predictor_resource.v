// Shared multiplier implementation; one transaction contains six synchronous samples.
module weather_predictor_resource(input clk,input rst_n,input sample_valid,output sample_ready,
 input signed [17:0] temperature_in,pressure_in,humidity_in,wind_speed_in,direction_cos_in,direction_sin_in,
 output reg forecast_valid,output reg signed [17:0] temperature_out,pressure_out,humidity_out,wind_speed_out,direction_cos_out,direction_sin_out);
reg [2:0] channel;reg signed [17:0] forecast_out;
reg signed [17:0] hist[0:149];
reg [4:0] count;reg [3:0] state;reg [2:0] term;
reg signed [17:0] operand; reg signed [35:0] product;reg signed [47:0] acc;
integer i,j;
assign sample_ready=rst_n && state==0;
function signed [17:0] coefficient;input [2:0] k;begin case({channel,k})
0: coefficient=18'h04e43;
1: coefficient=18'h3db89;
2: coefficient=18'h00655;
3: coefficient=18'h3ff33;
4: coefficient=18'h0000f;
5: coefficient=18'h03654;
6: coefficient=18'h3d772;
8: coefficient=18'h073e8;
9: coefficient=18'h3b0b6;
10: coefficient=18'h01443;
11: coefficient=18'h0029c;
12: coefficient=18'h3fdff;
13: coefficient=18'h02d2e;
14: coefficient=18'h3d749;
16: coefficient=18'h043b4;
17: coefficient=18'h3e69e;
18: coefficient=18'h00387;
19: coefficient=18'h3feaa;
20: coefficient=18'h000fb;
21: coefficient=18'h0368a;
22: coefficient=18'h3da1b;
24: coefficient=18'h05a00;
25: coefficient=18'h3c97c;
26: coefficient=18'h00693;
27: coefficient=18'h000bd;
28: coefficient=18'h000b8;
29: coefficient=18'h02276;
30: coefficient=18'h3e9ce;
32: coefficient=18'h04c97;
33: coefficient=18'h3dd37;
34: coefficient=18'h3ff13;
35: coefficient=18'h3ffe2;
36: coefficient=18'h0047a;
37: coefficient=18'h01739;
38: coefficient=18'h3f598;
40: coefficient=18'h04a73;
41: coefficient=18'h3e052;
42: coefficient=18'h3ff74;
43: coefficient=18'h0049f;
44: coefficient=18'h00558;
45: coefficient=18'h010aa;
46: coefficient=18'h3f82d;
default:coefficient=0;endcase end endfunction
function signed [31:0] bias; input integer c;begin case(c)
0:bias=32'h00000136;
1:bias=32'h00000337;
2:bias=32'h0000025a;
3:bias=32'h00000059;
4:bias=32'hfffffffb;
5:bias=32'h00000000;
default:bias=0;endcase end endfunction
function integer lag;input integer k;begin case(k)
0:lag=0;
1:lag=1;
2:lag=3;
3:lag=6;
4:lag=12;
5:lag=21;
6:lag=24;
default:lag=0;endcase end endfunction
wire signed [47:0] scaled=acc>>>14;
reg signed [47:0] limited;
always @* begin
 limited=scaled;
 if(channel==2) begin if(scaled<0) limited=0;else if(scaled>25600) limited=25600;end
 if(channel==3 && scaled<0) limited=0;
 if(channel>=4) begin if(scaled < -256) limited=-256;else if(scaled>256) limited=256;end
end
always @(posedge clk) begin
 if(!rst_n) begin count<=0;state<=0;term<=0;forecast_valid<=0;forecast_out<=0;channel<=0;temperature_out<=0;pressure_out<=0;humidity_out<=0;wind_speed_out<=0;direction_cos_out<=0;direction_sin_out<=0;operand<=0;product<=0;acc<=0;end
 else begin
 forecast_valid<=0;
 case(state)
 0:if(sample_valid && sample_ready) begin
   for(j=0;j<6;j=j+1) for(i=24;i>0;i=i-1) hist[j*25+i]<=hist[j*25+i-1];
hist[0]<=temperature_in;hist[25]<=pressure_in;hist[50]<=humidity_in;hist[75]<=wind_speed_in;hist[100]<=direction_cos_in;hist[125]<=direction_sin_in;
   if(count<24) count<=count+5'd1;
   if(count==24) begin acc<=$signed(bias(0))*48'sd16384;channel<=0;term<=0;state<=1;end
 end
 1:begin operand<=hist[channel*25+lag(term)];state<=2;end
 2:begin product<=operand*coefficient(term);state<=3;end
 3:begin acc<=acc+{{12{product[35]}},product};if(term==6)state<=4;else begin term<=term+3'd1;state<=1;end end
 4:begin
   if(limited>131071)forecast_out<=18'h1ffff;else if(limited < -131072)forecast_out<=18'h20000;else forecast_out<=limited[17:0];
   state<=5;
 end
 5:begin
 case(channel)
 0:temperature_out<=forecast_out;1:pressure_out<=forecast_out;2:humidity_out<=forecast_out;3:wind_speed_out<=forecast_out;4:direction_cos_out<=forecast_out;5:direction_sin_out<=forecast_out;
 endcase
 if(channel==5) begin forecast_valid<=1;state<=0;end
 else begin channel<=channel+3'd1;term<=0;acc<=$signed(bias(channel+3'd1))*48'sd16384;state<=1;end
 end
 endcase
 end
end
endmodule
