`timescale 1ns/1ps
module tb_weather_uart #(parameter SHARED=0);
reg CLOCK_50=0;always #10 CLOCK_50=~CLOCK_50;
reg KEY0_N=0,UART_RXD=1;wire UART_TXD;
de2_weather_uart #(.SHARED(SHARED)) dut(.*);
localparam BAUD_CLKS=50000000/115200;
integer fd,status,raw[0:5],expected[0:5],has,angle,i,checked=0;reg corrupt=0;
task send_byte(input [7:0] data);begin
 UART_RXD=0;repeat(BAUD_CLKS)@(negedge CLOCK_50);
 for(integer k=0;k<8;k++)begin UART_RXD=data[k];repeat(BAUD_CLKS)@(negedge CLOCK_50);end
 UART_RXD=1;repeat(BAUD_CLKS)@(negedge CLOCK_50);
end endtask
task send_frame;reg [7:0] check;begin
 @(negedge CLOCK_50);check=8'h02^8'h12;
 send_byte(8'haa);send_byte(8'h55);send_byte(8'h02);send_byte(8'h12);
 for(integer c=0;c<6;c++)begin
 send_byte(raw[c][23:16]);send_byte(raw[c][15:8]);send_byte(raw[c][7:0]);check=check^raw[c][23:16]^raw[c][15:8]^raw[c][7:0];
 end
 send_byte(corrupt ? check^8'h01 : check);
end endtask
task receive_byte(output [7:0] data);begin
 @(negedge UART_TXD);repeat(BAUD_CLKS/2)@(posedge CLOCK_50);
 if(UART_TXD!==0)$fatal(1,"Start bit");repeat(BAUD_CLKS)@(posedge CLOCK_50);
 for(integer k=0;k<8;k++)begin data[k]=UART_TXD;repeat(BAUD_CLKS)@(posedge CLOCK_50);end
 if(UART_TXD!==1)$fatal(1,"Stop bit");
end endtask
task receive_frame;reg [7:0] bytes[0:26];reg [7:0] checksum;integer received;real delta;begin
 for(integer k=0;k<27;k++)receive_byte(bytes[k]);
 if(bytes[0]!==8'haa||bytes[1]!==8'h55||bytes[2]!==8'h82||bytes[3]!==8'h16)$fatal(1,"Response header");
 checksum=0;for(integer k=2;k<26;k++)checksum=checksum^bytes[k];if(bytes[26]!==checksum)$fatal(1,"Checksum");
 for(integer c=0;c<6;c++)begin received=$signed({bytes[4+c*3],bytes[5+c*3],bytes[6+c*3]});if(received!==expected[c])$fatal(1,"UART channel %0d got=%0d expected=%0d",c,received,expected[c]);end
 received={bytes[22],bytes[23],bytes[24]};
 if(expected[4]==0 && expected[5]==0)begin if(bytes[25]!==0||received!=0)$fatal(1,"Undefined direction");end
 else begin if(bytes[25]!==1)$fatal(1,"Direction flag");delta=real'(received-angle);if(delta>46080)delta=delta-92160;if(delta< -46080)delta=delta+92160;if(delta>5||delta< -5)$fatal(1,"UART direction mismatch");end
 checked=checked+1;
end endtask
initial begin
 fd=$fopen("vectors.txt","r");if(!fd)$fatal(1,"No vectors");
 repeat(20)@(negedge CLOCK_50);KEY0_N=1;repeat(10)@(negedge CLOCK_50);
 // A corrupt request must not count toward warm-up.
 for(integer c=0;c<6;c++)raw[c]=0;corrupt=1;send_frame();corrupt=0;
 for(i=0;i<32;i++)begin
 status=$fscanf(fd,"%d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",raw[0],raw[1],raw[2],raw[3],raw[4],raw[5],has,expected[0],expected[1],expected[2],expected[3],expected[4],expected[5],angle);
 if(status!=14)$fatal(1,"Malformed vectors");
 if(has)begin fork send_frame();receive_frame();join end else send_frame();
 repeat(1000)@(negedge CLOCK_50);
end
if(checked!=8)$fatal(1,"Wrong reply count");
$display("PASS weather UART 50 MHz / 115200 baud: architecture=%0d frames=32 checked=8 bad-checksum rejected",SHARED);$finish;
end
initial begin #200000000;$fatal(1,"UART timeout");end
endmodule
