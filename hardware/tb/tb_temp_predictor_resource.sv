`timescale 1ns/1ps
module tb_temp_predictor_resource #(
    parameter integer A_Q = 8192,
    parameter integer B_Q = 3277,
    parameter integer C_Q = 0,
    parameter integer LATENCY = 8
);
    wire clk, rst_n, sample_valid, sample_ready, forecast_valid;
    wire signed [15:0] temp_in, forecast_out;
    temp_predictor_resource
`ifndef OLS_DUT_NO_PARAMETERS
        #(.A_Q(A_Q), .B_Q(B_Q), .C_Q(C_Q))
`endif
        dut (.*);
    ols_tb_driver #(.SPEED_MODE(0), .A_Q(A_Q), .B_Q(B_Q), .C_Q(C_Q),
                    .LATENCY(LATENCY), .MAX_LATENCY(10), .MAX_II(10))
        checks (.*);
endmodule
