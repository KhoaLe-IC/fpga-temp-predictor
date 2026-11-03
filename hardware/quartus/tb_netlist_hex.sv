`timescale 1ns/1ps
// Same C++ vectors as the decimal bench, packed as {sample[15:0],valid,expected[15:0]}.
// This avoids simulator-specific signed-decimal file conversion behavior.
module tb_netlist_hex;
 reg clk=0;always #10 clk=~clk;
 reg rst_n=0,sample_valid=0;reg signed [15:0] temp_in=0;
 wire sample_ready,forecast_valid;wire signed [15:0] forecast_out;
 `DUT dut(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid),.sample_ready(sample_ready),.temp_in(temp_in),.forecast_valid(forecast_valid),.forecast_out(forecast_out));
 reg [32:0] vectors[0:4095];reg signed [15:0] queue[0:4095];integer n,wr=0,rd=0;string hexfile;
 always @(posedge clk)begin
 #8;
 if(rst_n && $isunknown(forecast_valid))$fatal(1,"Unknown valid");
 if(rst_n && forecast_valid===1)begin
 if(rd>=wr)$fatal(1,"Unexpected output");
 if(forecast_out!==queue[rd])$fatal(1,"Mismatch index=%0d got=%0d expected=%0d",rd,forecast_out,queue[rd]);
 rd=rd+1;
 end
 end
 initial begin
 if(!$value$plusargs("HEX=%s",hexfile))$fatal(1,"Missing HEX file");
 $readmemh(hexfile,vectors);
 repeat(5)@(negedge clk);rst_n=1;
 for(n=0;n<4096;n=n+1)begin
 if($isunknown(vectors[n]) || vectors[n][16]!=(n>=24))$fatal(1,"Malformed vector %0d",n);
 @(negedge clk);temp_in=vectors[n][32:17];sample_valid=1;
 while(sample_ready!==1)@(negedge clk);
 if(vectors[n][16])begin queue[wr]=vectors[n][15:0];wr=wr+1;end
 @(posedge clk);@(negedge clk);sample_valid=0;
 end
 repeat(30)@(negedge clk);
 if(rd!=4072 || rd!=wr)$fatal(1,"Missing results");
 $display("PASS HEX netlist 50 MHz: inputs=4096 forecasts=4072");$finish;
 end
 initial begin #5000000;$fatal(1,"Timeout");end
endmodule
