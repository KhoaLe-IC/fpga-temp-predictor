// Write-only HD44780 driver for the DE2 16x2 LCD (8-bit bus, RW tied low, fixed delays instead of busy polling).
// After power-up initialisation it rewrites both lines continuously from `text`, so the display always
// follows the latched text. Delays are generous versions of the HD44780 datasheet minimums.
module lcd_hd44780 #(parameter CLK_HZ = 50_000_000)(
 input clk, input rst_n,
 input [255:0] text,                       // line 1 in [255:128], leftmost character most significant
 output reg [7:0] lcd_data = 8'd0, output reg lcd_rs = 1'b0, output reg lcd_en = 1'b0,
 output lcd_rw, output lcd_on, output lcd_blon);

 localparam integer US      = CLK_HZ / 1_000_000;
 localparam integer T_POWER = 20000 * US;  // >15 ms after Vcc
 localparam integer T_FIRST = 5000 * US;   // >4.1 ms after the first function set
 localparam integer T_CLEAR = 2000 * US;   // >1.52 ms for clear display
 localparam integer T_CMD   = 100 * US;    // >37 us for other instructions and data writes
 localparam integer T_SETUP = US;          // RS/data set-up before E
 localparam integer T_PULSE = US;          // E high width (>450 ns)

 assign lcd_rw = 1'b0;
 assign lcd_on = 1'b1;
 assign lcd_blon = 1'b1;

 // steps 0-5: initialisation; 6: line-1 address, 7-22: line 1; 23: line-2 address, 24-39: line 2
 // Power-up values: LCD_ON powers the module when the FPGA is configured, so the 20 ms power-on
 // wait must also run straight after configuration, not only after a reset.
 reg [5:0] step = 6'd0;
 reg [1:0] phase = 2'd0;                   // 0 wait, 1 set-up, 2 E high
 reg [31:0] timer = T_POWER;
 reg [7:0] b;
 reg rs;
 reg [31:0] after;
 wire [4:0] col = (step >= 24) ? step - 6'd24 : step - 6'd7;
 wire [255:0] shifted = (step >= 24) ? text << (8 * (16 + col)) : text << (8 * col);

 always @* begin
  rs = 1'b0; after = T_CMD;
  case (step)
   6'd0: begin b = 8'h38; after = T_FIRST; end   // function set: 8-bit, 2 lines, 5x8
   6'd1: b = 8'h38;
   6'd2: b = 8'h38;
   6'd3: b = 8'h0C;                              // display on, cursor off
   6'd4: begin b = 8'h01; after = T_CLEAR; end   // clear
   6'd5: b = 8'h06;                              // entry mode: increment, no shift
   6'd6: b = 8'h80;                              // DDRAM address 0x00
   6'd23: b = 8'hC0;                             // DDRAM address 0x40
   default: begin b = shifted[255:248]; rs = 1'b1; end
  endcase
 end

 always @(posedge clk) begin
  if (!rst_n) begin
   step <= 0; phase <= 0; timer <= T_POWER;
   lcd_en <= 0; lcd_rs <= 0; lcd_data <= 0;
  end else if (timer != 0) begin
   timer <= timer - 1;
  end else case (phase)
   2'd0: begin lcd_rs <= rs; lcd_data <= b; lcd_en <= 0; timer <= T_SETUP; phase <= 1; end
   2'd1: begin lcd_en <= 1; timer <= T_PULSE; phase <= 2; end
   default: begin
    lcd_en <= 0; timer <= after; phase <= 0;
    step <= (step == 6'd39) ? 6'd6 : step + 6'd1;
   end
  endcase
 end
endmodule
