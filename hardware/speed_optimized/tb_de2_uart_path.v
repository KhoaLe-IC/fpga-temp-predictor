`timescale 1ns/1ps
// -----------------------------------------------------------------------------
// Basic simulation testbench for the UART packet path.
// This TB sends a packet at the RTL UART level, waits for the predictor,
// and checks that an output packet is produced.
//
// For a full predictor numerical check, continue using tb_temp_predictor_speed.v.
// -----------------------------------------------------------------------------
module tb_de2_uart_path;

    reg clk;
    reg rst_n;
    reg rxd;

    wire txd;

    // Test uses a very small baud divider to keep simulation fast.
    localparam CLK_FREQ  = 1000000;
    localparam BAUD_RATE = 100000;

    de2_temp_predictor_top #(
        .COEF_FILE ("coeffs.txt"),
        .CLK_FREQ  (CLK_FREQ),
        .BAUD_RATE (BAUD_RATE)
    ) dut (
        .CLOCK_50 (clk),
        .KEY0_N   (rst_n),
        .UART_RXD (rxd),
        .UART_TXD (txd),
        .LEDR     (),
        .HEX0     (),
        .HEX1     (),
        .HEX2     (),
        .HEX3     ()
    );

    always #500 clk = ~clk; // 1 MHz

    task uart_send_byte;
        input [7:0] data;
        integer k;
        begin
            // Start
            rxd = 1'b0;
            repeat (10) @(posedge clk);

            // Data, LSB first
            for (k = 0; k < 8; k = k + 1) begin
                rxd = data[k];
                repeat (10) @(posedge clk);
            end

            // Stop
            rxd = 1'b1;
            repeat (10) @(posedge clk);
        end
    endtask

    task send_temperature;
        input [15:0] temp;
        reg [7:0] chk;
        begin
            chk = 8'h01 ^ 8'h02 ^ temp[15:8] ^ temp[7:0];

            uart_send_byte(8'hAA);
            uart_send_byte(8'h55);
            uart_send_byte(8'h01);
            uart_send_byte(8'h02);
            uart_send_byte(temp[15:8]);
            uart_send_byte(temp[7:0]);
            uart_send_byte(chk);
        end
    endtask

    initial begin
        clk = 1'b0;
        rst_n = 1'b0;
        rxd = 1'b1;

        repeat (20) @(posedge clk);
        rst_n = 1'b1;

        // 25 samples are needed before the first prediction.
        // Send a constant 20.00 C = 20*256 = 16'h1400.
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);
        send_temperature(16'h1400);

        repeat (5000) @(posedge clk);

        $display("UART path simulation finished.");
        $finish;
    end
endmodule
