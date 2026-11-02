// Clock-domain mailbox downstream of ALTSOURCE_PROBE's synchronized source.
// Host holds payload and request toggle until matching completion acknowledgement.
module jtag_mailbox #(parameter RESULT_WIDTH=16, parameter WEATHER=0, parameter SHARED=0)(
 input clk,input board_rst_n,input [127:0] source,
 output [255:0] probe,output core_rst_n,output sample_valid,
 output reg [107:0] sample_data,input sample_ready,input forecast_valid,
 input [RESULT_WIDTH-1:0] forecast_data,input direction_defined);
 reg ack;reg [2:0] state;reg [1:0] settle;
 reg [4:0] history_count;reg [15:0] accepted_count,forecast_count;
 reg [127:0] result;reg result_valid,result_defined;
 wire reset_active=!board_rst_n || source[1];
 assign core_rst_n=!reset_active;
 assign sample_valid=(state==2) && !reset_active;
 assign probe={32'h46504741,56'd0,(SHARED!=0),(WEATHER!=0),reset_active,
 sample_ready,result_defined,result_valid,(state!=0),ack,
 forecast_count,accepted_count,result};
 always @(posedge clk)begin
  if(reset_active)begin
   ack<=source[0];state<=0;settle<=0;sample_data<=0;history_count<=0;
   accepted_count<=0;forecast_count<=0;result<=0;result_valid<=0;result_defined<=0;
  end else case(state)
   0:if(source[0]!=ack)begin state<=1;settle<=0;end
   // Allow all synchronized payload bits to settle before taking one snapshot.
   1:if(settle==2)begin sample_data<=source[109:2];state<=2;end else settle<=settle+1'b1;
   2:if(sample_ready)begin
    accepted_count<=accepted_count+1'b1;
    if(history_count<24)begin history_count<=history_count+1'b1;ack<=source[0];state<=0;end
    else state<=3;
   end
   3:if(forecast_valid)begin
    result<={{(128-RESULT_WIDTH){1'b0}},forecast_data};
    result_valid<=1;result_defined<=direction_defined;
    forecast_count<=forecast_count+1'b1;ack<=source[0];state<=0;
   end
   default:state<=0;
  endcase
 end
endmodule
