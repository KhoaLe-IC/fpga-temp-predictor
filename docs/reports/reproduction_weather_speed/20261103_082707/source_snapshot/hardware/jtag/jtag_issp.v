// Synthesis uses Quartus's ALTSOURCE_PROBE IP; no external JTAG pins are required.
module jtag_issp(input clk,input [255:0] probe,output [127:0] source);
 altsource_probe #(.probe_width(256),.source_width(128),
 .source_initial_value("0"),.enable_metastability("YES"),
 .sld_auto_instance_index("NO"),.sld_instance_index(0),.instance_id("FCST"))
 access_node(.probe(probe),.source(source),.source_clk(clk),.source_ena(1'b1));
endmodule
