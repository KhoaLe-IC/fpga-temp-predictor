`timescale 1ns/1ps

module temp_uart_controller (

    input wire                    clk,
    input wire                    rst_n,

    // =====================================================
    // RX FIFO
    // =====================================================

    input wire [7:0]              rx_fifo_data,
    input wire                    rx_fifo_empty,

    output reg                    rx_fifo_rd_en,

    // =====================================================
    // TX FIFO
    // =====================================================

    output reg [7:0]              tx_fifo_write_data,
    output reg                    tx_fifo_wr_en,

    input wire                    tx_fifo_full,

    // =====================================================
    // PREDICTOR
    // =====================================================

    output reg                    sample_valid,
    output reg signed [15:0]      temp_in,

    input wire                    sample_ready,

    input wire                    forecast_valid,
    input wire signed [15:0]      forecast_out

);


    // =====================================================
    // FSM
    // =====================================================

    localparam [4:0]

        ST_WAIT_1       = 5'd0,
        ST_WAIT_2       = 5'd1,
        ST_WAIT_3       = 5'd2,
        ST_WAIT_4       = 5'd3,

        ST_SEND_SAMPLE  = 5'd4,

        ST_WAIT_RESULT  = 5'd5,

        ST_TX_1         = 5'd6,
        ST_TX_2         = 5'd7,
        ST_TX_3         = 5'd8,
        ST_TX_4         = 5'd9,

        ST_TX_CR        = 5'd10,
        ST_TX_LF        = 5'd11;


    reg [4:0] state;


    // =====================================================
    // SAMPLE BUFFER
    // =====================================================

    reg [15:0] sample_buffer;


    // =====================================================
    // RESULT BUFFER
    // =====================================================

    reg [15:0] result_buffer;


    // =====================================================
    // SAMPLE COUNTER
    //
    // sample_count = number of samples already sent
    // to predictor.
    //
    // Prediction starts from sample #25.
    // =====================================================

    reg [5:0] sample_count;


    // =====================================================
    // HEX CHECK
    // =====================================================

    function is_hex;

        input [7:0] c;

        begin

            if (((c >= "0") && (c <= "9")) ||
                ((c >= "A") && (c <= "F")) ||
                ((c >= "a") && (c <= "f")))

                is_hex = 1'b1;

            else

                is_hex = 1'b0;

        end

    endfunction


    // =====================================================
    // ASCII HEX -> BINARY
    // =====================================================

    function [3:0] hex_to_bin;

        input [7:0] c;

        begin

            if ((c >= "0") && (c <= "9"))

                hex_to_bin = c - "0";

            else if ((c >= "A") && (c <= "F"))

                hex_to_bin = c - "A" + 4'd10;

            else if ((c >= "a") && (c <= "f"))

                hex_to_bin = c - "a" + 4'd10;

            else

                hex_to_bin = 4'd0;

        end

    endfunction


    // =====================================================
    // BINARY -> ASCII HEX
    // =====================================================

    function [7:0] bin_to_hex;

        input [3:0] value;

        begin

            if (value < 10)

                bin_to_hex = "0" + value;

            else

                bin_to_hex = "A" + (value - 10);

        end

    endfunction


    // =====================================================
    // RX FIFO READ ENABLE (COMBINATIONAL)
    //
    // simple_fifo is show-ahead: dout is already the first
    // byte. In every WAIT state the byte at dout is consumed
    // (either captured as hex or discarded), so rd_en must be
    // asserted in the SAME cycle that the byte is looked at.
    // A registered rd_en would pop one cycle late and make
    // the next state read the same byte again.
    // =====================================================

    always @(*) begin

        rx_fifo_rd_en = 1'b0;

        case (state)

            ST_WAIT_1,
            ST_WAIT_2,
            ST_WAIT_3,
            ST_WAIT_4:
                rx_fifo_rd_en = !rx_fifo_empty;

            default:
                rx_fifo_rd_en = 1'b0;

        endcase

    end


    // =====================================================
    // MAIN FSM
    // =====================================================

    always @(posedge clk) begin

        if (!rst_n) begin

            state <= ST_WAIT_1;

            sample_buffer <= 16'd0;

            result_buffer <= 16'd0;

            sample_count <= 6'd0;

            tx_fifo_write_data <= 8'd0;

            tx_fifo_wr_en <= 1'b0;

            sample_valid <= 1'b0;

            temp_in <= 16'sd0;

        end

        else begin

            // -------------------------------------------------
            // DEFAULT PULSE SIGNALS
            // -------------------------------------------------

            tx_fifo_wr_en <= 1'b0;

            sample_valid <= 1'b0;


            case (state)


                // =================================================
                // HEX CHARACTER #1
                // =================================================

                ST_WAIT_1: begin

                    if (!rx_fifo_empty && is_hex(rx_fifo_data)) begin

                        sample_buffer[15:12] <= hex_to_bin(rx_fifo_data);

                        state <= ST_WAIT_2;

                    end

                end


                // =================================================
                // HEX CHARACTER #2
                // =================================================

                ST_WAIT_2: begin

                    if (!rx_fifo_empty && is_hex(rx_fifo_data)) begin

                        sample_buffer[11:8] <= hex_to_bin(rx_fifo_data);

                        state <= ST_WAIT_3;

                    end

                end


                // =================================================
                // HEX CHARACTER #3
                // =================================================

                ST_WAIT_3: begin

                    if (!rx_fifo_empty && is_hex(rx_fifo_data)) begin

                        sample_buffer[7:4] <= hex_to_bin(rx_fifo_data);

                        state <= ST_WAIT_4;

                    end

                end


                // =================================================
                // HEX CHARACTER #4
                // =================================================

                ST_WAIT_4: begin

                    if (!rx_fifo_empty && is_hex(rx_fifo_data)) begin

                        sample_buffer[3:0] <= hex_to_bin(rx_fifo_data);

                        state <= ST_SEND_SAMPLE;

                    end

                end


                // =================================================
                // SEND SAMPLE TO PREDICTOR
                // =================================================

                ST_SEND_SAMPLE: begin

                    if (sample_ready) begin

                        temp_in <= sample_buffer;

                        sample_valid <= 1'b1;


                        if (sample_count < 6'd63)

                            sample_count <= sample_count + 1'b1;


                        // First 24 samples: only build history, no output.
                        if (sample_count < 6'd24) begin

                            state <= ST_WAIT_1;

                        end

                        // Sample #25 and after: predictor computes output.
                        else begin

                            state <= ST_WAIT_RESULT;

                        end

                    end

                end


                // =================================================
                // WAIT FOR PREDICTION
                // =================================================

                ST_WAIT_RESULT: begin

                    if (forecast_valid) begin

                        result_buffer <= forecast_out;

                        state <= ST_TX_1;

                    end

                end


                // =================================================
                // TX RESULT HEX #1
                // =================================================

                ST_TX_1: begin

                    if (!tx_fifo_full) begin

                        tx_fifo_write_data <=
                            bin_to_hex(result_buffer[15:12]);

                        tx_fifo_wr_en <= 1'b1;

                        state <= ST_TX_2;

                    end

                end


                // =================================================
                // TX RESULT HEX #2
                // =================================================

                ST_TX_2: begin

                    if (!tx_fifo_full) begin

                        tx_fifo_write_data <=
                            bin_to_hex(result_buffer[11:8]);

                        tx_fifo_wr_en <= 1'b1;

                        state <= ST_TX_3;

                    end

                end


                // =================================================
                // TX RESULT HEX #3
                // =================================================

                ST_TX_3: begin

                    if (!tx_fifo_full) begin

                        tx_fifo_write_data <=
                            bin_to_hex(result_buffer[7:4]);

                        tx_fifo_wr_en <= 1'b1;

                        state <= ST_TX_4;

                    end

                end


                // =================================================
                // TX RESULT HEX #4
                // =================================================

                ST_TX_4: begin

                    if (!tx_fifo_full) begin

                        tx_fifo_write_data <=
                            bin_to_hex(result_buffer[3:0]);

                        tx_fifo_wr_en <= 1'b1;

                        state <= ST_TX_CR;

                    end

                end


                // =================================================
                // CARRIAGE RETURN
                // =================================================

                ST_TX_CR: begin

                    if (!tx_fifo_full) begin

                        tx_fifo_write_data <= 8'h0D;

                        tx_fifo_wr_en <= 1'b1;

                        state <= ST_TX_LF;

                    end

                end


                // =================================================
                // LINE FEED
                // =================================================

                ST_TX_LF: begin

                    if (!tx_fifo_full) begin

                        tx_fifo_write_data <= 8'h0A;

                        tx_fifo_wr_en <= 1'b1;

                        // Do not reset predictor: the next sample
                        // continues the sliding-window history.

                        state <= ST_WAIT_1;

                    end

                end


                // =================================================
                // DEFAULT
                // =================================================

                default: begin

                    state <= ST_WAIT_1;

                end

            endcase

        end

    end

endmodule