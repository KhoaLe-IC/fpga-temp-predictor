`timescale 1ns/1ps
// Match these parameters to the real RTL and its documented latency.
module tb_temp_predictor_speed #(
    parameter integer A_Q = 8192,
    parameter integer B_Q = 3277,
    parameter integer C_Q = 0,
    parameter integer LATENCY = 5
);
    wire clk, rst_n, sample_valid, sample_ready, forecast_valid;
    wire signed [15:0] temp_in, forecast_out;
    temp_predictor_speed
`ifndef OLS_DUT_NO_PARAMETERS
        #(.A_Q(A_Q), .B_Q(B_Q), .C_Q(C_Q))
`endif
        dut (.*);
    ols_tb_driver #(.SPEED_MODE(1), .A_Q(A_Q), .B_Q(B_Q), .C_Q(C_Q),
                    .LATENCY(LATENCY), .MAX_LATENCY(8), .MAX_II(1))
        checks (.*);
endmodule
