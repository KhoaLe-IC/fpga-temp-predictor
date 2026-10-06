`timescale 1ns/1ps

module top_temp_predictor_uart (

    input  wire CLOCK_50,

    input  wire UART_RX,

    output wire UART_TX

);


    // =========================================================
    // POWER-ON RESET
    //
    // Holds rst_n low for 128 clocks after power-up / sim start,
    // then releases it. (reg initial value works on FPGA and
    // in simulation.)
    // =========================================================

    reg [7:0] por_cnt = 8'd0;

    always @(posedge CLOCK_50) begin

        if (!por_cnt[7])
            por_cnt <= por_cnt + 1'b1;

    end

    wire rst_n;

    assign rst_n = por_cnt[7];


    // =========================================================
    // UART RX INPUT SYNCHRONIZER (2 flip-flops)
    // =========================================================

    reg [1:0] rx_sync = 2'b11;

    always @(posedge CLOCK_50) begin

        rx_sync <= {rx_sync[0], UART_RX};

    end

    wire uart_rx_in;

    assign uart_rx_in = rx_sync[1];


    // =========================================================
    // UART RX
    // =========================================================

    wire [7:0] uart_rx_data;

    wire uart_rx_valid;


    uart_rx #(
        .CLK_FREQ(50000000),
        .BAUD_RATE(115200)
    ) uart_rx_inst (

        .clk(CLOCK_50),

        .rst_n(rst_n),

        .rx(uart_rx_in),

        .data_out(uart_rx_data),

        .data_valid(uart_rx_valid)

    );


    // =========================================================
    // RX FIFO
    // =========================================================

    wire [7:0] rx_fifo_data;

    wire rx_fifo_empty;

    wire rx_fifo_full;

    wire rx_fifo_rd_en;

    wire [8:0] rx_fifo_count;


    simple_fifo #(
        .DATA_WIDTH(8),
        .ADDR_WIDTH(8)
    ) rx_fifo_inst (

        .clk(CLOCK_50),

        .rst_n(rst_n),

        .wr_en(uart_rx_valid),

        .din(uart_rx_data),

        .rd_en(rx_fifo_rd_en),

        .dout(rx_fifo_data),

        .empty(rx_fifo_empty),

        .full(rx_fifo_full),

        .count(rx_fifo_count)

    );


    // =========================================================
    // CONTROLLER -> TX FIFO
    // =========================================================

    wire [7:0] controller_tx_data;

    wire controller_tx_wr_en;

    wire tx_fifo_full;


    // =========================================================
    // TX FIFO
    // =========================================================

    wire [7:0] tx_fifo_data;

    wire tx_fifo_empty;

    wire tx_fifo_rd_en;

    wire [9:0] tx_fifo_count;


    simple_fifo #(
        .DATA_WIDTH(8),
        .ADDR_WIDTH(9)
    ) tx_fifo_inst (

        .clk(CLOCK_50),

        .rst_n(rst_n),

        .wr_en(controller_tx_wr_en),

        .din(controller_tx_data),

        .rd_en(tx_fifo_rd_en),

        .dout(tx_fifo_data),

        .empty(tx_fifo_empty),

        .full(tx_fifo_full),

        .count(tx_fifo_count)

    );


    // =========================================================
    // UART TX
    // =========================================================

    wire uart_tx_busy;


    /*
     * If TX FIFO contains data and UART is idle:
     *
     *     send FIFO front byte
     *
     * and simultaneously pop it.
     */

    assign tx_fifo_rd_en =
        (!tx_fifo_empty) &&
        (!uart_tx_busy);


    uart_tx #(
        .CLK_FREQ(50000000),
        .BAUD_RATE(115200)
    ) uart_tx_inst (

        .clk(CLOCK_50),

        .rst_n(rst_n),

        .data_in(tx_fifo_data),

        .data_valid(tx_fifo_rd_en),

        .tx(UART_TX),

        .busy(uart_tx_busy)

    );


    // =========================================================
    // PREDICTOR SIGNALS
    // =========================================================

    wire sample_valid;

    wire sample_ready;

    wire signed [15:0] temp_in;

    wire forecast_valid;

    wire signed [15:0] forecast_out;


    // =========================================================
    // CONTROLLER
    // =========================================================

    temp_uart_controller controller_inst (

        .clk(CLOCK_50),

        .rst_n(rst_n),


        // -------------------------
        // RX FIFO
        // -------------------------

        .rx_fifo_data(rx_fifo_data),

        .rx_fifo_empty(rx_fifo_empty),

        .rx_fifo_rd_en(rx_fifo_rd_en),


        // -------------------------
        // TX FIFO
        // -------------------------

        .tx_fifo_write_data(controller_tx_data),

        .tx_fifo_wr_en(controller_tx_wr_en),

        .tx_fifo_full(tx_fifo_full),


        // -------------------------
        // Predictor
        // -------------------------

        .sample_valid(sample_valid),

        .temp_in(temp_in),

        .sample_ready(sample_ready),

        .forecast_valid(forecast_valid),

        .forecast_out(forecast_out)

    );


    // =========================================================
    // TEMPERATURE PREDICTOR
    // =========================================================

    temp_predictor_resource predictor_inst (

        .clk(CLOCK_50),

        .rst_n(rst_n),

        .sample_valid(sample_valid),

        .sample_ready(sample_ready),

        .temp_in(temp_in),

        .forecast_valid(forecast_valid),

        .forecast_out(forecast_out)

    );


endmodule