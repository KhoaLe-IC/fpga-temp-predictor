`timescale 1ns/1ps

// =============================================================================
// Self-checking testbench for top_temp_predictor_uart
//
//  - Drives UART_RX at 115200 baud (hex ASCII samples, various separators)
//  - Decodes UART_TX with its own UART receiver
//  - Reference model (64-bit integer math) predicts every output
//  - Checks: values, line framing (4 hex + CR + LF), no output before sample
//    #25, exact number of output lines, no UART framing errors
//
//  Plusargs:  +N=<samples>  +MODE=<0 random | 1 smooth | 2 extremes>
//             +SEED=<int>   +QUIET (hide per-sample table)   +VCD
//  Reads "coefficients.txt" (A, B in Q2.14 ; C in Q8.8) from the run directory,
//  the same file the DUT reads.
// =============================================================================

module tb_top_temp_predictor_uart;

    localparam integer BIT_NS = 8680;     // 434 clocks * 20 ns
    localparam integer MAX_N  = 256;
    localparam integer WARMUP = 24;       // outputs start at sample #25

    reg  CLOCK_50 = 1'b0;
    reg  UART_RX  = 1'b1;
    wire UART_TX;

    always #10 CLOCK_50 = ~CLOCK_50;

    top_temp_predictor_uart dut (
        .CLOCK_50(CLOCK_50),
        .UART_RX (UART_RX),
        .UART_TX (UART_TX)
    );

    // ------------------------------------------------------------------
    // Storage
    // ------------------------------------------------------------------
    reg signed [15:0] x        [0:MAX_N-1];
    reg signed [15:0] expected [0:MAX_N-1];
    reg        [15:0] coef_tb  [0:2];

    reg signed [15:0] cA, cB, cC;

    integer N, MODE, SEED, VERBOSE;
    integer seed_v;
    integer i;
    integer errors      = 0;
    integer lines_rx    = 0;
    integer hex_started = 0;
    integer max_rx_cnt  = 0;
    integer max_tx_cnt  = 0;
    integer pos         = 0;
    reg [15:0] line_val;
    reg signed [31:0] r;
    time t_last_send;

    // ------------------------------------------------------------------
    // Reference model
    //   res = sat16( ((x[n]-x[n-24])*A + (x[n]-x[n-3])*B) >>> 14
    //                + x[n-21] + C )
    // ------------------------------------------------------------------
    function signed [15:0] ref_model;
        input integer n;
        reg signed [63:0] dA, dB, acc, sh;
        begin
            dA  = x[n] - x[n-24];
            dB  = x[n] - x[n-3];
            acc = dA * cA + dB * cB;
            sh  = (acc >>> 14) + x[n-21] + cC;
            if (sh > 64'sd32767)        ref_model = 16'sh7FFF;
            else if (sh < -64'sd32768)  ref_model = 16'sh8000;
            else                        ref_model = sh[15:0];
        end
    endfunction

    function [7:0] hexchar;
        input [3:0] v;
        input       lower;
        begin
            if (v < 10) hexchar = "0" + v;
            else        hexchar = (lower ? "a" : "A") + (v - 10);
        end
    endfunction

    function is_hexchar;
        input [7:0] c;
        begin
            is_hexchar = ((c >= "0") && (c <= "9")) ||
                         ((c >= "A") && (c <= "F"));
        end
    endfunction

    function [3:0] hexval;
        input [7:0] c;
        begin
            if (c <= "9") hexval = c - "0";
            else          hexval = c - "A" + 4'd10;
        end
    endfunction

    // ------------------------------------------------------------------
    // UART driver
    // ------------------------------------------------------------------
    task uart_send_byte;
        input [7:0] b;
        integer k;
        begin
            UART_RX = 1'b0;  #(BIT_NS);
            for (k = 0; k < 8; k = k + 1) begin
                UART_RX = b[k];  #(BIT_NS);
            end
            UART_RX = 1'b1;  #(BIT_NS);
        end
    endtask

    task send_sample;
        input integer idx;
        reg [15:0] v;
        reg        lower;
        begin
            v     = x[idx];
            lower = (idx % 2);

            hex_started = hex_started + 1;  uart_send_byte(hexchar(v[15:12], lower));
            hex_started = hex_started + 1;  uart_send_byte(hexchar(v[11:8],  lower));
            hex_started = hex_started + 1;  uart_send_byte(hexchar(v[7:4],   lower));
            hex_started = hex_started + 1;  uart_send_byte(hexchar(v[3:0],   lower));

            // different separators between samples
            case (idx % 5)
                0: begin uart_send_byte(8'h0D); uart_send_byte(8'h0A); end
                1: uart_send_byte(8'h0A);
                2: uart_send_byte(" ");
                3: ;                                   // no separator at all
                4: begin uart_send_byte(8'h0D); uart_send_byte(8'h0A);
                         #(3*BIT_NS); end              // idle gap
            endcase

            if ((idx % 7) == 3) uart_send_byte(",");   // stray non-hex char
        end
    endtask

    // ------------------------------------------------------------------
    // UART TX monitor + checker
    // ------------------------------------------------------------------
    always @(negedge UART_TX) begin : tx_monitor
        integer b;
        reg [7:0] txb;
        integer idx;

        // start of a new output line: must not appear before its input exists
        if (pos == 0) begin
            if (hex_started < 4*(WARMUP + 1 + lines_rx)) begin
                $display("[%0t] ERROR: output line %0d started too early (only %0d hex digits sent)",
                         $time, lines_rx, hex_started);
                errors = errors + 1;
            end
        end

        #(BIT_NS/2);
        if (UART_TX !== 1'b0) begin
            $display("[%0t] ERROR: TX start bit glitch", $time);
            errors = errors + 1;
        end

        for (b = 0; b < 8; b = b + 1) begin
            #(BIT_NS);
            txb[b] = UART_TX;
        end

        #(BIT_NS);
        if (UART_TX !== 1'b1) begin
            $display("[%0t] ERROR: TX stop bit framing error", $time);
            errors = errors + 1;
        end

        // ---- byte -> line assembly
        case (pos)
            0, 1, 2, 3: begin
                if (is_hexchar(txb)) begin
                    line_val = {line_val[11:0], hexval(txb)};
                    pos = pos + 1;
                end else begin
                    $display("[%0t] ERROR: line %0d char %0d is not uppercase hex: 0x%02h",
                             $time, lines_rx, pos, txb);
                    errors = errors + 1;
                    pos = 0;
                end
            end

            4: begin
                if (txb === 8'h0D) pos = 5;
                else begin
                    $display("[%0t] ERROR: line %0d expected CR, got 0x%02h", $time, lines_rx, txb);
                    errors = errors + 1;
                    pos = 0;
                end
            end

            5: begin
                pos = 0;
                if (txb !== 8'h0A) begin
                    $display("[%0t] ERROR: line %0d expected LF, got 0x%02h", $time, lines_rx, txb);
                    errors = errors + 1;
                end else begin
                    idx = WARMUP + lines_rx;
                    if (idx >= N) begin
                        $display("[%0t] ERROR: unexpected extra output line %0d (value %04h)",
                                 $time, lines_rx, line_val);
                        errors = errors + 1;
                    end else begin
                        if (VERBOSE)
                            $display("  %6d | %04h (%6d) | %04h (%6d) | %04h (%6d) | %9.3f | %0s",
                                     idx + 1,
                                     x[idx],        x[idx],
                                     expected[idx], expected[idx],
                                     line_val,      $signed(line_val),
                                     $itor($signed(line_val)) / 256.0,
                                     (line_val === expected[idx]) ? "PASS" : "FAIL");
                        if (line_val !== expected[idx]) begin
                            if (!VERBOSE)
                                $display("[%0t] FAIL  sample #%0d  got %04h  expected %04h",
                                         $time, idx + 1, line_val, expected[idx]);
                            errors = errors + 1;
                        end
                    end
                    lines_rx = lines_rx + 1;
                end
            end
        endcase
    end

    // FIFO occupancy watch (overflow check)
    always @(posedge CLOCK_50) begin
        if (dut.rx_fifo_count > max_rx_cnt) max_rx_cnt = dut.rx_fifo_count;
        if (dut.tx_fifo_count > max_tx_cnt) max_tx_cnt = dut.tx_fifo_count;
        if (dut.rx_fifo_full === 1'b1) begin
            $display("[%0t] ERROR: RX FIFO full (data lost)", $time);
            errors = errors + 1;
        end
    end

    // ------------------------------------------------------------------
    // Main sequence
    // ------------------------------------------------------------------
    initial begin
        if (!$value$plusargs("N=%d",    N))    N    = 60;
        if (!$value$plusargs("MODE=%d", MODE)) MODE = 0;
        if (!$value$plusargs("SEED=%d", SEED)) SEED = 1;
        VERBOSE = !$test$plusargs("QUIET");   // per-sample table is ON by default
        if (N < WARMUP + 1) N = WARMUP + 1;
        if (N > MAX_N)      N = MAX_N;

        if ($test$plusargs("VCD")) begin
            $dumpfile("tb.vcd");
            $dumpvars(0, tb_top_temp_predictor_uart);
        end

        $readmemh("coefficients.txt", coef_tb);
        cA = coef_tb[0];
        cB = coef_tb[1];
        cC = coef_tb[2];
        $display("TB: N=%0d MODE=%0d SEED=%0d  A=%04h B=%04h C=%04h",
                 N, MODE, SEED, cA, cB, cC);
        if (VERBOSE) begin
            $display("");
            $display("  Sample |  INPUT hex (dec)  |  EXPECTED hex (dec) |  DUT OUTPUT hex (dec) | out/256  | Result");
            $display("  -------+-------------------+---------------------+-----------------------+----------+-------");
        end

        // ---- generate stimulus + expected results
        seed_v = SEED;
        for (i = 0; i < N; i = i + 1) begin
            r = $random(seed_v);
            case (MODE)
                0: x[i] = r[15:0];
                1: x[i] = 16'sd6144 + $signed({7'b0, r[8:0]}) - 16'sd256;
                default: begin
                    case (r[1:0])
                        2'd0: x[i] = 16'sh7FFF;
                        2'd1: x[i] = 16'sh8000;
                        2'd2: x[i] = r[17:2];
                        2'd3: x[i] = 16'sd0;
                    endcase
                end
            endcase
        end
        for (i = WARMUP; i < N; i = i + 1)
            expected[i] = ref_model(i);

        // ---- wait for power-on reset to release, then offset from clock edge
        wait (dut.rst_n === 1'b1);
        repeat (10) @(posedge CLOCK_50);
        #5;

        // ---- first WARMUP samples back-to-back (history only, no output)
        for (i = 0; i < WARMUP; i = i + 1)
            send_sample(i);

        // ---- from sample #25: send one, wait for its result line, repeat
        for (i = WARMUP; i < N; i = i + 1) begin
            send_sample(i);
            wait (lines_rx == (i - WARMUP + 1));
        end
        t_last_send = $time;

        // ---- wait for all expected lines (or timeout)
        while ((lines_rx < N - WARMUP) &&
               (($time - t_last_send) < ((N - WARMUP) * 70 + 500) * BIT_NS))
            #(BIT_NS);

        // catch spurious extra lines / half-finished lines
        #(30*BIT_NS);

        if (lines_rx !== N - WARMUP) begin
            $display("ERROR: received %0d output lines, expected %0d", lines_rx, N - WARMUP);
            errors = errors + 1;
        end
        if (pos !== 0) begin
            $display("ERROR: incomplete output line at end of test (pos=%0d)", pos);
            errors = errors + 1;
        end

        $display("TB: lines=%0d/%0d  max_rx_fifo=%0d  max_tx_fifo=%0d",
                 lines_rx, N - WARMUP, max_rx_cnt, max_tx_cnt);
        if (errors == 0) $display("RESULT: PASS");
        else             $display("RESULT: FAIL (%0d errors)", errors);
        $finish;
    end

    // global watchdog
    initial begin
        #800_000_000;
        $display("RESULT: FAIL (watchdog timeout)");
        $finish;
    end

endmodule