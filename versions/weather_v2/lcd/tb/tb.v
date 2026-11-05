// End-to-end check of de2_weather_lcd at the real 50 MHz clock:
// host protocol over the JTAG mailbox (stubbed ISSP) -> predictor -> latched view -> HD44780 bus.
// An HD44780 model rebuilds the display from LCD_EN/RS/DATA and checks E width and busy times.
// Vectors and expected text come from host/lcd_reference.py (fixed-point golden model).
`timescale 1ns/1ps
module tb;
 reg clk = 0; always #10 clk = ~clk;
 reg key_n = 0;
 reg [127:0] host_source = 0;
 wire [7:0] lcd_d; wire lcd_rw, lcd_en, lcd_rs, lcd_on, lcd_blon;
 de2_weather_lcd dut(.CLOCK_50(clk), .KEY0_N(key_n), .LCD_DATA(lcd_d), .LCD_RW(lcd_rw), .LCD_EN(lcd_en),
  .LCD_RS(lcd_rs), .LCD_ON(lcd_on), .LCD_BLON(lcd_blon));

 integer errors = 0, i;

 // ---------------- HD44780 model ----------------
 reg [7:0] ddram [0:127]; reg [6:0] addr = 0;
 realtime busy_until = 0, en_rise = 0;
 integer writes = 0;
 initial for (i = 0; i < 128; i = i + 1) ddram[i] = 8'h20;
 always @(posedge lcd_en) begin
  en_rise = $realtime;
  if ($realtime < busy_until) begin errors = errors + 1; $display("ERROR LCD written while busy at %0t", $realtime); end
 end
 always @(negedge lcd_en) if (en_rise > 0) begin   // ignore the power-on X->0 transition
  if ($realtime - en_rise < 450.0) begin errors = errors + 1; $display("ERROR E pulse too short at %0t", $realtime); end
  if (lcd_rw !== 1'b0) begin errors = errors + 1; $display("ERROR RW not low"); end
  writes = writes + 1;
  if (!lcd_rs) begin
   if (lcd_d[7]) begin addr = lcd_d[6:0]; busy_until = $realtime + 37_000; end
   else if (lcd_d == 8'h01) begin for (i = 0; i < 128; i = i + 1) ddram[i] = 8'h20; addr = 0; busy_until = $realtime + 1_520_000; end
   else if (lcd_d == 8'h38 && writes == 1) busy_until = $realtime + 4_100_000;
   else busy_until = $realtime + 37_000;
  end else begin
   ddram[addr] = lcd_d; addr = addr + 1; busy_until = $realtime + 41_000;
  end
 end
 function [255:0] screen; input dummy; integer k; begin
  for (k = 0; k < 16; k = k + 1) begin screen[255 - 8*k -: 8] = ddram[k]; screen[127 - 8*k -: 8] = ddram[64 + k]; end
 end endfunction
 task check_screen(input [255:0] want, input [8*24-1:0] what); begin
  if (screen(0) !== want) begin
   errors = errors + 1;
   $display("ERROR %0s: LCD |%s|%s|  expected |%s|%s|", what, screen(0) >> 128, screen(0) & {128{1'b1}}, want >> 128, want & {128{1'b1}});
  end else $display("ok   %-22s |%s|%s|", what, want[255:128], want[127:0]);
 end endtask

 // ---------------- host side ----------------
 reg toggle = 0;
 task cycles(input integer n); repeat (n) @(posedge clk); endtask
 task ms(input integer n); integer k; for (k = 0; k < n; k = k + 1) cycles(50_000); endtask
 task jtag_reset; begin
  host_source = 128'd2; cycles(20);
  if (!dut.probe[165]) begin errors = errors + 1; $display("ERROR reset not seen"); end
  host_source = 128'd0; toggle = 0; cycles(20);
 end endtask
 task send_frame(input [107:0] payload); integer k; begin
  host_source = {18'd0, payload, 1'b0, toggle}; cycles(5);   // stage with the old request bit
  toggle = ~toggle; host_source[0] = toggle;                  // commit
  k = 0;
  while (dut.probe[160] !== toggle && k < 2000) begin cycles(1); k = k + 1; end
  if (k == 2000) begin errors = errors + 1; $display("ERROR no acknowledgement"); end
  cycles(3);
 end endtask

 // ---------------- vectors ----------------
 integer fd, nwin, w, r;
 reg [107:0] payload [0:24];
 reg [127:0] expected; integer exp_defined; reg [255:0] exp_text, exp_text_prev;
 task read_window; integer k; begin
  for (k = 0; k < 25; k = k + 1) r = $fscanf(fd, "%h\n", payload[k]);
  r = $fscanf(fd, "%h %d\n", expected, exp_defined);
  r = $fscanf(fd, "%h\n", exp_text);
 end endtask
 task check_result(input integer n); begin
  if (dut.probe[159:144] !== 16'd1 || dut.probe[143:128] !== 16'd25) begin
   errors = errors + 1; $display("ERROR window %0d: accepted=%0d forecasts=%0d", n, dut.probe[143:128], dut.probe[159:144]);
  end
  if (dut.probe[125:0] !== expected[125:0] || dut.probe[163] !== exp_defined[0]) begin
   errors = errors + 1; $display("ERROR window %0d: forecast %h expected %h", n, dut.probe[125:0], expected[125:0]);
  end else $display("ok   window %0d: forecast word matches fixed-point reference", n);
 end endtask

 initial begin
  fd = $fopen("vectors.txt", "r");
  if (fd == 0) begin $display("ERROR missing vectors.txt"); $finish; end
  r = $fscanf(fd, "%d\n", nwin);
  cycles(100); key_n = 1;
  ms(33);
  check_screen({"Weather +3h FPGA", "Send 25 frames  "}, "after power-up");
  for (w = 0; w < nwin; w = w + 1) begin
   read_window;
   jtag_reset;
   if (w > 0) begin ms(5); check_screen(exp_text_prev, "held after JTAG reset"); end
   for (i = 0; i < 10; i = i + 1) send_frame(payload[i]);
   ms(5);
   check_screen({"Receiving window", "Frame 10 of 25  "}, "while loading");
   for (i = 10; i < 25; i = i + 1) send_frame(payload[i]);
   check_result(w);
   ms(5);
   check_screen(exp_text, "forecast shown");
   ms(10);
   check_screen(exp_text, "forecast still held");
   exp_text_prev = exp_text;
  end
  key_n = 0; cycles(100); key_n = 1; ms(33);
  check_screen({"Weather +3h FPGA", "Send 25 frames  "}, "after KEY0");
  if (errors == 0) $display("PASS LCD window variant: %0d windows, %0d LCD bus writes checked", nwin, writes);
  else $display("FAIL LCD window variant: %0d errors", errors);
  $finish;
 end
endmodule
