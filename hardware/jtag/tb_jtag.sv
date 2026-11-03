`timescale 1ns/1ps
// Only the vendor scan transport is mocked. Mailbox and production predictors are real RTL.
module jtag_issp(input clk,input [255:0] probe,output [127:0] source);
 reg [127:0] source_reg=0;assign source=source_reg;
endmodule
module tb_jtag #(parameter WEATHER=0,SHARED=0);
 reg clk=0;always #10 clk=~clk;reg key=0;
 `DUT dut(.CLOCK_50(clk),.KEY0_N(key));
 integer fd,status,n=0,forecasts=0;reg [127:0] stage,commit;reg [255:0] probe;
 integer expected_count,expected_fc;reg [127:0] expected_result;string vectors;
 task read_probe;begin #1;probe=dut.access_unit.probe;end endtask
 task reset_mailbox;begin
  @(negedge clk);dut.access_unit.source_reg=128'd2;
  repeat(12)@(negedge clk);read_probe();
  if(probe[165]!==1 || probe[159:128]!==0)$fatal(1,"Reset not visible");
  dut.access_unit.source_reg=0;repeat(12)@(negedge clk);read_probe();
  if(probe[165]!==0 || probe[160]!==0 || probe[255:224]!==32'h46504741)$fatal(1,"Reset/magic failure");
 end endtask
 task submit;integer timeout,delta;begin
  // Payload precedes request; non-clock-aligned transport update.
  #3;dut.access_unit.source_reg=stage;repeat(4)@(negedge clk);
  #7;dut.access_unit.source_reg=commit;timeout=0;read_probe();
  while(probe[160]!==commit[0] || probe[161]!==0)begin
   @(negedge clk);read_probe();timeout=timeout+1;if(timeout>600)$fatal(1,"Mailbox timeout");
  end
  if(probe[143:128]!==16'(expected_count) || probe[159:144]!==16'(expected_fc))$fatal(1,"Counter mismatch");
  if(probe[166]!==1'(WEATHER) || probe[167]!==1'(SHARED))$fatal(1,"Wrong variant flags");
  if(expected_fc>0)begin
   if(probe[162]!==1)$fatal(1,"Missing result flag");
   if(WEATHER)begin
    if(probe[107:0]!==expected_result[107:0])$fatal(1,"Weather scalar mismatch");
    if(probe[163]!==((expected_result[89:72]!=0)||(expected_result[107:90]!=0)))$fatal(1,"Defined flag");
    delta=int'(probe[125:108])-int'(expected_result[125:108]);
    if(delta>46080)delta-=92160;if(delta< -46080)delta+=92160;
    if(delta>5 || delta< -5)$fatal(1,"Angle mismatch");
   end else if(probe[15:0]!==expected_result[15:0])$fatal(1,"Temperature mismatch");
  end else if(probe[162]!==0)$fatal(1,"Forecast during warmup");
  // Holding the request must not create duplicate observations.
  repeat(5)@(negedge clk);read_probe();
  if(probe[143:128]!==16'(expected_count))$fatal(1,"Duplicate request accepted");
 end endtask
 initial begin
  if(!$value$plusargs("VECTORS=%s",vectors))$fatal(1,"Missing vectors");
  repeat(6)@(negedge clk);key=1;repeat(6)@(negedge clk);reset_mailbox();
  fd=$fopen(vectors,"r");if(!fd)$fatal(1,"Missing vector file");
  while(!$feof(fd))begin
   status=$fscanf(fd,"%h %h %d %d %h\n",stage,commit,expected_count,expected_fc,expected_result);
   if(status!=5)$fatal(1,"Malformed vector");submit();n++;
  end
  if(n!=128 || expected_fc!=104)$fatal(1,"Incomplete replay");
  // A request held across a reset is consumed by reset, not replayed afterward.
  stage=128'd0;commit=128'd1;#3;dut.access_unit.source_reg=commit;
  repeat(5)@(negedge clk);dut.access_unit.source_reg=128'd3;
  repeat(8)@(negedge clk);dut.access_unit.source_reg=128'd1;
  repeat(200)@(negedge clk);read_probe();
  if(probe[159:128]!==0 || probe[162]!==0 || probe[160]!==1)$fatal(1,"Reset cancellation/held toggle failed");
  reset_mailbox();
  $fclose(fd);fd=$fopen(vectors,"r");
  // Fresh warmup after reset must reproduce the first forecast.
  for(integer i=0;i<25;i++)begin
   status=$fscanf(fd,"%h %h %d %d %h\n",stage,commit,expected_count,expected_fc,expected_result);
   if(status!=5)$fatal(1,"Missing reset replay");submit();
  end
  $display("PASS JTAG mailbox: weather=%0d shared=%0d inputs=128 forecasts=104 reset_replay=25",WEATHER,SHARED);$finish;
 end
 initial begin #2000000;$fatal(1,"Timeout");end
endmodule
