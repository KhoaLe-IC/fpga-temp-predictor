`timescale 1ns/1ps

module temp_predictor_resource (

    input  wire                    clk,
    input  wire                    rst_n,

    input  wire                    sample_valid,
    output wire                    sample_ready,

    input  wire signed [15:0]      temp_in,

    output reg                     forecast_valid,
    output wire signed [15:0]      forecast_out
);

    // =========================================================
    // COEFFICIENTS
    // =========================================================

    // A, B = Q2.14
    // C     = Q8.8

    reg signed [15:0] coeff_mem [0:2];

    wire signed [15:0] coeff_a;
    wire signed [15:0] coeff_b;
    wire signed [15:0] coeff_c;

    initial begin

        coeff_mem[0] = 16'h0000;
        coeff_mem[1] = 16'h0000;
        coeff_mem[2] = 16'h0000;

        $readmemh("coefficients.txt", coeff_mem);

    end

    assign coeff_a = coeff_mem[0];
    assign coeff_b = coeff_mem[1];
    assign coeff_c = coeff_mem[2];


    // =========================================================
    // FSM
    // =========================================================

    localparam [3:0]

        ST_IDLE       = 4'd0,
        ST_DIFF_A     = 4'd1,
        ST_MUL_A      = 4'd2,
        ST_DIFF_B     = 4'd3,
        ST_MUL_B      = 4'd4,
        ST_ACC_P1     = 4'd5,
        ST_ACC_P2     = 4'd6,
        ST_ACC_ANCHOR = 4'd7,
        ST_ACC_C      = 4'd8,
        ST_OUTPUT     = 4'd9;


    reg [3:0] state;

    reg [5:0] sample_count;

    reg signed [15:0] current_sample;

    reg history_push;

    reg diff_sel_b;
    reg multiply_sel_b;

    reg diff_capture;
    reg product_a_capture;
    reg product_b_capture;

    reg acc_load_product_a;
    reg acc_add_product_b;
    reg acc_add_anchor;
    reg acc_add_offset;

    reg output_capture;


    // =========================================================
    // HISTORY
    // =========================================================

    wire signed [15:0] tap_3;
    wire signed [15:0] tap_21;
    wire signed [15:0] tap_24;


    // =========================================================
    // DATAPATH
    // =========================================================

    wire signed [15:0] datapath_result;


    assign sample_ready = (state == ST_IDLE);

    assign forecast_out = datapath_result;


    // =========================================================
    // HISTORY BUFFER
    // =========================================================

    temp_history_buffer history_inst (

        .clk(clk),
        .rst_n(rst_n),

        .push(history_push),

        .sample_in(temp_in),

        .tap_3(tap_3),
        .tap_21(tap_21),
        .tap_24(tap_24)

    );


    // =========================================================
    // SHARED DATAPATH
    // =========================================================

    ols_shared_datapath datapath_inst (

        .clk(clk),
        .rst_n(rst_n),

        .current_sample(current_sample),

        .tap_3(tap_3),
        .tap_21(tap_21),
        .tap_24(tap_24),

        .coeff_a(coeff_a),
        .coeff_b(coeff_b),
        .coeff_c(coeff_c),

        .diff_sel_b(diff_sel_b),
        .multiply_sel_b(multiply_sel_b),

        .diff_capture(diff_capture),
        .product_a_capture(product_a_capture),
        .product_b_capture(product_b_capture),

        .acc_load_product_a(acc_load_product_a),
        .acc_add_product_b(acc_add_product_b),
        .acc_add_anchor(acc_add_anchor),
        .acc_add_offset(acc_add_offset),

        .output_capture(output_capture),

        .result_out(datapath_result)

    );


    // =========================================================
    // CONTROL SIGNALS
    // =========================================================

    always @(*) begin

        history_push       = 1'b0;

        diff_sel_b         = 1'b0;
        multiply_sel_b     = 1'b0;

        diff_capture       = 1'b0;

        product_a_capture  = 1'b0;
        product_b_capture  = 1'b0;

        acc_load_product_a = 1'b0;
        acc_add_product_b  = 1'b0;
        acc_add_anchor     = 1'b0;
        acc_add_offset     = 1'b0;

        output_capture     = 1'b0;


        if ((state == ST_IDLE) &&
            sample_valid &&
            sample_ready) begin

            history_push = 1'b1;

        end


        case (state)

            ST_DIFF_A: begin

                diff_sel_b   = 1'b0;
                diff_capture = 1'b1;

            end


            ST_MUL_A: begin

                multiply_sel_b    = 1'b0;
                product_a_capture = 1'b1;

            end


            ST_DIFF_B: begin

                diff_sel_b   = 1'b1;
                diff_capture = 1'b1;

            end


            ST_MUL_B: begin

                multiply_sel_b    = 1'b1;
                product_b_capture = 1'b1;

            end


            ST_ACC_P1: begin
                acc_load_product_a = 1'b1;
            end


            ST_ACC_P2: begin
                acc_add_product_b = 1'b1;
            end


            ST_ACC_ANCHOR: begin
                acc_add_anchor = 1'b1;
            end


            ST_ACC_C: begin
                acc_add_offset = 1'b1;
            end


            ST_OUTPUT: begin
                output_capture = 1'b1;
            end


            default: begin
            end

        endcase

    end


    // =========================================================
    // FSM
    // =========================================================

    always @(posedge clk) begin

        if (!rst_n) begin

            state          <= ST_IDLE;

            sample_count   <= 6'd0;

            current_sample <= 16'sd0;

            forecast_valid <= 1'b0;

        end

        else begin

            forecast_valid <= 1'b0;


            case (state)

                // =================================================
                // RECEIVE SAMPLE
                // =================================================

                ST_IDLE: begin

                    if (sample_valid && sample_ready) begin

                        if (sample_count < 6'd25)
                            sample_count <= sample_count + 1'b1;


                        /*
                         * sample_count == 24 means:
                         *
                         * 24 samples already stored
                         * current sample = sample #25
                         *
                         * Therefore start prediction.
                         */

                        if (sample_count >= 6'd24) begin

                            current_sample <= temp_in;

                            state <= ST_DIFF_A;

                        end

                    end

                end


                ST_DIFF_A:
                    state <= ST_MUL_A;


                ST_MUL_A:
                    state <= ST_DIFF_B;


                ST_DIFF_B:
                    state <= ST_MUL_B;


                ST_MUL_B:
                    state <= ST_ACC_P1;


                ST_ACC_P1:
                    state <= ST_ACC_P2;


                ST_ACC_P2:
                    state <= ST_ACC_ANCHOR;


                ST_ACC_ANCHOR:
                    state <= ST_ACC_C;


                ST_ACC_C:
                    state <= ST_OUTPUT;


                ST_OUTPUT: begin

                    forecast_valid <= 1'b1;

                    state <= ST_IDLE;

                end


                default:
                    state <= ST_IDLE;

            endcase

        end

    end

endmodule