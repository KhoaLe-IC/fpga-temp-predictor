// 16x2 LCD text for the window variant. Two register stages (scale, then BCD/text) keep the
// x100 scaling and the binary-to-BCD conversion in separate clock cycles; the latched inputs change
// only once per forecast, so the 2-cycle delay is invisible on the display.
// text[255:128] = line 1, text[127:0] = line 2, leftmost character in the most significant byte.
//   idle    : "Weather +3h FPGA" / "Send 25 frames  "
//   loading : "Receiving window" / "Frame nn of 25  "
//   result  : "T+dd.dC Pddd.dd " / "Hddd% Wdd.d Dddd"   (leading zeros shown as spaces)
// Rounding matches lcd_reference.py: value = (|q8| * scale + 128) >> 8.
module weather_lcd_text(
 input clk,
 input [1:0] mode,                 // 0 idle, 1 loading, 2 result
 input [4:0] loaded,               // frames received so far (loading)
 input [125:0] result,             // {angle, sin, cos, wind, humidity, pressure, temperature}, 18 bits each
 input defined,                    // direction defined flag
 output reg [255:0] text);

 // binary (up to 17 bits) -> five BCD digits, double dabble
 function [19:0] bcd5;
  input [16:0] v;
  integer i;
  reg [36:0] s;
  begin
   s = {20'd0, v};
   for (i = 0; i < 17; i = i + 1) begin
    if (s[20:17] > 4) s[20:17] = s[20:17] + 3;
    if (s[24:21] > 4) s[24:21] = s[24:21] + 3;
    if (s[28:25] > 4) s[28:25] = s[28:25] + 3;
    if (s[32:29] > 4) s[32:29] = s[32:29] + 3;
    if (s[36:33] > 4) s[36:33] = s[36:33] + 3;
    s = s << 1;
   end
   bcd5 = s[36:17];
  end
 endfunction

 function [7:0] dig;        // BCD digit -> ASCII
  input [3:0] d;
  dig = 8'h30 + d;
 endfunction

 function [7:0] lead;       // digit, or space when it is a leading zero
  input [3:0] d;
  input blank;
  lead = blank ? 8'h20 : 8'h30 + d;
 endfunction

 wire signed [17:0] t = result[17:0], p = result[35:18], h = result[53:36], w = result[71:54];
 wire [17:0] angle = result[125:108];

 // magnitudes (negative pressure/humidity/wind cannot occur after the lane limits; shown as zero)
 wire [18:0] t_mag = t[17] ? -{t[17], t} : {1'b0, t};
 wire [17:0] p_mag = p[17] ? 18'd0 : p;
 wire [17:0] h_mag = h[17] ? 18'd0 : h;
 wire [17:0] w_mag = w[17] ? 18'd0 : w;

 wire [22:0] t_x10  = t_mag * 4'd10 + 23'd128;
 wire [24:0] p_x100 = p_mag * 7'd100 + 25'd128;
 wire [17:0] h_r    = h_mag + 18'd128;
 wire [21:0] w_x10  = w_mag * 4'd10 + 22'd128;
 wire [18:0] a_r    = angle + 19'd128;

 wire [14:0] t10_raw = t_x10[22:8];
 wire [13:0] w10_raw = w_x10[21:8];
 wire [10:0] deg_raw = a_r[18:8];

 // stage 1: scaled integers
 reg [9:0] t10, hp, w10; reg [16:0] p100; reg [8:0] deg; reg t_neg, def_r; reg [1:0] mode_r; reg [4:0] loaded_r;
 always @(posedge clk) begin
  t10  <= (t10_raw > 999) ? 10'd999 : t10_raw[9:0];
  p100 <= p_x100[24:8];
  hp   <= h_r[17:8];
  w10  <= (w10_raw > 999) ? 10'd999 : w10_raw[9:0];
  deg  <= (deg_raw >= 360) ? 9'd0 : deg_raw[8:0];
  t_neg <= t[17]; def_r <= defined; mode_r <= mode; loaded_r <= loaded;
 end

 wire [19:0] tb = bcd5({7'd0, t10});
 wire [19:0] pb = bcd5(p100);
 wire [19:0] hb = bcd5({7'd0, hp});
 wire [19:0] wb = bcd5({7'd0, w10});
 wire [19:0] db = bcd5({8'd0, deg});
 wire [19:0] nb = bcd5({12'd0, loaded_r});

 // stage 2: BCD digits -> ASCII text
 always @(posedge clk) begin
  case (mode_r)
   2'd0: text <= {"Weather +3h FPGA", "Send 25 frames  "};
   2'd1: text <= {"Receiving window", "Frame ", dig(nb[7:4]), dig(nb[3:0]), " of 25  "};
   default: text <= {
    "T", (t_neg ? "-" : "+"), lead(tb[11:8], tb[11:8] == 0), dig(tb[7:4]), ".", dig(tb[3:0]), "C",
    " P", lead(pb[19:16], pb[19:16] == 0), lead(pb[15:12], pb[19:12] == 0), dig(pb[11:8]), ".", dig(pb[7:4]), dig(pb[3:0]), " ",
    "H", lead(hb[11:8], hb[11:8] == 0), lead(hb[7:4], hb[11:4] == 0), dig(hb[3:0]), "%",
    " W", lead(wb[11:8], wb[11:8] == 0), dig(wb[7:4]), ".", dig(wb[3:0]),
    " D", (def_r ? {lead(db[11:8], db[11:8] == 0), lead(db[7:4], db[11:4] == 0), dig(db[3:0])} : "---")};
  endcase
 end
endmodule
