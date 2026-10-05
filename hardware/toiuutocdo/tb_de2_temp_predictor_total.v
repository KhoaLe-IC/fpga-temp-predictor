`timescale 1ns/1ps
// COMPLETE END-TO-END TEST
// PC UART TX -> DE2 UART RX -> packet_parser -> predictor -> formatter -> UART TX -> PC UART RX
// Host packet : AA 55 01 02 TEMP_H TEMP_L CHECKSUM
// Reply packet: AA 55 81 02 FORECAST_H FORECAST_L CHECKSUM
//
// The test sends 25 identical +20.00 C samples. Therefore D1=D2=0 and
// forecast = T + C. C is read from coeffs.txt, so the expected result is
// generated from the same coefficient file used by the DUT.
module tb_de2_temp_predictor_total;
    reg clk;
    reg reset_n;
    reg uart_rxd;
    wire uart_txd;
    wire [7:0] led;
    wire [6:0] hex0, hex1, hex2, hex3;

    localparam integer CLK_FREQ = 1000000;
    localparam integer BAUD_RATE = 100000;
    localparam integer BAUD_CLKS = CLK_FREQ / BAUD_RATE;

    reg [15:0] coef_mem [0:2];
    reg [15:0] expected_forecast;
    integer error_count;
    integer sample_count;

    de2_temp_predictor_top #(
        .COEF_FILE("coeffs.txt"),
        .CLK_FREQ(CLK_FREQ),
        .BAUD_RATE(BAUD_RATE)
    ) dut (
        .CLOCK_50(clk),
        .KEY0_N(reset_n),
        .UART_RXD(uart_rxd),
        .UART_TXD(uart_txd),
        .LEDR(led),
        .HEX0(hex0), .HEX1(hex1), .HEX2(hex2), .HEX3(hex3)
    );

    always #500 clk = ~clk; // 1 MHz

    function [15:0] sat16;
        input signed [31:0] value;
        begin
            if (value > 32767)
                sat16 = 16'h7FFF;
            else if (value < -32768)
                sat16 = 16'h8000;
            else
                sat16 = value[15:0];
        end
    endfunction

    task pc_send_byte;
        input [7:0] data;
        integer k;
        begin
            uart_rxd = 1'b0;
            repeat (BAUD_CLKS) @(posedge clk);
            for (k = 0; k < 8; k = k + 1) begin
                uart_rxd = data[k];
                repeat (BAUD_CLKS) @(posedge clk);
            end
            uart_rxd = 1'b1;
            repeat (BAUD_CLKS) @(posedge clk);
        end
    endtask

    task pc_send_temperature;
        input [15:0] temp;
        reg [7:0] chk;
        begin
            chk = 8'h01 ^ 8'h02 ^ temp[15:8] ^ temp[7:0];
            pc_send_byte(8'hAA);
            pc_send_byte(8'h55);
            pc_send_byte(8'h01);
            pc_send_byte(8'h02);
            pc_send_byte(temp[15:8]);
            pc_send_byte(temp[7:0]);
            pc_send_byte(chk);
        end
    endtask

    task pc_receive_byte;
        output [7:0] data;
        integer k;
        begin
            @(negedge uart_txd);
            repeat (BAUD_CLKS/2) @(posedge clk);
            if (uart_txd !== 1'b0) begin
                $display("ERROR: TX start bit");
                error_count = error_count + 1;
            end
            repeat (BAUD_CLKS) @(posedge clk);
            data = 8'h00;
            for (k = 0; k < 8; k = k + 1) begin
                data[k] = uart_txd;
                repeat (BAUD_CLKS) @(posedge clk);
            end
            if (uart_txd !== 1'b1) begin
                $display("ERROR: TX stop bit");
                error_count = error_count + 1;
            end
            // FIX: do NOT wait another full bit here. We are in the middle of
            // the stop bit; waiting BAUD_CLKS would run past the falling edge of
            // the next byte's start bit, and the next call's @(negedge uart_txd)
            // would then lock onto a data bit and decode garbage.
            // The next call blocks on @(negedge uart_txd) by itself.
        end
    endtask

    task check_response;
        reg [7:0] b0,b1,b2,b3,bh,bl,bc;
        reg [15:0] received;
        reg [7:0] chk;
        begin
            pc_receive_byte(b0);
            pc_receive_byte(b1);
            pc_receive_byte(b2);
            pc_receive_byte(b3);
            pc_receive_byte(bh);
            pc_receive_byte(bl);
            pc_receive_byte(bc);
            received = {bh,bl};
            chk = 8'h81 ^ 8'h02 ^ bh ^ bl;

            $display("RX packet = %02h %02h %02h %02h %02h %02h %02h", b0,b1,b2,b3,bh,bl,bc);
            $display("Expected forecast = %04h, received = %04h", expected_forecast, received);

            if (b0 !== 8'hAA) error_count = error_count + 1;
            if (b1 !== 8'h55) error_count = error_count + 1;
            if (b2 !== 8'h81) error_count = error_count + 1;
            if (b3 !== 8'h02) error_count = error_count + 1;
            if (bc !== chk) begin
                $display("ERROR: response checksum");
                error_count = error_count + 1;
            end
            if (received !== expected_forecast) begin
                $display("ERROR: forecast mismatch");
                error_count = error_count + 1;
            end else begin
                $display("PASS: forecast matches.");
            end
        end
    endtask

    initial begin
        clk = 1'b0;
        reset_n = 1'b0;
        uart_rxd = 1'b1;
        error_count = 0;
        sample_count = 0;

        $readmemh("coeffs.txt", coef_mem);
        expected_forecast = sat16(32'sh00001400 + $signed(coef_mem[2]));

        $display("============================================================");
        $display("TOTAL UART -> PARSER -> PREDICTOR -> UART TEST");
        $display("C = %04h, input = 1400, expected = %04h", coef_mem[2], expected_forecast);
        $display("============================================================");

        repeat (20) @(posedge clk);
        reset_n = 1'b1;

        // First prediction requires 25 accepted samples.
        repeat (25) begin
            pc_send_temperature(16'h1400);
            sample_count = sample_count + 1;
            $display("PC -> FPGA : sample %0d = 20.00 C", sample_count);
        end

        check_response();

        // Prove that the system continues after warm-up.
        pc_send_temperature(16'h1400);
        sample_count = sample_count + 1;
        $display("PC -> FPGA : sample %0d = 20.00 C", sample_count);
        check_response();

        repeat (100) @(posedge clk);

        $display("============================================================");
        if (error_count == 0)
            $display("TOTAL TEST: PASS");
        else
            $display("TOTAL TEST: FAIL, errors = %0d", error_count);
        $display("============================================================");
        $finish;
    end
endmodule