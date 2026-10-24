`timescale 1ns/1ps
module tb_weather # (parameter LATENCY=40);
 reg clk=0;always #10 clk=~clk;
 reg rst_n=0,sample_valid=0;
 reg signed [17:0] inputs[0:5];wire signed [17:0] outputs[0:5];
 wire sample_ready,forecast_valid,direction_defined;wire [17:0] wind_direction_out;
 `DUT dut(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid),.sample_ready(sample_ready),
 .temperature_in(inputs[0]),.pressure_in(inputs[1]),.humidity_in(inputs[2]),.wind_speed_in(inputs[3]),.direction_cos_in(inputs[4]),.direction_sin_in(inputs[5]),
 .forecast_valid(forecast_valid),.temperature_out(outputs[0]),.pressure_out(outputs[1]),.humidity_out(outputs[2]),.wind_speed_out(outputs[3]),.direction_cos_out(outputs[4]),.direction_sin_out(outputs[5]),.wind_direction_out(wind_direction_out),.direction_defined(direction_defined));
 import "DPI-C" function chandle weather_create();
 import "DPI-C" function void weather_reset(input chandle p);
 import "DPI-C" function void weather_destroy(input chandle p);
 import "DPI-C" function int weather_push(input chandle p,input int a,b,c,d,e,f,output int oa,ob,oc,od,oe,of);
 chandle model;integer cycle=0,wr=0,rd=0,total=0,aborted=0,accepted=0,status;
 integer expected[0:4095][0:5];integer due[0:4095];integer value[0:5];
 real angle,delta;integer i,j,k,seed=12345,dummy;
 always @(posedge clk) begin
  cycle=cycle+1;
  if(!rst_n) begin weather_reset(model);aborted=aborted+wr-rd;wr=0;rd=0;end
  else if(sample_valid && sample_ready) begin
   accepted=accepted+1;
   status=weather_push(model,inputs[0],inputs[1],inputs[2],inputs[3],inputs[4],inputs[5],value[0],value[1],value[2],value[3],value[4],value[5]);
   if(status<0)$fatal(1,"Reference error");
   if(status==1) begin for(integer c=0;c<6;c++)expected[wr][c]=value[c];due[wr]=cycle+LATENCY;wr=wr+1;end
  end
  #2;
  if(!rst_n && forecast_valid!==0)$fatal(1,"Stale valid during reset");
  if(rst_n) begin
   if(forecast_valid===1) begin
    if(rd>=wr)$fatal(1,"Unexpected forecast");
    if(cycle!=due[rd])$fatal(1,"Latency got cycle %0d expected %0d",cycle,due[rd]);
    for(integer c=0;c<6;c++)if(outputs[c]!==expected[rd][c])$fatal(1,"Mismatch channel=%0d output=%0d expected=%0d",c,outputs[c],expected[rd][c]);
    if(expected[rd][4]==0 && expected[rd][5]==0)begin if(direction_defined!==0 || wind_direction_out!==0)$fatal(1,"Zero direction policy");end
    else begin
     if(direction_defined!==1)$fatal(1,"Missing direction");
     angle=$atan2(real'(expected[rd][5]),real'(expected[rd][4]))*180.0/3.141592653589793;
     if(angle<0)angle=angle+360.0;
     delta=real'(wind_direction_out)/256.0-angle;if(delta>180)delta=delta-360;if(delta< -180)delta=delta+360;
     if(delta>0.02 || delta< -0.02)$fatal(1,"Angle got=%f expected=%f",real'(wind_direction_out)/256.0,angle);
    end
    rd=rd+1;total=total+1;
   end
   if(rd<wr && cycle>=due[rd])$fatal(1,"Missing forecast");
  end
 end
 task reset_core;begin @(negedge clk);rst_n=0;sample_valid=1;repeat(4)@(negedge clk);rst_n=1;sample_valid=0;end endtask
 task send(input integer mode);begin
  @(negedge clk);
  for(integer c=0;c<6;c++)begin
   if(mode==0)inputs[c]=$urandom_range(0,262143)-131072;
   else if(mode==1)inputs[c]=c==0?7000:c==1?25700:c==2?22000:c==3?600:c==4?181:-181;
   else inputs[c]=k%2 ? 131071 : -131072;
  end
  sample_valid=1;
  do @(posedge clk);while(!sample_ready);
  @(negedge clk);sample_valid=0;
 end endtask
 initial begin
  model=weather_create();if(model==null)$fatal(1,"Model creation failed");
  dummy=$urandom(seed);for(j=0;j<6;j++)inputs[j]=0;
  reset_core();
  for(k=0;k<1200;k++)begin
   send(k<100?1:k<200?2:0);
   if(k%17==0)repeat(3)@(negedge clk);
   if(k==250 || k==700)reset_core();
  end
  repeat(300)@(negedge clk);
  if(rd!=wr || total<1000)$fatal(1,"Insufficient or incomplete checks");
  $display("PASS weather DPI-C: accepted=%0d checked=%0d reset_aborted=%0d latency=%0d",accepted,total,aborted,LATENCY);
  weather_destroy(model);$finish;
 end
 initial begin #10000000;$fatal(1,"Timeout");end
endmodule
