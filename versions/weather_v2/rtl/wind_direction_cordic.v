// Iterative vectoring CORDIC. Input: signed Q8 cosine/sine; angle: unsigned degrees Q8.
// The zero vector has no direction: angle_defined=0, angle_out=0.
module wind_direction_cordic(input clk,input rst_n,input in_valid,
 input signed [17:0] cos_in,sin_in,output reg out_valid,
 output reg [17:0] angle_out,output reg angle_defined);
reg busy;reg [4:0] step;
reg signed [35:0] x,y;
reg signed [31:0] angle;
reg defined;
function signed [31:0] atan_deg;input integer i;begin case(i)
0:atan_deg=32'sd2949120;
1:atan_deg=32'sd1740967;
2:atan_deg=32'sd919879;
3:atan_deg=32'sd466945;
4:atan_deg=32'sd234379;
5:atan_deg=32'sd117304;
6:atan_deg=32'sd58666;
7:atan_deg=32'sd29335;
8:atan_deg=32'sd14668;
9:atan_deg=32'sd7334;
10:atan_deg=32'sd3667;
11:atan_deg=32'sd1833;
12:atan_deg=32'sd917;
13:atan_deg=32'sd458;
14:atan_deg=32'sd229;
15:atan_deg=32'sd115;
default:atan_deg=0;endcase end endfunction
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
