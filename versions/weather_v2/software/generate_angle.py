from pathlib import Path
import math
R=Path(__file__).resolve().parents[1]
s='''// Iterative vectoring CORDIC. Input: signed Q8 cosine/sine; angle: unsigned degrees Q8.
// The zero vector has no direction: angle_defined=0, angle_out=0.
module wind_direction_cordic(input clk,input rst_n,input in_valid,
 input signed [17:0] cos_in,sin_in,output reg out_valid,
 output reg [17:0] angle_out,output reg angle_defined);
reg busy;reg [4:0] step;
reg signed [35:0] x,y;
reg signed [31:0] angle;
reg defined;
function signed [31:0] atan_deg;input integer i;begin case(i)
'''
for i in range(16):s+=f'{i}:atan_deg=32\'sd{round(math.degrees(math.atan(2**-i))*65536)};\n'
s+='''default:atan_deg=0;endcase end endfunction
wire signed [31:0] wrapped=angle<0 ? angle+32'sd23592960 : angle;
always @(posedge clk) begin
 if(!rst_n) begin busy<=0;step<=0;x<=0;y<=0;angle<=0;defined<=0;out_valid<=0;angle_out<=0;angle_defined<=0;end
 else begin
 out_valid<=0;
 if(!busy) begin
  if(in_valid) begin
   busy<=1;step<=0;defined<=(cos_in!=0 || sin_in!=0);
   if(cos_in<0) begin
    x<=-($signed(cos_in)*36'sd65536);y<=-($signed(sin_in)*36'sd65536);
    angle<=sin_in<0 ? -32'sd11796480 : 32'sd11796480;
   end else begin x<=$signed(cos_in)*36'sd65536;y<=$signed(sin_in)*36'sd65536;angle<=0;end
  end
 end else if(step<16) begin
  if(y>0) begin x<=x+(y>>>step);y<=y-(x>>>step);angle<=angle+atan_deg(step);end
  else if(y<0) begin x<=x-(y>>>step);y<=y+(x>>>step);angle<=angle-atan_deg(step);end
  step<=step+5'd1;
 end else begin
  angle_out<=defined ? wrapped[25:8] : 18'd0;
  angle_defined<=defined;out_valid<=1;busy<=0;
 end
 end
end
endmodule
'''
(R/'rtl/wind_direction_cordic.v').write_text(s)
for variant in ['speed','resource']:
 names=['temperature','pressure','humidity','wind_speed','direction_cos','direction_sin']
 s=f'module weather_system_{variant}(input clk,input rst_n,input sample_valid,output sample_ready,\n'
 s+='input signed [17:0] '+','.join(n+'_in' for n in names)+',\noutput forecast_valid,output reg signed [17:0] '+','.join(n+'_out' for n in names)+',\noutput [17:0] wind_direction_out,output direction_defined);\n'
 s+='wire core_valid;\nwire signed [17:0] '+','.join(n+'_core' for n in names)+';\n'
 s+=f'weather_predictor_{variant} core(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid),.sample_ready(sample_ready),.forecast_valid(core_valid),\n'
 s+=',\n'.join(f'.{n}_in({n}_in),.{n}_out({n}_core)' for n in names)+');\n'
 s+='wind_direction_cordic angle_unit(.clk(clk),.rst_n(rst_n),.in_valid(core_valid),.cos_in(direction_cos_core),.sin_in(direction_sin_core),.out_valid(forecast_valid),.angle_out(wind_direction_out),.angle_defined(direction_defined));\n'
 s+='always @(posedge clk) begin\nif(!rst_n) begin\n'+''.join(n+'_out<=0;\n' for n in names)+'end else if(core_valid) begin\n'+''.join(n+'_out<='+n+'_core;\n' for n in names)+'end\nend\nendmodule\n'
 (R/f'rtl/weather_system_{variant}.v').write_text(s)
