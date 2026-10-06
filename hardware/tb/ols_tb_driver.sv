`timescale 1ns/1ps
// Shared black-box scoreboard/stimulus. No DUT-internal signals are accessed.
module ols_tb_driver #(
    parameter bit SPEED_MODE = 1,
    parameter integer A_Q = 8192, B_Q = 3277, C_Q = 0,
    parameter integer LATENCY = 5, MAX_LATENCY = 8, MAX_II = 1,
    parameter integer QUEUE_SIZE = 65536
) (
    output logic clk = 0, rst_n = 0, sample_valid = 0,
    output logic signed [15:0] temp_in = 0,
    input wire sample_ready, forecast_valid,
    input wire signed [15:0] forecast_out
);
    always #10 clk = ~clk; // DE2 board clock: 50 MHz

    import "DPI-C" function int ols_ref_selftest();
    import "DPI-C" function chandle ols_ref_create(input int a, b, c);
    import "DPI-C" function void ols_ref_reset(input chandle handle);
    import "DPI-C" function int ols_ref_push(input chandle handle, input int temperature,
                                           output int prediction,
                                           output longint sum, output longint scaled);
    import "DPI-C" function void ols_ref_destroy(input chandle handle);
    chandle model_handle = null;
    integer ref_valid, ref_prediction;
    logic signed [15:0] expected [0:QUEUE_SIZE-1];
    integer due [0:QUEUE_SIZE-1], sample_number [0:QUEUE_SIZE-1];
    integer head = 0, tail = 0, epoch_samples = 0, cycle = 0;
    integer total_samples = 0, eligible = 0, checked = 0, aborted = 0;
    integer stalls = 0, reset_events = 0, negative_inputs = 0;
    integer sat_hi = 0, sat_lo = 0, negative_fraction = 0;
    integer phase = 0, previous_phase = -1, previous_accept = -1;
    integer continuous_checked = 0;
    bit file_enable = 0;
    integer file_has_result = 0, file_result = 0;
    bit reset_seen = 0;
    bit first_active_edge;
    bit diagnostic_reset_bubble = 0;
    longint signed raw_sum, scaled;
    logic signed [15:0] predicted;
    logic [31:0] rng = 32'h6b8b4567;
    string vector_path, vcd_path, results_path;
    integer results_fd = 0;
    bit stalled_previous = 0;
    logic signed [15:0] stalled_value;


    // Prediction arithmetic and accepted-sample history live in C++.
    // SV owns transaction indexing, protocol checks, and the timing queue.
    final begin
        if (model_handle != null) ols_ref_destroy(model_handle);
        if (results_fd != 0) $fclose(results_fd);
    end

    function automatic integer random_sample;
        begin
            // Local deterministic PRNG: independent of simulator seed APIs.
            rng = rng * 32'd1664525 + 32'd1013904223;
            random_sample = int'($signed(rng[31:16]));
        end
    endfunction

    // Sample ready/input BEFORE the DUT's nonblocking updates, inspect outputs
    // AFTER them. Stimulus changes only on falling edges, avoiding DUT races.
    always @(posedge clk) begin
        cycle = cycle + 1;
        if (!rst_n) begin
            if (!reset_seen) begin
                reset_events = reset_events + 1;
                aborted = aborted + tail - head;
            end
            reset_seen = 1;
            head = 0; tail = 0; epoch_samples = 0;
            previous_accept = -1; previous_phase = -1; stalled_previous = 0;
            ols_ref_reset(model_handle);
            #1;
            if (forecast_valid !== 1'b0)
                $fatal(1, "RESET: forecast_valid must clear at reset edge (cycle %0d)", cycle);
        end else begin
            first_active_edge = reset_seen;
            reset_seen = 0;
            if (stalled_previous && (!sample_valid || temp_in !== stalled_value))
                $fatal(1, "STIMULUS: pending input changed before acceptance");
            stalled_previous = sample_valid && !sample_ready;
            stalled_value = temp_in;
            if (sample_ready !== 1'b0 && sample_ready !== 1'b1)
                $fatal(1, "UNKNOWN: sample_ready at cycle %0d", cycle);
            if (SPEED_MODE && sample_ready !== 1'b1 &&
                !(diagnostic_reset_bubble && first_active_edge && sample_ready === 1'b0))
                $fatal(1, "READY: speed core must stay ready, cycle %0d", cycle);
            if (!SPEED_MODE && tail > head && due[head] > cycle && sample_ready !== 1'b0)
                $fatal(1, "BUSY: resource core ready while inference is pending, cycle %0d", cycle);
            if (sample_valid && !sample_ready) stalls = stalls + 1;
            if (sample_valid && sample_ready) begin
                if ($isunknown(temp_in)) $fatal(1, "UNKNOWN: accepted temperature");
                if ($signed(temp_in) < 0) negative_inputs = negative_inputs + 1;
                total_samples = total_samples + 1;
                ref_valid = ols_ref_push(model_handle, int'($signed(temp_in)),
                                         ref_prediction, raw_sum, scaled);
                if (ref_valid < 0) $fatal(1, "DPI: C++ reference rejected an accepted sample");
                epoch_samples = epoch_samples + 1;
                if (ref_valid != int'(epoch_samples >= 25))
                    $fatal(1, "DPI: reference warm-up count disagrees with SV transaction count");
                if (file_enable && file_has_result != int'(epoch_samples >= 25))
                    $fatal(1, "VECTOR: warm-up flag disagrees at sample %0d", epoch_samples);
                if (epoch_samples >= 25) begin
                    if (phase == 3 && previous_phase == 3 && previous_accept >= 0 &&
                        cycle - previous_accept > MAX_II)
                        $fatal(1, "II: sustained acceptance gap %0d exceeds %0d",
                               cycle-previous_accept, MAX_II);
                    previous_accept = cycle; previous_phase = phase;
                    predicted = ref_prediction[15:0];
                    if (scaled > 32767) sat_hi = sat_hi + 1;
                    if (scaled < -32768) sat_lo = sat_lo + 1;
                    if (raw_sum < 0 && raw_sum % 16384 != 0)
                        negative_fraction = negative_fraction + 1;
                    if (file_enable && int'($signed(predicted)) != file_result)
                        $fatal(1, "ORACLE: live DPI/file disagree sample %0d: DPI=%0d file=%0d",
                               epoch_samples, $signed(predicted), file_result);
                    if (tail >= QUEUE_SIZE) $fatal(1, "Scoreboard capacity exceeded; increase QUEUE_SIZE");
                    expected[tail] = predicted;
                    due[tail] = cycle + LATENCY;
                    sample_number[tail] = epoch_samples;
                    tail = tail + 1; eligible = eligible + 1;
                end
            end
            #1;
            if (forecast_valid !== 1'b0 && forecast_valid !== 1'b1)
                $fatal(1, "UNKNOWN: forecast_valid at cycle %0d", cycle);
            if (forecast_valid === 1'b1) begin
                if (head == tail) $fatal(1, "UNEXPECTED: output without an eligible input at cycle %0d", cycle);
                if (due[head] != cycle)
                    $fatal(1, "LATENCY: sample %0d expected cycle %0d, observed %0d",
                           sample_number[head], due[head], cycle);
                if (forecast_out !== expected[head])
                    $fatal(1, "DATA: sample %0d expected %0d (0x%04h), got %0d (0x%04h)",
                           sample_number[head], $signed(expected[head]), expected[head],
                           $signed(forecast_out), forecast_out);
                if (phase == 3) continuous_checked = continuous_checked + 1;
                if (phase == 7 && results_fd != 0)
                    $fdisplay(results_fd, "%0d,%0d,%0d", sample_number[head],
                              $signed(forecast_out), cycle);
                head = head + 1; checked = checked + 1;
            end
            if (head < tail && due[head] <= cycle)
                $fatal(1, "MISSING: sample %0d output due at cycle %0d", sample_number[head], due[head]);
        end
    end

    task automatic idle(input integer clocks);
        integer k;
        begin
            for (k = 0; k < clocks; k = k + 1) begin
                @(negedge clk); sample_valid = 0;
                temp_in = 16'(random_sample()); // Invalid bus changes must not affect history.
                @(posedge clk); #2;
            end
        end
    endtask

    task automatic send_sample(input integer value);
        integer attempts;
        bit accepted;
        begin
            attempts = 0; accepted = 0;
            // Data and valid are held stable across every backpressure cycle.
            @(negedge clk); temp_in = value[15:0]; sample_valid = 1;
            while (!accepted) begin
                @(posedge clk);
                accepted = (sample_ready === 1'b1);
                #2;
                attempts = attempts + 1;
                if (attempts > MAX_II + 2) $fatal(1, "TIMEOUT: input not accepted within %0d clocks", attempts);
            end
        end
    endtask

    task automatic drain;
        begin
            idle(MAX_LATENCY + 3);
            if (head != tail) $fatal(1, "DRAIN: pending outputs remain");
        end
    endtask

    task automatic apply_reset;
        begin
            @(negedge clk); rst_n = 0; sample_valid = 1; temp_in = 16'sd2468; file_enable = 0;
            repeat (2) @(negedge clk);
            sample_valid = 0; rst_n = 1;
        end
    endtask

    task automatic replay_cpp_vectors(input string path);
        integer fd, rc, va, vb, vc, value, flag, result, rows;
        begin
            fd = $fopen(path, "r");
            if (fd == 0) $fatal(1, "Cannot open C++ vector file: %s", path);
            rc = $fscanf(fd, "%d %d %d\n", va, vb, vc);
            if (rc != 3 || va != A_Q || vb != B_Q || vc != C_Q)
                $fatal(1, "VECTOR: coefficient header does not match testbench");
            apply_reset(); phase = 7; rows = 0;
            while (!$feof(fd)) begin
                rc = $fscanf(fd, "%d %d %d\n", value, flag, result);
                if (rc == 3) begin
                    if (value < -32768 || value > 32767 || flag < 0 || flag > 1 ||
                        result < -32768 || result > 32767)
                        $fatal(1, "VECTOR: illegal row %0d", rows+1);
                    file_enable = 1; file_has_result = flag; file_result = result;
                    send_sample(value); rows = rows + 1;
                end else if (rc != -1) $fatal(1, "VECTOR: malformed row %0d", rows+1);
            end
            // Drop valid before disabling the metadata for the last accepted row.
            @(negedge clk); sample_valid = 0; file_enable = 0;
            $fclose(fd); drain();
            if (rows < 25) $fatal(1, "VECTOR: file contains no eligible forecast");
            $display("C++ replay: %0d samples checked", rows);
        end
    endtask

    integer i, value, gap;
    initial begin
        diagnostic_reset_bubble = $test$plusargs("DIAGNOSTIC_RESET_BUBBLE");
        if (diagnostic_reset_bubble && SPEED_MODE)
            $display("DIAGNOSTIC ONLY: tolerating one speed-ready bubble at each reset release; not spec acceptance");
        if (LATENCY < 1 || LATENCY > MAX_LATENCY) $fatal(1, "Invalid LATENCY parameter");
        if (A_Q < -32768 || A_Q > 32767 || B_Q < -32768 || B_Q > 32767 ||
            C_Q < -32768 || C_Q > 32767) $fatal(1, "Coefficients must be signed 16-bit integers");
        if (ols_ref_selftest() != 1) $fatal(1, "DPI: C++ arithmetic/history self-test failed");
        model_handle = ols_ref_create(A_Q, B_Q, C_Q);
        if (model_handle == null) $fatal(1, "DPI: could not create C++ reference model");
        if ($value$plusargs("RESULTS=%s", results_path)) begin
            results_fd = $fopen(results_path, "w");
            if (results_fd == 0) $fatal(1, "Cannot open results CSV");
            $fdisplay(results_fd, "sample_index,prediction_raw,output_cycle");
        end
        if ($value$plusargs("VCD=%s", vcd_path)) begin
            $dumpfile(vcd_path); $dumpvars;
        end
        if (SPEED_MODE) $display("TEST speed A=%0d B=%0d C=%0d latency=%0d", A_Q, B_Q, C_Q, LATENCY);
        else $display("TEST resource A=%0d B=%0d C=%0d latency=%0d", A_Q, B_Q, C_Q, LATENCY);
        apply_reset(); phase = 1;
        for (i = 0; i < 24; i = i + 1) send_sample(20*256 + i);
        drain(); // Must produce zero outputs.
        if (checked != 0) $fatal(1, "Warm-up produced output");
        send_sample(21*256); drain(); // Exactly the 25th accepted sample.
        if (checked != 1) $fatal(1, "25th-sample boundary failed");

        phase = 2;
        for (i = 0; i < 70; i = i + 1) send_sample(-10*256);
        for (i = 0; i < 70; i = i + 1) send_sample(i*137 - 4000);
        // Extreme differences exercise sign extension, product width, saturation.
        for (i = 0; i < 150; i = i + 1)
            send_sample((i % 25 < 12) ? -32768 : 32767);
        drain();

        phase = 3;
        for (i = 0; i < 4096; i = i + 1) send_sample(random_sample());
        drain();
        if (continuous_checked < 4000) $fatal(1, "Sustained-traffic test did not complete");
        phase = 4;
        for (i = 0; i < 300; i = i + 1) begin
            value = random_sample(); gap = int'(rng[2:0]);
            idle(gap); send_sample(value);
        end
        drain();
        phase = 5;
        for (i = 0; i < 30; i = i + 1) begin
            send_sample(random_sample()); idle(MAX_LATENCY + 2);
        end
        drain();

        // Reset halfway through warm-up, then require a fresh 25 samples.
        apply_reset(); phase = 6;
        for (i = 0; i < 12; i = i + 1) send_sample(1234);
        apply_reset();
        for (i = 0; i < 24; i = i + 1) send_sample(-3456);
        drain();
        // Accept first eligible input, then reset before its result can emerge.
        send_sample(7890); apply_reset(); drain();
        for (i = 0; i < 60; i = i + 1) send_sample(random_sample());
        drain();
        if ($value$plusargs("VECTORS=%s", vector_path)) replay_cpp_vectors(vector_path);
        else $display("NOTE: no +VECTORS supplied; live DPI-C reference used for all accepted samples.");
        if (eligible != checked + aborted) $fatal(1, "Accounting mismatch");
        if (!SPEED_MODE && stalls == 0) $fatal(1, "Resource backpressure was never exercised");
        if (aborted == 0) $fatal(1, "Reset never aborted an in-flight forecast");
        if (A_Q == 8192 && B_Q == 3277 && C_Q == 0 &&
            (sat_hi == 0 || sat_lo == 0 || negative_fraction == 0))
            $fatal(1, "Default-coefficient arithmetic coverage was incomplete");
        $display("PASS: accepted=%0d checked=%0d reset_aborted=%0d stalls=%0d resets=%0d",
                 total_samples, checked, aborted, stalls, reset_events);
        $display("Arithmetic bins: negative_inputs=%0d sat_hi=%0d sat_lo=%0d negative_fraction=%0d",
                 negative_inputs, sat_hi, sat_lo, negative_fraction);
        $finish;
    end
    initial begin
        #100000000; $fatal(1, "GLOBAL TIMEOUT");
    end
endmodule
