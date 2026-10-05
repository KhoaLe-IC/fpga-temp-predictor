`timescale 1ns/1ps

module ols_shared_datapath (
    input  wire                    clk,
    input  wire                    rst_n,

    input  wire signed [15:0]       current_sample,
    input  wire signed [15:0]       tap_3,
    input  wire signed [15:0]       tap_21,
    input  wire signed [15:0]       tap_24,

    input  wire signed [15:0]       coeff_a,
    input  wire signed [15:0]       coeff_b,
    input  wire signed [15:0]       coeff_c,

    input  wire                    diff_sel_b,
    input  wire                    multiply_sel_b,

    input  wire                    diff_capture,
    input  wire                    product_a_capture,
    input  wire                    product_b_capture,
    input  wire                    acc_load_product_a,
    input  wire                    acc_add_product_b,
    input  wire                    acc_add_anchor,
    input  wire                    acc_add_offset,
    input  wire                    output_capture,

    output reg  signed [15:0]       result_out
);

    reg signed [16:0] difference;
    reg signed [32:0] product_a;
    reg signed [32:0] product_b;
    reg signed [34:0] accumulator;

    wire signed [16:0] subtract_rhs;
    wire signed [16:0] subtract_result;
    wire signed [15:0] selected_coefficient;
    wire signed [32:0] multiply_result;

    wire signed [34:0] product_a_extended;
    wire signed [34:0] product_b_extended;
    wire signed [34:0] anchor_aligned;
    wire signed [34:0] offset_aligned;
    wire signed [34:0] shifted_value;

    assign subtract_rhs = diff_sel_b ? {tap_3[15], tap_3}
                                     : {tap_24[15], tap_24};

    assign subtract_result = {current_sample[15], current_sample}
                           - subtract_rhs;

    assign selected_coefficient = multiply_sel_b ? coeff_b : coeff_a;

    assign multiply_result = difference * selected_coefficient;

    assign product_a_extended = {{2{product_a[32]}}, product_a};
    assign product_b_extended = {{2{product_b[32]}}, product_b};

    // Q8.8 anchor and offset are shifted into the Q22 accumulator domain.
    assign anchor_aligned = {{5{tap_21[15]}}, tap_21, 14'b0};
    assign offset_aligned = {{5{coeff_c[15]}}, coeff_c, 14'b0};

    assign shifted_value = accumulator >>> 14;

    always @(posedge clk) begin
        if (!rst_n) begin
            difference <= 17'sd0;
            product_a <= 33'sd0;
            product_b <= 33'sd0;
            accumulator <= 35'sd0;
            result_out <= 16'sd0;
        end else begin
            if (diff_capture)
                difference <= subtract_result;

            if (product_a_capture)
                product_a <= multiply_result;

            if (product_b_capture)
                product_b <= multiply_result;

            if (acc_load_product_a)
                accumulator <= product_a_extended;

            if (acc_add_product_b)
                accumulator <= accumulator + product_b_extended;

            if (acc_add_anchor)
                accumulator <= accumulator + anchor_aligned;

            if (acc_add_offset)
                accumulator <= accumulator + offset_aligned;

            if (output_capture) begin
                if (shifted_value > 35'sd32767)
                    result_out <= 16'sh7FFF;
                else if (shifted_value < -35'sd32768)
                    result_out <= 16'sh8000;
                else
                    result_out <= shifted_value[15:0];
            end
        end
    end

endmodule