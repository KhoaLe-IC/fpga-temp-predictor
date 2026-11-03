`timescale 1ns/1ps
// CHECKER SELF-TEST ONLY. These are timed behavioral stand-ins, not FPGA RTL.
// Never compile this file with real DUTs or include it in a synthesis project.
`ifndef OLS_MOCK_SPEED_LATENCY
`define OLS_MOCK_SPEED_LATENCY 5
`endif
`ifndef OLS_MOCK_RESOURCE_LATENCY
`define OLS_MOCK_RESOURCE_LATENCY 8
`endif
module ols_behavioral_dut #(
    parameter bit SPEED_MODE = 1,
    parameter integer LATENCY = 5,
    parameter integer A_Q = 8192, B_Q = 3277, C_Q = 0
) (
    input wire clk, rst_n, sample_valid,
    input wire signed [15:0] temp_in,
    output wire sample_ready,
    output logic forecast_valid = 0,
    output logic signed [15:0] forecast_out = 0
);
    logic signed [15:0] history [0:24];
    logic signed [15:0] results [0:65535];
    integer deadlines [0:65535];
    integer n = 0, cycles = 0, head = 0, tail = 0, j;
    logic busy = 0;
    reg [255:0] mutation = 0;
    integer unused;
    initial unused = $value$plusargs("MUTATION=%s", mutation);
    assign sample_ready = (mutation == "READY") ? (SPEED_MODE ? 1'b0 : 1'b1) :
                          (SPEED_MODE ? 1'b1 : !busy);

    // A bounded-width, shift-based implementation differs from the driver's
    // unbounded-in-practice 64-bit, floor-division arithmetic oracle.
    function automatic logic signed [15:0] calculate;
        input logic signed [15:0] t0, t3, t21, t24;
        logic signed [16:0] d1, d2;
        logic signed [15:0] a, b;
        logic signed [32:0] p1, p2;
        logic signed [34:0] s, base, offset, q;
        begin
            a = 16'(A_Q); b = 16'(B_Q);
            d1 = {t0[15],t0} - {t24[15],t24};
            d2 = {t0[15],t0} - {t3[15],t3};
            p1 = d1*a; p2 = d2*b;
            base = 35'(t21); offset = 35'(C_Q);
            s = {{2{p1[32]}},p1} + {{2{p2[32]}},p2} +
                (base <<< 14) + (offset <<< 14);
            q = s >>> 14;
            if (q > 32767) calculate = 16'sh7fff;
            else if (q < -32768) calculate = 16'sh8000;
            else calculate = q[15:0];
        end
    endfunction

    always @(posedge clk) begin
        cycles = cycles + 1;
        forecast_valid <= 0;
        if (!rst_n) begin
            if (mutation == "RESET_STALE" && head < tail)
                forecast_valid <= 1;
            n = 0; head = 0; tail = 0; busy <= 0;
            for (j = 0; j < 25; j = j + 1) history[j] = 0;
        end else begin
            if (sample_valid && sample_ready) begin
                for (j = 24; j > 0; j = j - 1) history[j] = history[j-1];
                history[0] = temp_in; n = n + 1;
                if (n >= 25) begin
                    results[tail] = calculate(history[0], history[3], history[21], history[24]);
                    deadlines[tail] = cycles + LATENCY - ((mutation == "EARLY") ? 1 : 0);
                    tail = tail + 1;
                    if (!SPEED_MODE) busy <= 1;
                end
            end
            if (head < tail && deadlines[head] == cycles) begin
                forecast_valid <= (mutation != "DROP");
                forecast_out <= results[head] ^ ((mutation == "DATA") ? 16'h0001 : 16'h0000);
                head = head + 1;
                if (!SPEED_MODE) busy <= 0;
            end
        end
    end
endmodule

module temp_predictor_speed #(
    parameter integer A_Q = 8192, B_Q = 3277, C_Q = 0
) (
    input wire clk, rst_n, sample_valid,
    input wire signed [15:0] temp_in,
    output wire sample_ready, forecast_valid,
    output wire signed [15:0] forecast_out
);
    ols_behavioral_dut #(.SPEED_MODE(1), .LATENCY(`OLS_MOCK_SPEED_LATENCY),
                         .A_Q(A_Q), .B_Q(B_Q), .C_Q(C_Q)) model (.*);
endmodule

module temp_predictor_resource #(
    parameter integer A_Q = 8192, B_Q = 3277, C_Q = 0
) (
    input wire clk, rst_n, sample_valid,
    input wire signed [15:0] temp_in,
    output wire sample_ready, forecast_valid,
    output wire signed [15:0] forecast_out
);
    ols_behavioral_dut #(.SPEED_MODE(0), .LATENCY(`OLS_MOCK_RESOURCE_LATENCY),
                         .A_Q(A_Q), .B_Q(B_Q), .C_Q(C_Q)) model (.*);
endmodule
