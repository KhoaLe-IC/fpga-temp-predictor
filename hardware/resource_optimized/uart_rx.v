`timescale 1ns/1ps

module uart_rx #(
    parameter CLK_FREQ  = 50000000,
    parameter BAUD_RATE = 115200
)(
    input wire       clk,
    input wire       rst_n,

    input wire       rx,

    output reg [7:0] data_out,
    output reg       data_valid
);

    localparam integer CLKS_PER_BIT =
        CLK_FREQ / BAUD_RATE;


    localparam [2:0]

        S_IDLE  = 3'd0,
        S_START = 3'd1,
        S_DATA  = 3'd2,
        S_STOP  = 3'd3;


    reg [2:0] state;

    reg [15:0] clk_count;

    reg [2:0] bit_count;

    reg [7:0] rx_shift;


    always @(posedge clk) begin

        if (!rst_n) begin

            state      <= S_IDLE;

            clk_count  <= 16'd0;
            bit_count  <= 3'd0;

            rx_shift   <= 8'd0;

            data_out   <= 8'd0;
            data_valid <= 1'b0;

        end

        else begin

            data_valid <= 1'b0;


            case (state)


                // =========================================
                // IDLE
                // =========================================

                S_IDLE: begin

                    clk_count <= 16'd0;
                    bit_count <= 3'd0;

                    if (rx == 1'b0)
                        state <= S_START;

                end


                // =========================================
                // START
                // =========================================

                S_START: begin

                    if (clk_count ==
                        (CLKS_PER_BIT / 2 - 1)) begin

                        clk_count <= 16'd0;

                        if (rx == 1'b0)
                            state <= S_DATA;
                        else
                            state <= S_IDLE;

                    end

                    else begin

                        clk_count <= clk_count + 1'b1;

                    end

                end


                // =========================================
                // DATA
                // =========================================

                S_DATA: begin

                    if (clk_count == CLKS_PER_BIT - 1) begin

                        clk_count <= 16'd0;

                        rx_shift[bit_count] <= rx;


                        if (bit_count == 3'd7) begin

                            bit_count <= 3'd0;

                            state <= S_STOP;

                        end

                        else begin

                            bit_count <= bit_count + 1'b1;

                        end

                    end

                    else begin

                        clk_count <= clk_count + 1'b1;

                    end

                end


                // =========================================
                // STOP
                // =========================================

                S_STOP: begin

                    if (clk_count == CLKS_PER_BIT - 1) begin

                        clk_count <= 16'd0;

                        data_out <= rx_shift;

                        data_valid <= 1'b1;

                        state <= S_IDLE;

                    end

                    else begin

                        clk_count <= clk_count + 1'b1;

                    end

                end


                default:
                    state <= S_IDLE;

            endcase

        end

    end

endmodule
