`timescale 1ns/1ps
module tb_weather_netlist # (parameter LATENCY=40);
 reg clk=0;always #10 clk=~clk;
 reg rst_n=0,sample_valid=0;
 reg signed [17:0] inputs[0:5];wire signed [17:0] outputs[0:5];
 wire sample_ready,forecast_valid,direction_defined;wire [17:0] wind_direction_out;
 `DUT dut(.clk(clk),.rst_n(rst_n),.sample_valid(sample_valid),.sample_ready(sample_ready),
 .temperature_in(inputs[0]),.pressure_in(inputs[1]),.humidity_in(inputs[2]),.wind_speed_in(inputs[3]),.direction_cos_in(inputs[4]),.direction_sin_in(inputs[5]),
 .forecast_valid(forecast_valid),.temperature_out(outputs[0]),.pressure_out(outputs[1]),.humidity_out(outputs[2]),.wind_speed_out(outputs[3]),.direction_cos_out(outputs[4]),.direction_sin_out(outputs[5]),.wind_direction_out(wind_direction_out),.direction_defined(direction_defined));
 integer fd,stat,raw[0:5],exp[0:5],has,angle,n=0,wr=0,rd=0,cycle=0;
 integer q[0:4095][0:6],due[0:4095];real delta;
 string vectors;
 always @(posedge clk) begin
 cycle=cycle+1;
 #2;
 if(rst_n && forecast_valid===1)begin
 if(rd>=wr)$fatal(1,"Unexpected output");
 if(cycle!=due[rd])$fatal(1,"Wrong latency got=%0d expected=%0d",cycle,due[rd]);
 for(integer c=0;c<6;c++)if(outputs[c]!==q[rd][c])$fatal(1,"Mismatch channel=%0d got=%0d expected=%0d",c,outputs[c],q[rd][c]);
 if(q[rd][4]==0 && q[rd][5]==0)begin if(direction_defined!==0 || wind_direction_out!==0)$fatal(1,"Undefined vector");end
 else begin
 if(direction_defined!==1)$fatal(1,"Direction invalid");
 delta=real'(wind_direction_out)-real'(q[rd][6]);if(delta>46080)delta=delta-92160;if(delta< -46080)delta=delta+92160;
 if(delta>5 || delta< -5)$fatal(1,"Angle mismatch index=%0d got=%0d expected=%0d delta=%f cos=%0d sin=%0d",rd,wind_direction_out,q[rd][6],delta,outputs[4],outputs[5]);
 end
 rd=rd+1;
 end
 end
 initial begin
 for(integer c=0;c<6;c++)inputs[c]=0;
 if(!$value$plusargs("VECTORS=%s",vectors))$fatal(1,"Missing vectors");
 fd=$fopen(vectors,"r");if(!fd)$fatal(1,"Missing file");
 repeat(5)@(negedge clk);rst_n=1;
 while(!$feof(fd))begin
 stat=$fscanf(fd,"%d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",raw[0],raw[1],raw[2],raw[3],raw[4],raw[5],has,exp[0],exp[1],exp[2],exp[3],exp[4],exp[5],angle);
 if(stat!=14)$fatal(1,"Malformed vector");
 @(negedge clk);for(integer c=0;c<6;c++)inputs[c]=raw[c];sample_valid=1;
 while(sample_ready!==1)@(negedge clk);
 @(posedge clk); #0.001;
 if(has)begin for(integer c=0;c<6;c++)q[wr][c]=exp[c];q[wr][6]=angle;due[wr]=cycle+LATENCY;wr=wr+1;end
 @(negedge clk);sample_valid=0;n=n+1;
 end
 repeat(300)@(negedge clk);
 if(rd!=wr || rd==0)$fatal(1,"Missing outputs checked=%0d expected=%0d",rd,wr);
 $display("PASS weather netlist 50 MHz: inputs=%0d forecasts=%0d",n,rd);$finish;
 end
 initial begin #5000000;$fatal(1,"Timeout");end
endmodule
