// Power-up without any reset pulse (rst_n high from time 0): the driver must still wait >15 ms
// before its first E pulse and then show the text.
`timescale 1ns/1ps
module tb_powerup;
 reg clk = 0; always #10 clk = ~clk;
 wire [7:0] d; wire rs, en, rw, on, blon;
 reg [255:0] text = {"Weather +3h FPGA", "Send 25 frames  "};
 lcd_hd44780 dut(.clk(clk), .rst_n(1'b1), .text(text), .lcd_data(d), .lcd_rs(rs), .lcd_en(en), .lcd_rw(rw), .lcd_on(on), .lcd_blon(blon));
 realtime first = 0; reg [7:0] mem [0:127]; reg [6:0] a = 0; integer i, errors = 0;
 initial for (i = 0; i < 128; i = i + 1) mem[i] = 8'h20;
 always @(posedge en) if (first == 0) first = $realtime;
 always @(negedge en) if (first > 0) begin
  if (!rs) begin if (d[7]) a = d[6:0]; else if (d == 8'h01) a = 0; end else begin mem[a] = d; a = a + 1; end
 end
 initial begin
  #35_000_000;
  if (first < 15_000_000) begin errors = errors + 1; $display("ERROR first E pulse at %0t ns, before 15 ms", first); end
  for (i = 0; i < 16; i = i + 1) if (mem[i] !== text[255-8*i -: 8] || mem[64+i] !== text[127-8*i -: 8]) errors = errors + 1;
  if (errors == 0) $display("PASS power-up without reset: first E pulse at %0.1f ms, text shown", first / 1e6);
  else $display("FAIL power-up: %0d errors", errors);
  $finish;
 end
endmodule
