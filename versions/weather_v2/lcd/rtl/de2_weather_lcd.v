// DE2 top level: one host command sends a 25-frame window over JTAG; the LCD holds the single forecast.
// The verified JTAG mailbox and weather_system_speed core are reused unchanged. After a JTAG reset the
// mailbox treats frames 1-24 as history fill and frame 25 as the forecast request, so a 25-frame window
// yields exactly one forecast. This file only adds the LCD view of that result.
module de2_weather_lcd(
 input CLOCK_50, input KEY0_N,
 output [7:0] LCD_DATA, output LCD_RW, output LCD_EN, output LCD_RS, output LCD_ON, output LCD_BLON);

 wire board_rst_n, core_rst_n, sample_valid, sample_ready, forecast_valid, defined;
 wire [127:0] source; wire [255:0] probe; wire [107:0] sample_data;
 wire signed [17:0] t, p, h, w, c, s; wire [17:0] angle;

 reset_sync reset_unit(.clk(CLOCK_50), .reset_n_in(KEY0_N), .reset_n_sync(board_rst_n));
 jtag_issp access_unit(.clk(CLOCK_50), .probe(probe), .source(source));
 jtag_mailbox #(.RESULT_WIDTH(126), .WEATHER(1), .SHARED(0)) mailbox(
  .clk(CLOCK_50), .board_rst_n(board_rst_n), .source(source), .probe(probe),
  .core_rst_n(core_rst_n), .sample_valid(sample_valid), .sample_data(sample_data),
  .sample_ready(sample_ready), .forecast_valid(forecast_valid),
  .forecast_data({angle, s, c, w, h, p, t}), .direction_defined(defined));
 weather_system_speed predictor(
  .clk(CLOCK_50), .rst_n(core_rst_n), .sample_valid(sample_valid), .sample_ready(sample_ready),
  .temperature_in(sample_data[17:0]), .pressure_in(sample_data[35:18]), .humidity_in(sample_data[53:36]),
  .wind_speed_in(sample_data[71:54]), .direction_cos_in(sample_data[89:72]), .direction_sin_in(sample_data[107:90]),
  .forecast_valid(forecast_valid), .temperature_out(t), .pressure_out(p), .humidity_out(h), .wind_speed_out(w),
  .direction_cos_out(c), .direction_sin_out(s), .wind_direction_out(angle), .direction_defined(defined));

 // ---- LCD view: only the board button clears it; a JTAG reset for the next window does not ----
 wire [15:0] accepted  = probe[143:128];
 wire [15:0] forecasts = probe[159:144];
 reg [1:0] mode = 2'd0; reg [4:0] loaded = 5'd0; reg [15:0] seen = 16'd0;
 reg [125:0] shown = 126'd0; reg shown_defined = 1'b0;
 always @(posedge CLOCK_50) begin
  if (!board_rst_n) begin
   mode <= 0; loaded <= 0; seen <= 0; shown <= 0; shown_defined <= 0;
  end else if (forecasts != seen) begin
   seen <= forecasts;
   if (forecasts != 0) begin shown <= probe[125:0]; shown_defined <= probe[163]; mode <= 2; end
  end else if (accepted != 0 && forecasts == 0) begin
   mode <= 1; loaded <= (accepted > 25) ? 5'd25 : accepted[4:0];
  end
 end

 wire [255:0] text;
 weather_lcd_text formatter(.clk(CLOCK_50), .mode(mode), .loaded(loaded), .result(shown), .defined(shown_defined), .text(text));

 lcd_hd44780 lcd(.clk(CLOCK_50), .rst_n(board_rst_n), .text(text),
  .lcd_data(LCD_DATA), .lcd_rs(LCD_RS), .lcd_en(LCD_EN), .lcd_rw(LCD_RW), .lcd_on(LCD_ON), .lcd_blon(LCD_BLON));
endmodule
