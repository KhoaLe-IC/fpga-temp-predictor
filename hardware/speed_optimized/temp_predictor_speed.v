// -----------------------------------------------------------------------------
// temp_predictor_speed.v
// Speed-optimized fixed-coefficient OLS temperature predictor (Verilog-2001)
//
//   T^(t+3) = T(t-21) + a*[T(t)-T(t-24)] + b*[T(t)-T(t-3)] + c
//
// Numerical contract (spec section 2):
//   temp_in / forecast_out : signed Q8.8
//   COEF_A, COEF_B         : signed Q2.14
//   COEF_C                 : signed Q8.8
//   S = A*D1 + B*D2 + (T21<<<14) + (C<<<14)   (35-bit, no narrowing before sum)
//   forecast_out = sat16(S >>> 14)            (arithmetic shift, then saturate)
//
// Pipeline (II = 1). "Edge e" = rising edge on which a sample is accepted.
//   e     : stage0  snapshot of T(t), T(t-3), T(t-21), T(t-24)
//   e+1   : stage1  D1, D2 (two parallel 17-bit subtractors)
//   e+2   : stage2  P1 = A*D1, P2 = B*D2 (two 17x16 multipliers), base = (T21+C)<<14
//   e+3   : stage3  P1 + P2
//   e+4   : stage4  S = (P1+P2) + base
//   e+5   : stage5  shift + saturate -> forecast_out / forecast_valid
// forecast_valid is therefore visible 5 clock edges after the accepting edge
// (6 register stages counting the capture stage)  => L_speed = 6 <= 8.
// -----------------------------------------------------------------------------
(* multstyle = "dsp" *)
module temp_predictor_speed #(
    // Coefficients are read ONCE at elaboration/power-up from a text file with
    // three hex words (16-bit, two's complement), in this order:
    //     line 1: A  (Q2.14)    line 2: B  (Q2.14)    line 3: C  (Q8.8)
    // "//" comments are allowed. The file is written by `ols_ref quant a b c`.
    // Simulation : path is relative to the simulator working directory.
    // Quartus    : path is relative to the project directory; changing the file
    //              requires a re-compile (coefficients are static in hardware).
    parameter COEF_FILE = "coeffs.txt"
) (
    input  wire               clk,
    input  wire               rst_n,           // active-low, synchronous
    input  wire               sample_valid,
    output wire               sample_ready,
    input  wire signed [15:0] temp_in,
    output wire               forecast_valid,
    output wire signed [15:0] forecast_out
);

    // ------------------------------------------------------------------
    // Coefficients from text file (static after initialization)
    // ------------------------------------------------------------------
    reg [15:0] coef_mem [0:2];
    initial $readmemh(COEF_FILE, coef_mem);

    wire signed [15:0] COEF_A = coef_mem[0];   // Q2.14
    wire signed [15:0] COEF_B = coef_mem[1];   // Q2.14
    wire signed [15:0] COEF_C = coef_mem[2];   // Q8.8

    // ------------------------------------------------------------------
    // Input handshake + warm-up counter
    // ------------------------------------------------------------------
    reg        ready_r;
    reg  [4:0] cnt;                 // accepted samples so far, saturates at 24
    wire       accept = sample_valid & ready_r;

    assign sample_ready = ready_r;

    always @(posedge clk) begin
        if (!rst_n) begin
            ready_r <= 1'b0;
            cnt     <= 5'd0;
        end else begin
            ready_r <= 1'b1;
            if (accept && cnt != 5'd24)
                cnt <= cnt + 5'd1;
        end
    end

    // ------------------------------------------------------------------
    // 25 x 16-bit history. hist[0]=T(t) after an acceptance.
    // No reset needed: nothing is emitted until cnt reaches 24.
    // ------------------------------------------------------------------
    reg signed [15:0] hist [0:24];

    always @(posedge clk) begin
        if (accept) begin
            hist[24] <= hist[23];
            hist[23] <= hist[22];
            hist[22] <= hist[21];
            hist[21] <= hist[20];
            hist[20] <= hist[19];
            hist[19] <= hist[18];
            hist[18] <= hist[17];
            hist[17] <= hist[16];
            hist[16] <= hist[15];
            hist[15] <= hist[14];
            hist[14] <= hist[13];
            hist[13] <= hist[12];
            hist[12] <= hist[11];
            hist[11] <= hist[10];
            hist[10] <= hist[9];
            hist[9]  <= hist[8];
            hist[8]  <= hist[7];
            hist[7]  <= hist[6];
            hist[6]  <= hist[5];
            hist[5]  <= hist[4];
            hist[4]  <= hist[3];
            hist[3]  <= hist[2];
            hist[2]  <= hist[1];
            hist[1]  <= hist[0];
            hist[0]  <= temp_in;
        end
    end

    // ------------------------------------------------------------------
    // Stage 0: snapshot taps (pre-shift indices: new T(t-3) = old hist[2], ...)
    // ------------------------------------------------------------------
    reg signed [15:0] s0_t, s0_t3, s0_t21, s0_t24;
    reg               v0;
    always @(posedge clk) begin
        s0_t   <= temp_in;
        s0_t3  <= hist[2];
        s0_t21 <= hist[20];
        s0_t24 <= hist[23];
        if (!rst_n) v0 <= 1'b0;
        else        v0 <= accept & (cnt == 5'd24);   // 25th accepted sample onward
    end

    // ------------------------------------------------------------------
    // Stage 1: differences (explicit 17-bit sign extension)
    // ------------------------------------------------------------------
    reg signed [16:0] s1_d1, s1_d2;
    reg signed [15:0] s1_t21;
    reg               v1;
    always @(posedge clk) begin
        s1_d1  <= {s0_t[15], s0_t} - {s0_t24[15], s0_t24};
        s1_d2  <= {s0_t[15], s0_t} - {s0_t3[15],  s0_t3};
        s1_t21 <= s0_t21;
        if (!rst_n) v1 <= 1'b0; else v1 <= v0;
    end

    // ------------------------------------------------------------------
    // Stage 2: two parallel signed 17x16 multipliers + constant base term
    //   base = (T21 <<< 14) + (C <<< 14) = (T21 + C) <<< 14   (exact)
    // ------------------------------------------------------------------
    reg signed [32:0] s2_p1, s2_p2;
    reg signed [34:0] s2_base;
    reg               v2;
    wire signed [16:0] tc_sum = {s1_t21[15], s1_t21} + {COEF_C[15], COEF_C};
    always @(posedge clk) begin
        s2_p1   <= COEF_A * s1_d1;                       // 16 x 17 -> 33 bit
        s2_p2   <= COEF_B * s1_d2;
        s2_base <= {{4{tc_sum[16]}}, tc_sum, 14'b0};     // 4 + 17 + 14 = 35 bit
        if (!rst_n) v2 <= 1'b0; else v2 <= v1;
    end

    // ------------------------------------------------------------------
    // Stage 3: P1 + P2 (34 bit)
    // ------------------------------------------------------------------
    reg signed [33:0] s3_p;
    reg signed [34:0] s3_base;
    reg               v3;
    always @(posedge clk) begin
        s3_p    <= {s2_p1[32], s2_p1} + {s2_p2[32], s2_p2};
        s3_base <= s2_base;
        if (!rst_n) v3 <= 1'b0; else v3 <= v2;
    end

    // ------------------------------------------------------------------
    // Stage 4: full 35-bit accumulator S
    // ------------------------------------------------------------------
    reg signed [34:0] s4_s;
    reg               v4;
    always @(posedge clk) begin
        s4_s <= {s3_p[33], s3_p} + s3_base;
        if (!rst_n) v4 <= 1'b0; else v4 <= v3;
    end

    // ------------------------------------------------------------------
    // Stage 5: arithmetic shift >>> 14 and saturation to 16 bit
    // ------------------------------------------------------------------
    wire signed [34:0] s4_sh = s4_s >>> 14;
    reg  signed [15:0] s5_out;
    reg                v5;
    always @(posedge clk) begin
        if (s4_sh > 35'sd32767)       s5_out <= 16'sh7FFF;
        else if (s4_sh < -35'sd32768) s5_out <= 16'sh8000;
        else                          s5_out <= s4_sh[15:0];
        if (!rst_n) v5 <= 1'b0; else v5 <= v4;
    end

    assign forecast_valid = v5;
    assign forecast_out   = s5_out;

endmodule