`timescale 1ns/1ps
// -----------------------------------------------------------------------------
// Directed testbench for temp_predictor_speed (same style as the resource TB).
// Files needed: temp_predictor_speed.v, this file, coefficients.txt
//
// Expected values are computed from the loaded coefficients using the shared
// numerical contract: ONE sum  S = A*D1 + B*D2 + (T21 + C)<<14,  then
// floor(S / 2^14) and saturation to 16 bit (no per-product shifting).
// -----------------------------------------------------------------------------
module tb_temp_predictor_speed_directed;
    localparam LATENCY_NEGEDGES = 5;   // negedges between end of send_sample and forecast_valid

    reg clk;
    reg rst_n;
    reg sample_valid;
    reg signed [15:0] sample_in;

    wire sample_ready;
    wire forecast_valid;
    wire signed [15:0] forecast_out;

    integer i;
    integer errors;
    integer timeout_count;
    integer verbose;
    integer fv_count;                   // number of cycles forecast_valid was high
    integer fv_before;
    integer n_sent;                     // samples accepted since last reset
    reg signed [15:0] samp [0:127];     // history of samples sent since last reset
    reg signed [15:0] expected_raw;
    real actual_temp;
    real expected_temp;

    initial clk = 1'b0;
    always #10 clk = ~clk; // 50 MHz

    always @(posedge clk) if (forecast_valid === 1'b1) fv_count = fv_count + 1;

    temp_predictor_speed #(.COEF_FILE("coeffs.txt")) uut (
        .clk(clk),
        .rst_n(rst_n),
        .sample_valid(sample_valid),
        .sample_ready(sample_ready),
        .temp_in(sample_in),
        .forecast_valid(forecast_valid),
        .forecast_out(forecast_out)
    );

    // ---------------------------------------------------------------
    // Expected forecast for sample index idx (needs idx >= 24)
    // ---------------------------------------------------------------
    function signed [15:0] calc_expected;
        input integer idx;
        reg signed [63:0] t, t3, t21, t24, a, b, c, s, q, d, sat;
        begin
            t = samp[idx];  t3 = samp[idx-3];  t21 = samp[idx-21];  t24 = samp[idx-24];
            a = $signed(uut.COEF_A);  b = $signed(uut.COEF_B);  c = $signed(uut.COEF_C);
            s = a*(t - t24) + b*(t - t3) + (t21 + c)*64'sd16384;
            d = 64'sd16384;
            q = s / d;
            if ((s % d) != 0 && s < 0) q = q - 64'sd1;      // floor
            sat = q;
            if (q >  64'sd32767) sat =  64'sd32767;
            if (q < -64'sd32768) sat = -64'sd32768;
            calc_expected = sat[15:0];
        end
    endfunction

    task do_reset;
        begin
            @(negedge clk);
            rst_n = 1'b0;
            sample_valid = 1'b0;
            repeat (2) @(negedge clk);
            rst_n = 1'b1;
            n_sent = 0;
        end
    endtask

    task send_sample;
        input signed [15:0] value;
        begin
            @(negedge clk);
            while (sample_ready !== 1'b1)
                @(negedge clk);
            sample_in = value;
            sample_valid = 1'b1;
            samp[n_sent] = value;
            n_sent = n_sent + 1;
            @(negedge clk);
            sample_valid = 1'b0;
            if (verbose)
                $display("INPUT #%0d  Q8.8=%0d, temperature=%0.3f C",
                         n_sent-1, $signed(value), $itor($signed(value))/256.0);
        end
    endtask

    // Wait for the forecast of the most recently sent sample and check value + latency
    task check_prediction;
        input [255:0] name;
        reg received;
        begin
            expected_raw = calc_expected(n_sent-1);
            received = 1'b0;
            timeout_count = 0;
            while ((received == 1'b0) && (timeout_count < 500)) begin
                @(negedge clk);
                timeout_count = timeout_count + 1;
                if (forecast_valid === 1'b1)
                    received = 1'b1;
            end

            $display("---- %0s ----", name);
            if (!received) begin
                $display("ERROR: prediction timeout");
                errors = errors + 1;
            end else begin
                actual_temp   = $itor($signed(forecast_out))/256.0;
                expected_temp = $itor($signed(expected_raw))/256.0;
                $display("OUTPUT raw Q8.8 : %0d (0x%04h)   temp = %0.3f C",
                         $signed(forecast_out), forecast_out, actual_temp);
                $display("EXPECTED raw    : %0d (0x%04h)   temp = %0.3f C",
                         $signed(expected_raw), expected_raw, expected_temp);
                if ($signed(forecast_out) == $signed(expected_raw))
                    $display("VALUE  CHECK: PASS");
                else begin
                    $display("VALUE  CHECK: FAIL");
                    errors = errors + 1;
                end
                if (timeout_count == LATENCY_NEGEDGES)
                    $display("LATENCY CHECK: PASS (%0d cycles after accepting edge)", timeout_count);
                else begin
                    $display("LATENCY CHECK: FAIL (got %0d, expected %0d)", timeout_count, LATENCY_NEGEDGES);
                    errors = errors + 1;
                end
            end
        end
    endtask

    task expect_no_forecast;
        input [255:0] name;
        input integer before_count;
        begin
            if (fv_count == before_count)
                $display("---- %0s: PASS (no forecast_valid) ----", name);
            else begin
                $display("---- %0s: FAIL (forecast_valid seen %0d time(s)) ----", name, fv_count - before_count);
                errors = errors + 1;
            end
        end
    endtask

    initial begin
        rst_n = 1'b0;
        sample_valid = 1'b0;
        sample_in = 16'sd0;
        errors = 0;
        timeout_count = 0;
        verbose = 1;
        fv_count = 0;
        n_sent = 0;

        repeat (3) @(negedge clk);
        #1;
        $display("========================================");
        $display(" OLS TEMPERATURE PREDICTOR (SPEED) TESTBENCH");
        $display(" Coefficients loaded from coefficients.txt");
        $display(" A Q2.14 raw=0x%h, A=%0.5f", uut.COEF_A, $itor($signed(uut.COEF_A))/16384.0);
        $display(" B Q2.14 raw=0x%h, B=%0.5f", uut.COEF_B, $itor($signed(uut.COEF_B))/16384.0);
        $display(" C Q8.8  raw=0x%h, C=%0.5f C", uut.COEF_C, $itor($signed(uut.COEF_C))/256.0);
        if ((^uut.COEF_A === 1'bx) || (^uut.COEF_B === 1'bx) || (^uut.COEF_C === 1'bx)) begin
            $display("FATAL: coefficient value is X. Check ModelSim working directory and coefficients.txt.");
            $finish;
        end
        $display("========================================");

        rst_n = 1'b1;

        // ---- TEST 1: no forecast during the first 24 samples (0..23 C) ----
        $display("\n#### TEST 1: no output before the 25th sample");
        for (i = 0; i < 24; i = i + 1) send_sample(i * 256);
        repeat (12) @(negedge clk);
        expect_no_forecast("24 samples sent", 0);

        // ---- TEST 2: 25th sample (24 C) -> first forecast; ramp: T=24, T-3=21, T-21=3, T-24=0 ----
        $display("\n#### TEST 2: 25th sample produces the first forecast");
        send_sample(24 * 256);
        check_prediction("first forecast (25th sample)");

        // ---- TEST 3: next sample, sliding window ----
        $display("\n#### TEST 3: 26th sample, window slides");
        send_sample(25 * 256);
        check_prediction("second forecast (26th sample)");

        // ---- TEST 4: constant negative temperature (-10 C): D1 = D2 = 0 -> T21 + C ----
        $display("\n#### TEST 4: reset, then constant -10 C");
        do_reset;
        for (i = 0; i < 25; i = i + 1) send_sample(-10 * 256);
        check_prediction("constant -10 C");

        // ---- TEST 5: large step between extremes (stress D1/D2 range) ----
        $display("\n#### TEST 5: reset, 24 x (-32768) then +32767");
        do_reset;
        verbose = 0;
        for (i = 0; i < 24; i = i + 1) send_sample(16'sh8000);
        send_sample(16'sh7FFF);
        verbose = 1;
        check_prediction("extreme step");

        // ---- TEST 6: reset discards an in-flight forecast ----
        $display("\n#### TEST 6: reset while the 25th forecast is in the pipeline");
        do_reset;
        verbose = 0;
        for (i = 0; i < 24; i = i + 1) send_sample(i * 256);
        verbose = 1;
        fv_before = fv_count;
        send_sample(24 * 256);                // forecast now in flight
        do_reset;                             // reset one cycle later
        repeat (15) @(negedge clk);
        expect_no_forecast("in-flight forecast discarded", fv_before);

        // ---- TEST 7: warm-up restarts after reset (25 samples again, 5..29 C) ----
        $display("\n#### TEST 7: warm-up restarts after reset");
        verbose = 0;
        for (i = 0; i < 24; i = i + 1) send_sample((i + 5) * 256);
        repeat (10) @(negedge clk);
        expect_no_forecast("only 24 samples after reset", fv_before);
        verbose = 1;
        send_sample(29 * 256);
        check_prediction("forecast after restarted warm-up");

        $display("\n========================================");
        if (errors == 0)
            $display("ALL TESTS PASSED (expected values calculated from loaded coefficients)");
        else
            $display("TEST FAILED: %0d error(s)", errors);
        $display("========================================");
        $finish;
    end

    initial begin
        #200000;
        $display("ERROR: global simulation timeout");
        $finish;
    end
endmodule