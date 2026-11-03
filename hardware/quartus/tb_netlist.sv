`timescale 1ns/1ps
// Four-state replay of the trained temperature netlist at 50 MHz.
module tb_netlist #(parameter A_Q=12214,B_Q=150,C_Q=0);
 reg clk=0;always #10 clk=~clk;
 reg rst_n=0,sample_valid=0;reg signed [15:0] temp_in=0;
 wire sample_ready,forecast_valid;wire signed [15:0] forecast_out;
 `DUT dut(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid),.sample_ready(sample_ready),.temp_in(temp_in),.forecast_valid(forecast_valid),.forecast_out(forecast_out));
 integer fd,status,raw,valid,expected,n=0,checked=0,chars;
 reg signed [15:0] queue[0:8191];integer wr=0,rd=0;
 reg [1023:0] line;reg [1031:0] padded_line;string vectors;
 // Parse one complete record at a time. Malformed records always fail;
 // no simulator may silently skip a record after a failed conversion.
 task read_vector;begin
  chars=$fgets(line,fd);
  padded_line={line,8'h20};
  if(chars==0)status=0;else status=$sscanf(padded_line,"%d %d %d",raw,valid,expected);
 end endtask
 always @(posedge clk)begin
  #2;
  if(rst_n && $isunknown(forecast_valid))$fatal(1,"Unknown forecast_valid");
  if(rst_n && forecast_valid===1'b1)begin
   if(rd>=wr)$fatal(1,"Unexpected output");
   if(forecast_out!==queue[rd])$fatal(1,"Mismatch index=%0d got=%0d expected=%0d",rd,forecast_out,queue[rd]);
   rd=rd+1;checked=checked+1;
  end
 end
 initial begin
  if(!$value$plusargs("VECTORS=%s",vectors))$fatal(1,"Missing vectors");
  fd=$fopen(vectors,"r");if(!fd)$fatal(1,"Cannot open vectors");
  read_vector();
  if(status!=3 || raw!=A_Q || valid!=B_Q || expected!=C_Q)$fatal(1,"Coefficient header mismatch");
  repeat(5)@(negedge clk);rst_n=1;
  read_vector();
  while(chars>0)begin
   if(status!=3 || (valid!=0 && valid!=1) || valid!=(n>=24) || raw< -32768 || raw>32767 || expected< -32768 || expected>32767)$fatal(1,"Malformed vector row %0d",n);
   @(negedge clk);sample_valid=1;temp_in=raw;
   while(sample_ready!==1'b1)@(negedge clk);
   if(valid)begin if(wr>=8192)$fatal(1,"Queue overflow");queue[wr]=expected;wr=wr+1;end
   @(posedge clk);@(negedge clk);sample_valid=0;n=n+1;
   read_vector();
  end
  repeat(30)@(negedge clk);
  if(checked!=wr || checked!=n-24 || checked==0)$fatal(1,"Missing outputs checked=%0d expected=%0d",checked,wr);
  $display("PASS netlist at 50 MHz: inputs=%0d forecasts=%0d",n,checked);$finish;
 end
 initial begin #5000000;$fatal(1,"Timeout");end
endmodule
