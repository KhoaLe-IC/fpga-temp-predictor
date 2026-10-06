// -----------------------------------------------------------------------------
// uart_tx.v
// 8-N-1 UART transmitter, LSB first.
// Default: 50 MHz clock, 115200 baud.
// tx_ready is high when a new byte can be accepted.
// tx_valid is sampled on a rising edge when tx_ready is high.
// Verilog-2001 compatible.
// -----------------------------------------------------------------------------
module uart_tx #(
    parameter CLK_FREQ  = 50000000,
    parameter BAUD_RATE = 115200
) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] tx_data,
    input  wire       tx_valid,
    output wire       tx_ready,
    output reg        txd
);

    localparam integer BAUD_DIV = CLK_FREQ / BAUD_RATE;

    reg busy;
    reg [15:0] baud_cnt;
    reg [3:0]  bit_cnt;
    reg [9:0]  shift_reg;

    assign tx_ready = ~busy;

    always @(posedge clk) begin
        if (!rst_n) begin
            busy      <= 1'b0;
            baud_cnt  <= 16'd0;
            bit_cnt   <= 4'd0;
            shift_reg <= 10'b1111111111;
            txd       <= 1'b1;
        end else begin
            if (!busy) begin
                txd <= 1'b1;

                if (tx_valid) begin
                    // {stop, data[7:0], start}; transmitted from bit 0 upward.
                    shift_reg <= {1'b1, tx_data, 1'b0};
                    busy      <= 1'b1;
                    baud_cnt  <= BAUD_DIV - 1;
                    bit_cnt   <= 4'd0;
                    txd       <= 1'b0;
                end
            end else begin
                if (baud_cnt != 0) begin
                    baud_cnt <= baud_cnt - 16'd1;
                end else begin
                    baud_cnt <= BAUD_DIV - 1;

                    if (bit_cnt == 4'd9) begin
                        busy <= 1'b0;
                        txd  <= 1'b1;
                    end else begin
                        bit_cnt <= bit_cnt + 4'd1;
                        txd <= shift_reg[bit_cnt + 4'd1];
                    end
                end
            end
        end
    end
endmodule
