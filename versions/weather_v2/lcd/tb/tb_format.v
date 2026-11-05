// Unit test: weather_lcd_text result mode against lcd_reference.py on edge and random values.
module tb_format;
 reg [125:0] r; reg d; wire [255:0] text; reg [255:0] want; reg [127:0] word;
 integer fd, n, k, e, errors = 0, x;
 reg clk = 0; always #1 clk = ~clk;
 weather_lcd_text dut(.clk(clk), .mode(2'd2), .loaded(5'd0), .result(r), .defined(d), .text(text));
 initial begin
  fd = $fopen("format_cases.txt", "r"); x = $fscanf(fd, "%d\n", n);
  for (k = 0; k < n; k = k + 1) begin
   x = $fscanf(fd, "%h %d %h\n", word, e, want); r = word[125:0]; d = e[0]; repeat (3) @(posedge clk); #0.5;
   if (text !== want) begin errors = errors + 1; if (errors < 6) $display("ERROR case %0d: |%s|%s| want |%s|%s|", k, text[255:128], text[127:0], want[255:128], want[127:0]); end
  end
  if (errors == 0) $display("PASS formatter: %0d cases match lcd_reference.py", n); else $display("FAIL formatter: %0d of %0d", errors, n);
  $finish;
 end
endmodule
