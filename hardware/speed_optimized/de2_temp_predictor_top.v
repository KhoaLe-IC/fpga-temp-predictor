// -----------------------------------------------------------------------------
// de2_temp_predictor_top.v
//
// DE2 top-level wrapper.
//
// Board connections:
//   CLOCK_50 : DE2 50 MHz clock
//   KEY0_N   : active-low physical reset button
//   UART_RXD : PC -> FPGA
//   UART_TXD : FPGA -> PC
//
// Data path:
//   PC UART
//      -> uart_rx
//      -> packet_parser
//      -> temp_predictor_speed
//      -> packet_formatter
//      -> uart_tx
//      -> PC
//
// Host -> FPGA packet:
//   AA 55 01 02 TEMP_H TEMP_L CHK
//
// FPGA -> Host packet:
//   AA 55 81 02 FORECAST_H FORECAST_L CHK
//
// Temperature and forecast are signed Q8.8.
// Verilog-2001 compatible.
// -----------------------------------------------------------------------------
module de2_temp_predictor_top #(
    parameter COEF_FILE = "coeffs.txt",
    parameter CLK_FREQ  = 50000000,
    parameter BAUD_RATE = 115200
) (
    input  wire CLOCK_50,
    input  wire KEY0_N,
    input  wire UART_RXD,
    output wire UART_TXD,

    output wire [7:0] LEDR,
    output wire [6:0] HEX0,
    output wire [6:0] HEX1,
    output wire [6:0] HEX2,
    output wire [6:0] HEX3
);

    wire rst_n;

    wire [7:0] rx_data;
    wire       rx_valid;
    wire       rx_ready;

    wire signed [15:0] parsed_temp;
    wire               parsed_temp_valid;
    wire               predictor_ready;
    wire               packet_error;

    wire               forecast_valid;
    wire signed [15:0] forecast_out;

    wire [7:0] tx_data;
    wire       tx_valid;
    wire       tx_ready;

    // -----------------------------------------------------------------
    // Reset synchronizer
    // -----------------------------------------------------------------
    reset_sync u_reset_sync (
        .clk          (CLOCK_50),
        .reset_n_in   (KEY0_N),
        .reset_n_sync (rst_n)
    );

    // -----------------------------------------------------------------
    // UART receiver
    // Receiver can always accept a byte. Parser performs framing.
    // -----------------------------------------------------------------
    assign rx_ready = 1'b1;

    uart_rx #(
        .CLK_FREQ  (CLK_FREQ),
        .BAUD_RATE (BAUD_RATE)
    ) u_uart_rx (
        .clk       (CLOCK_50),
        .rst_n     (rst_n),
        .rxd       (UART_RXD),
        .rx_data   (rx_data),
        .rx_valid  (rx_valid),
        .rx_ready  (rx_ready)
    );

    // -----------------------------------------------------------------
    // Packet parser
    // -----------------------------------------------------------------
    packet_parser u_packet_parser (
        .clk         (CLOCK_50),
        .rst_n       (rst_n),
        .rx_data     (rx_data),
        .rx_valid    (rx_valid),
        .temp_out    (parsed_temp),
        .temp_valid  (parsed_temp_valid),
        .temp_ready  (predictor_ready),
        .packet_error(packet_error)
    );

    // -----------------------------------------------------------------
    // Predictor
    // -----------------------------------------------------------------
    temp_predictor_speed #(
        .COEF_FILE (COEF_FILE)
    ) u_predictor (
        .clk           (CLOCK_50),
        .rst_n         (rst_n),
        .sample_valid  (parsed_temp_valid),
        .sample_ready  (predictor_ready),
        .temp_in       (parsed_temp),
        .forecast_valid(forecast_valid),
        .forecast_out  (forecast_out)
    );

    // -----------------------------------------------------------------
    // Packet formatter
    // -----------------------------------------------------------------
    packet_formatter u_packet_formatter (
        .clk            (CLOCK_50),
        .rst_n           (rst_n),
        .forecast_valid (forecast_valid),
        .forecast_data  (forecast_out),
        .tx_data        (tx_data),
        .tx_valid       (tx_valid),
        .tx_ready       (tx_ready)
    );

    // -----------------------------------------------------------------
    // UART transmitter
    // -----------------------------------------------------------------
    uart_tx #(
        .CLK_FREQ  (CLK_FREQ),
        .BAUD_RATE (BAUD_RATE)
    ) u_uart_tx (
        .clk       (CLOCK_50),
        .rst_n     (rst_n),
        .tx_data   (tx_data),
        .tx_valid  (tx_valid),
        .tx_ready  (tx_ready),
        .txd       (UART_TXD)
    );

    // -----------------------------------------------------------------
    // Simple board debug outputs.
    // LED0 = packet error
    // LED1 = predictor output valid
    // LED2 = UART RX byte valid
    // LED3 = UART TX busy (= not ready)
    // LED4 = predictor ready
    // LED5 = parser has just produced a temperature sample
    // LED6/7 reserved
    // -----------------------------------------------------------------
    assign LEDR[0] = packet_error;
    assign LEDR[1] = forecast_valid;
    assign LEDR[2] = rx_valid;
    assign LEDR[3] = ~tx_ready;
    assign LEDR[4] = predictor_ready;
    assign LEDR[5] = parsed_temp_valid;
    assign LEDR[7:6] = 2'b00;

    // HEX displays forecast_out as a signed Q8.8 raw hexadecimal value.
    hex7seg u_hex0 (.hex(forecast_out[3:0]),   .seg(HEX0));
    hex7seg u_hex1 (.hex(forecast_out[7:4]),   .seg(HEX1));
    hex7seg u_hex2 (.hex(forecast_out[11:8]),  .seg(HEX2));
    hex7seg u_hex3 (.hex(forecast_out[15:12]), .seg(HEX3));

endmodule

// -----------------------------------------------------------------------------
// DE2 seven-segment decoder.
// DE2 HEX displays are active-low.
// -----------------------------------------------------------------------------
module hex7seg (
    input  wire [3:0] hex,
    output reg  [6:0] seg
);
    always @(*) begin
        case (hex)
            4'h0: seg = 7'b1000000;
            4'h1: seg = 7'b1111001;
            4'h2: seg = 7'b0100100;
            4'h3: seg = 7'b0110000;
            4'h4: seg = 7'b0011001;
            4'h5: seg = 7'b0010010;
            4'h6: seg = 7'b0000010;
            4'h7: seg = 7'b1111000;
            4'h8: seg = 7'b0000000;
            4'h9: seg = 7'b0010000;
            4'hA: seg = 7'b0001000;
            4'hB: seg = 7'b0000011;
            4'hC: seg = 7'b1000110;
            4'hD: seg = 7'b0100001;
            4'hE: seg = 7'b0000110;
            4'hF: seg = 7'b0001110;
            default: seg = 7'b1111111;
        endcase
    end
endmodule
