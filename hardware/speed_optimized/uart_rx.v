// -----------------------------------------------------------------------------
// uart_rx.v
// 8-N-1 UART receiver, LSB first.
// Default: 50 MHz clock, 115200 baud.
// One-cycle rx_valid pulse is generated for every received byte.
// rx_ready is provided so the user logic can throttle the receiver.
// Verilog-2001 compatible.
// -----------------------------------------------------------------------------
module uart_rx #(
    parameter CLK_FREQ  = 50000000,
    parameter BAUD_RATE = 115200
) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       rxd,
    output reg [7:0]  rx_data,
    output reg        rx_valid,
    input  wire       rx_ready
);

    localparam integer BAUD_DIV = CLK_FREQ / BAUD_RATE;
    localparam integer HALF_DIV = BAUD_DIV / 2;

    reg rxd_ff1;
    reg rxd_ff2;
    reg busy;
    reg [15:0] baud_cnt;
    reg [3:0]  bit_cnt;
    reg [7:0]  shift_reg;

    always @(posedge clk) begin
        if (!rst_n) begin
            rxd_ff1  <= 1'b1;
            rxd_ff2  <= 1'b1;
            busy     <= 1'b0;
            baud_cnt <= 16'd0;
            bit_cnt  <= 4'd0;
            shift_reg <= 8'd0;
            rx_data  <= 8'd0;
            rx_valid <= 1'b0;
        end else begin
            rxd_ff1  <= rxd;
            rxd_ff2  <= rxd_ff1;
            rx_valid <= 1'b0;

            if (!busy) begin
                baud_cnt <= 16'd0;
                bit_cnt  <= 4'd0;

                if (rxd_ff2 == 1'b0) begin
                    // Start bit detected. Wait half a bit and confirm it.
                    busy     <= 1'b1;
                    baud_cnt <= HALF_DIV - 1;
                    bit_cnt  <= 4'd0;
                end
            end else begin
                if (baud_cnt != 0) begin
                    baud_cnt <= baud_cnt - 16'd1;
                end else begin
                    baud_cnt <= BAUD_DIV - 1;

                    if (bit_cnt == 4'd0) begin
                        // Confirm start bit.
                        if (rxd_ff2 != 1'b0) begin
                            busy <= 1'b0;
                        end else begin
                            bit_cnt <= 4'd1;
                        end
                    end else if (bit_cnt <= 4'd8) begin
                        // Data bits, LSB first.
                        shift_reg[bit_cnt-1] <= rxd_ff2;
                        bit_cnt <= bit_cnt + 4'd1;
                    end else begin
                        // Stop bit.
                        busy <= 1'b0;
                        if (rxd_ff2 == 1'b1 && rx_ready) begin
                            rx_data  <= shift_reg;
                            rx_valid <= 1'b1;
                        end
                    end
                end
            end
        end
    end
endmodule
