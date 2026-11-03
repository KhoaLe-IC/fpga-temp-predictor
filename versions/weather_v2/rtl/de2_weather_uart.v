// Original DE2 UART board wrapper. Host uses stop-and-wait after warm-up.
// Request: AA 55 02 12 + six signed 24-bit big-endian Q8 words + XOR checksum.
// Reply: AA 55 82 16 + six signed 24-bit Q8 outputs + unsigned 24-bit Q8
// direction + one direction-defined byte + XOR checksum. XOR excludes AA 55.
module de2_weather_uart #(parameter SHARED=0)(input CLOCK_50,input KEY0_N,input UART_RXD,output UART_TXD);
wire rst_n;reset_sync reset_unit(.clk(CLOCK_50),.reset_n_in(KEY0_N),.reset_n_sync(rst_n));
wire [7:0] rx_data;wire rx_valid;
uart_rx receiver(.clk(CLOCK_50),.rst_n(rst_n),.rxd(UART_RXD),.rx_data(rx_data),.rx_valid(rx_valid),.rx_ready(1'b1));
reg [2:0] parse_state;reg [4:0] byte_count;reg [7:0] rx_check;reg [143:0] input_frame;reg sample_valid,encoding_error;
wire sample_ready,forecast_valid,direction_defined;
wire signed [17:0] temperature_out,pressure_out,humidity_out,wind_speed_out,direction_cos_out,direction_sin_out;
wire [17:0] wind_direction_out;
always @(posedge CLOCK_50) begin
 if(!rst_n)begin parse_state<=0;byte_count<=0;rx_check<=0;input_frame<=0;sample_valid<=0;encoding_error<=0;end
 else begin
 sample_valid<=0;
 if(rx_valid)case(parse_state)
 0:if(rx_data==8'haa)parse_state<=1;
 1:if(rx_data==8'h55)parse_state<=2;else if(rx_data!=8'haa)parse_state<=0;
 2:if(rx_data==8'h02)begin rx_check<=rx_data;parse_state<=3;end else parse_state<=0;
 3:if(rx_data==8'h12)begin rx_check<=rx_check^rx_data;byte_count<=0;encoding_error<=0;parse_state<=4;end else parse_state<=0;
 4:begin
   input_frame<={input_frame[135:0],rx_data};rx_check<=rx_check^rx_data;
   if((byte_count==0 || byte_count==3 || byte_count==6 || byte_count==9 || byte_count==12 || byte_count==15) && rx_data[7:2]!={6{rx_data[1]}})encoding_error<=1;
   if(byte_count==17)parse_state<=5;else byte_count<=byte_count+5'd1;
 end
 5:begin if(rx_data==rx_check && !encoding_error && sample_ready)sample_valid<=1;parse_state<=0;end
 default:parse_state<=0;
 endcase
 end
end
generate if(SHARED==0)begin:parallel_system
weather_system_speed predictor(.clk(CLOCK_50),.rst_n(rst_n),.sample_valid(sample_valid),.sample_ready(sample_ready),
.temperature_in(input_frame[137:120]),.pressure_in(input_frame[113:96]),.humidity_in(input_frame[89:72]),.wind_speed_in(input_frame[65:48]),.direction_cos_in(input_frame[41:24]),.direction_sin_in(input_frame[17:0]),
.forecast_valid(forecast_valid),.temperature_out(temperature_out),.pressure_out(pressure_out),.humidity_out(humidity_out),.wind_speed_out(wind_speed_out),.direction_cos_out(direction_cos_out),.direction_sin_out(direction_sin_out),.wind_direction_out(wind_direction_out),.direction_defined(direction_defined));
end else begin:shared_system
weather_system_resource predictor(.clk(CLOCK_50),.rst_n(rst_n),.sample_valid(sample_valid),.sample_ready(sample_ready),
.temperature_in(input_frame[137:120]),.pressure_in(input_frame[113:96]),.humidity_in(input_frame[89:72]),.wind_speed_in(input_frame[65:48]),.direction_cos_in(input_frame[41:24]),.direction_sin_in(input_frame[17:0]),
.forecast_valid(forecast_valid),.temperature_out(temperature_out),.pressure_out(pressure_out),.humidity_out(humidity_out),.wind_speed_out(wind_speed_out),.direction_cos_out(direction_cos_out),.direction_sin_out(direction_sin_out),.wind_direction_out(wind_direction_out),.direction_defined(direction_defined));
end endgenerate
wire [175:0] new_payload={{6{temperature_out[17]}},temperature_out,{6{pressure_out[17]}},pressure_out,{6{humidity_out[17]}},humidity_out,{6{wind_speed_out[17]}},wind_speed_out,{6{direction_cos_out[17]}},direction_cos_out,{6{direction_sin_out[17]}},direction_sin_out,6'd0,wind_direction_out,7'd0,direction_defined};
function [7:0] payload_checksum;input [175:0] data;integer j;begin payload_checksum=8'h82^8'h16;for(j=0;j<22;j=j+1)payload_checksum=payload_checksum^data[j*8+:8];end endfunction
reg busy;reg [4:0] tx_index;reg [175:0] saved_payload;reg [7:0] tx_check,tx_data;reg tx_valid;wire tx_ready;
uart_tx transmitter(.clk(CLOCK_50),.rst_n(rst_n),.tx_data(tx_data),.tx_valid(tx_valid),.tx_ready(tx_ready),.txd(UART_TXD));
always @(posedge CLOCK_50)begin
 if(!rst_n)begin busy<=0;tx_index<=0;saved_payload<=0;tx_check<=0;tx_data<=0;tx_valid<=0;end
 else begin
 tx_valid<=0;
 if(!busy)begin if(forecast_valid)begin saved_payload<=new_payload;tx_check<=payload_checksum(new_payload);tx_index<=0;busy<=1;end end
 else if(tx_ready && !tx_valid)begin
 tx_valid<=1;
 case(tx_index)
 0:tx_data<=8'haa;1:tx_data<=8'h55;2:tx_data<=8'h82;3:tx_data<=8'h16;
 26:tx_data<=tx_check;
 default:tx_data<=saved_payload[(25-tx_index)*8+:8];
 endcase
 if(tx_index==26)begin busy<=0;tx_index<=0;end else tx_index<=tx_index+5'd1;
 end
 end
end
endmodule
