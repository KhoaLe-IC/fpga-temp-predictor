
`timescale 1ns/1ps

module uart_tx #(
    parameter CLK_FREQ  = 50000000,
    parameter BAUD_RATE = 115200
)(
    input wire       clk,
    input wire       rst_n,

    input wire [7:0] data_in,
    input wire       data_valid,

    output reg       tx,
    output reg       busy
);

    localparam integer CLKS_PER_BIT =
        CLK_FREQ / BAUD_RATE;


    reg [15:0] clk_count;

    reg [3:0] bit_count;

    reg [9:0] tx_shift;


    always @(posedge clk) begin

        if (!rst_n) begin

            tx        <= 1'b1;
            busy      <= 1'b0;

            clk_count <= 16'd0;
            bit_count <= 4'd0;

            tx_shift  <= 10'b1111111111;

        end

        else begin


            // =========================================
            // IDLE
            // =========================================

            if (!busy) begin

                tx <= 1'b1;

                clk_count <= 16'd0;

                bit_count <= 4'd0;


                if (data_valid) begin

                    /*
                     * UART frame:
                     *
                     * bit 0 = start
                     * bit 1..8 = data
                     * bit 9 = stop
                     */

                    tx_shift <= {
                        1'b1,
                        data_in,
                        1'b0
                    };

                    busy <= 1'b1;

                    tx <= 1'b0;

                end

            end


            // =========================================
            // TRANSMIT
            // =========================================

            else begin

                if (clk_count == CLKS_PER_BIT - 1) begin

                    clk_count <= 16'd0;


                    if (bit_count == 4'd9) begin

                        busy <= 1'b0;

                        bit_count <= 4'd0;

                        tx <= 1'b1;

                    end

                    else begin

                        bit_count <= bit_count + 1'b1;

                        tx <= tx_shift[bit_count + 1'b1];

                    end

                end

                else begin

                    clk_count <= clk_count + 1'b1;

                end

            end

        end

    end

endmodule