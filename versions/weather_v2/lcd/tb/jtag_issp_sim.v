// Simulation stand-in for the ALTSOURCE_PROBE node: the testbench drives tb.host_source directly.
module jtag_issp(input clk, input [255:0] probe, output [127:0] source);
 assign source = tb.host_source;
endmodule
