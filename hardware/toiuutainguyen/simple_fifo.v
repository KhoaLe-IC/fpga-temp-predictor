
`timescale 1ns/1ps

module simple_fifo #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 8
)(
    input wire                   clk,
    input wire                   rst_n,

    input wire                   wr_en,
    input wire [DATA_WIDTH-1:0]  din,

    input wire                   rd_en,
    output wire [DATA_WIDTH-1:0] dout,

    output wire                  empty,
    output wire                  full,

    output wire [ADDR_WIDTH:0]   count
);

    localparam integer DEPTH =
        (1 << ADDR_WIDTH);


    reg [DATA_WIDTH-1:0] mem [0:DEPTH-1];

    reg [ADDR_WIDTH-1:0] wr_ptr;

    reg [ADDR_WIDTH-1:0] rd_ptr;

    reg [ADDR_WIDTH:0] count_reg;


    assign empty =
        (count_reg == 0);


    assign full =
        (count_reg == DEPTH);


    assign count =
        count_reg;


    /*
     * SHOW-AHEAD FIFO
     *
     * Current first element is directly available
     * at dout.
     */

    assign dout =
        mem[rd_ptr];


    always @(posedge clk) begin

        if (!rst_n) begin

            wr_ptr <= 0;
            rd_ptr <= 0;

            count_reg <= 0;

        end

        else begin


            // =========================================
            // WRITE
            // =========================================

            if (wr_en && !full) begin

                mem[wr_ptr] <= din;

                wr_ptr <= wr_ptr + 1'b1;

            end


            // =========================================
            // READ
            // =========================================

            if (rd_en && !empty) begin

                rd_ptr <= rd_ptr + 1'b1;

            end


            // =========================================
            // COUNT
            // =========================================

            case ({
                (wr_en && !full),
                (rd_en && !empty)
            })

                2'b10:
                    count_reg <= count_reg + 1'b1;

                2'b01:
                    count_reg <= count_reg - 1'b1;

                default:
                    count_reg <= count_reg;

            endcase

        end

    end

endmodule