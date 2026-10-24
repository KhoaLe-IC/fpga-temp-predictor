"""Generate static seven-tap autoregressive coefficients after validation selection, rejecting cross-channel weights."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'models/model.json').read_text());w=m['weights_q14'];b=m['bias_q8'];lags=m['lags_hours']
for c in range(6):
 if any(v and j%6!=c for j,v in enumerate(w[c])): raise ValueError('Selected model needs multivariate RTL')
s='''// Generated from models/model.json; 18-bit Q8 samples, Q14 coefficients.
module weather_ar_channel #(parameter CHANNEL=0)(input clk,input rst_n,input sample_valid,output sample_ready,input signed [17:0] sample_in,output reg forecast_valid,output reg signed [17:0] forecast_out);
reg signed [17:0] hist[0:24];
reg [4:0] count;reg [3:0] state;reg [2:0] term;
reg signed [17:0] operand; reg signed [35:0] product;reg signed [47:0] acc;
integer i;
assign sample_ready=rst_n && state==0;
function signed [17:0] coefficient;input integer k;begin case(CHANNEL*7+k)
'''
for c in range(6):
 for k in range(7):s+=f'{c*7+k}: coefficient=18\'h{w[c][k*6+c]&262143:05x};\n'
s+='default:coefficient=0;endcase end endfunction\nfunction signed [31:0] bias; input integer c;begin case(c)\n'
for c,v in enumerate(b):s+=f'{c}:bias=32\'h{v&0xffffffff:08x};\n'
s+='default:bias=0;endcase end endfunction\nfunction integer lag;input integer k;begin case(k)\n'
for k,v in enumerate(lags):s+=f'{k}:lag={v};\n'
s+='''default:lag=0;endcase end endfunction
wire signed [47:0] scaled=acc>>>14;
reg signed [47:0] limited;
always @* begin
 limited=scaled;
 if(CHANNEL==2) begin if(scaled<0) limited=0;else if(scaled>25600) limited=25600;end
 if(CHANNEL==3 && scaled<0) limited=0;
 if(CHANNEL>=4) begin if(scaled < -256) limited=-256;else if(scaled>256) limited=256;end
end
always @(posedge clk) begin
 if(!rst_n) begin count<=0;state<=0;term<=0;forecast_valid<=0;forecast_out<=0;operand<=0;product<=0;acc<=0;end
 else begin
 forecast_valid<=0;
 case(state)
 0:if(sample_valid && sample_ready) begin
   for(i=24;i>0;i=i-1) hist[i]<=hist[i-1];hist[0]<=sample_in;
   if(count<24) count<=count+1;
   if(count==24) begin acc<=$signed(bias(CHANNEL))*48'sd16384;term<=0;state<=1;end
 end
 1:begin operand<=hist[lag(term)];state<=2;end
 2:begin product<=operand*coefficient(term);state<=3;end
 3:begin acc<=acc+{{12{product[35]}},product};if(term==6)state<=4;else begin term<=term+1;state<=1;end end
 4:begin
   if(limited>131071)forecast_out<=18'h1ffff;else if(limited < -131072)forecast_out<=18'h20000;else forecast_out<=limited[17:0];
   forecast_valid<=1;state<=0;
 end
 endcase
 end
end
endmodule
'''
(R/'rtl/weather_ar_channel.v').write_text(s)
# Parallel channel bank: independent arithmetic, common acceptance.
s='''module weather_predictor_speed(input clk,input rst_n,input sample_valid,output sample_ready,
 input signed [17:0] temperature_in,pressure_in,humidity_in,wind_speed_in,direction_cos_in,direction_sin_in,
 output forecast_valid,output signed [17:0] temperature_out,pressure_out,humidity_out,wind_speed_out,direction_cos_out,direction_sin_out);
wire [5:0] ready,valid;assign sample_ready=&ready;assign forecast_valid=&valid;
'''
ins=['temperature','pressure','humidity','wind_speed','direction_cos','direction_sin']
for c,n in enumerate(ins):s+=f'weather_ar_channel #(.CHANNEL({c})) c{c}(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid && sample_ready),.sample_ready(ready[{c}]),.sample_in({n}_in),.forecast_valid(valid[{c}]),.forecast_out({n}_out));\n'
s+='endmodule\n';(R/'rtl/weather_predictor_speed.v').write_text(s)
print('Generated parallel six-channel seven-tap autoregressive RTL')
s=(R/'rtl/weather_ar_channel.v').read_text()
a=s.index('reg signed [17:0] hist')
s='''// Shared multiplier implementation; one transaction contains six synchronous samples.
module weather_predictor_resource(input clk,input rst_n,input sample_valid,output sample_ready,
 input signed [17:0] temperature_in,pressure_in,humidity_in,wind_speed_in,direction_cos_in,direction_sin_in,
 output reg forecast_valid,output reg signed [17:0] temperature_out,pressure_out,humidity_out,wind_speed_out,direction_cos_out,direction_sin_out);
reg [2:0] channel;reg signed [17:0] forecast_out;
'''+s[a:]
s=s.replace('hist[0:24]','hist[0:149]').replace('integer i;','integer i,j;').replace('CHANNEL','channel').replace('operand<=hist[lag(term)]','operand<=hist[channel*25+lag(term)]')
s=s.replace('forecast_out<=0;operand<=0;', 'forecast_out<=0;channel<=0;temperature_out<=0;pressure_out<=0;humidity_out<=0;wind_speed_out<=0;direction_cos_out<=0;direction_sin_out<=0;operand<=0;')
s=s.replace('for(i=24;i>0;i=i-1) hist[i]<=hist[i-1];hist[0]<=sample_in;', '''for(j=0;j<6;j=j+1) for(i=24;i>0;i=i-1) hist[j*25+i]<=hist[j*25+i-1];
hist[0]<=temperature_in;hist[25]<=pressure_in;hist[50]<=humidity_in;hist[75]<=wind_speed_in;hist[100]<=direction_cos_in;hist[125]<=direction_sin_in;''')
s=s.replace('acc<=$signed(bias(channel))*48\'sd16384;term<=0;state<=1;','acc<=$signed(bias(0))*48\'sd16384;channel<=0;term<=0;state<=1;')
s=s.replace('forecast_valid<=1;state<=0;', '''state<=5;
 end
 5:begin
 case(channel)
 0:temperature_out<=forecast_out;1:pressure_out<=forecast_out;2:humidity_out<=forecast_out;3:wind_speed_out<=forecast_out;4:direction_cos_out<=forecast_out;5:direction_sin_out<=forecast_out;
 endcase
 if(channel==5) begin forecast_valid<=1;state<=0;end
 else begin channel<=channel+1;term<=0;acc<=$signed(bias(channel+1))*48'sd16384;state<=1;end''')
(R/'rtl/weather_predictor_resource.v').write_text(s)
print('Generated shared-multiplier six-channel seven-tap autoregressive RTL')
# Size control arithmetic explicitly to avoid implicit 32-bit narrowing warnings.
import re
for filename in ['weather_ar_channel.v','weather_predictor_resource.v']:
 p=R/'rtl'/filename;s=p.read_text().replace('count+1',"count+5'd1").replace('term+1',"term+3'd1").replace('channel+1',"channel+3'd1")
 if filename=='weather_predictor_resource.v':
  s=s.replace('coefficient;input integer k;begin case(channel*7+k)','coefficient;input [2:0] k;begin case({channel,k})')
  s=re.sub(r'(?m)^(\d+): coefficient=',lambda match:f'{(int(match[1])//7)*8+int(match[1])%7}: coefficient=',s)
 p.write_text(s)
