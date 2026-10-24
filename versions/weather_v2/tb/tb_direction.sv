`timescale 1ns/1ps
module tb_direction;
reg clk=0;always #10 clk=~clk;
reg rst_n=0,in_valid=0;reg signed [17:0] cos_in=0,sin_in=0;
wire out_valid,angle_defined;wire [17:0] angle_out;
wind_direction_cordic dut(.*);
integer x,y,checked=0;real expected,error,max_error=0;
initial begin
 repeat(4)@(negedge clk);rst_n=1;
 for(x=-256;x<=256;x++)for(y=-256;y<=256;y++)begin
 @(negedge clk);cos_in=x;sin_in=y;in_valid=1;
 @(negedge clk);in_valid=0;
 wait(out_valid);#1;
 if(x==0 && y==0)begin if(angle_defined!==0 || angle_out!==0)$fatal(1,"Zero vector");end
 else begin
 if(angle_defined!==1)$fatal(1,"Invalid direction");
 expected=$atan2(real'(y),real'(x))*180.0/3.141592653589793;if(expected<0)expected=expected+360;
 error=real'(angle_out)/256.0-expected;if(error>180)error=error-360;if(error< -180)error=error+360;
 if(error<0)error=-error;if(error>max_error)max_error=error;
 if(error>0.02)$fatal(1,"Angle error x=%0d y=%0d error=%f",x,y,error);
 end
 checked=checked+1;
 end
 $display("PASS exhaustive direction: vectors=%0d max_error_deg=%f",checked,max_error);$finish;
end
initial begin #200000000;$fatal(1,"Timeout");end
endmodule
