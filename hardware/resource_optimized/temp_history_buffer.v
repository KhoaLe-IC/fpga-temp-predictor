`timescale 1ns/1ps

module temp_history_buffer (
    input  wire                    clk,
    input  wire                    rst_n,
    input  wire                    push,
    input  wire signed [15:0]       sample_in,
    output wire signed [15:0]       tap_3,
    output wire signed [15:0]       tap_21,
    output wire signed [15:0]       tap_24
);

    reg signed [15:0] history [0:24];

    assign tap_3  = history[3];
    assign tap_21 = history[21];
    assign tap_24 = history[24];

    always @(posedge clk) begin
        if (!rst_n) begin
        end else if (push) begin
            history[24] <= history[23];
            history[23] <= history[22];
            history[22] <= history[21];
            history[21] <= history[20];
            history[20] <= history[19];
            history[19] <= history[18];
            history[18] <= history[17];
            history[17] <= history[16];
            history[16] <= history[15];
            history[15] <= history[14];
            history[14] <= history[13];
            history[13] <= history[12];
            history[12] <= history[11];
            history[11] <= history[10];
            history[10] <= history[9];
            history[9]  <= history[8];
            history[8]  <= history[7];
            history[7]  <= history[6];
            history[6]  <= history[5];
            history[5]  <= history[4];
            history[4]  <= history[3];
            history[3]  <= history[2];
            history[2]  <= history[1];
            history[1]  <= history[0];
            history[0]  <= sample_in;
        end
    end

endmodule