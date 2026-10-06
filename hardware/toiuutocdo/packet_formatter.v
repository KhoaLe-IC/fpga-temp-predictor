// -----------------------------------------------------------------------------
// packet_formatter.v
//
// FPGA -> Host packet:
//   AA 55 81 02 FORECAST_H FORECAST_L CHK
//
// CHK = 81 ^ 02 ^ FORECAST_H ^ FORECAST_L
//
// forecast_valid starts a packet. tx_ready is used to send one byte at a time.
// tx_valid is registered, so a new byte is only issued when tx_valid is low;
// otherwise the formatter would issue a second byte on the cycle before the
// UART transmitter has raised busy, and that byte would be dropped.
// Verilog-2001 compatible.
// -----------------------------------------------------------------------------
module packet_formatter (
    input  wire               clk,
    input  wire               rst_n,

    input  wire               forecast_valid,
    input  wire signed [15:0] forecast_data,

    output reg  [7:0]         tx_data,
    output reg                tx_valid,
    input  wire                tx_ready
);

    reg busy;
    reg [2:0] index;
    reg signed [15:0] saved_forecast;

    wire [7:0] forecast_hi = saved_forecast[15:8];
    wire [7:0] forecast_lo = saved_forecast[7:0];
    wire [7:0] checksum = 8'h81 ^ 8'h02 ^ forecast_hi ^ forecast_lo;

    always @(posedge clk) begin
        if (!rst_n) begin
            busy           <= 1'b0;
            index          <= 3'd0;
            saved_forecast <= 16'sd0;
            tx_data        <= 8'd0;
            tx_valid       <= 1'b0;
        end else begin
            tx_valid <= 1'b0;

            if (!busy) begin
                if (forecast_valid) begin
                    saved_forecast <= forecast_data;
                    busy <= 1'b1;
                    index <= 3'd0;
                end
            end else begin
                // FIX: also require !tx_valid. tx_valid is high for exactly one
                // cycle after a byte is issued; during that cycle uart_tx has
                // not yet set busy, so tx_ready is still 1 and must be ignored.
                if (tx_ready && !tx_valid) begin
                    tx_valid <= 1'b1;

                    case (index)
                        3'd0: tx_data <= 8'hAA;
                        3'd1: tx_data <= 8'h55;
                        3'd2: tx_data <= 8'h81;
                        3'd3: tx_data <= 8'h02;
                        3'd4: tx_data <= forecast_hi;
                        3'd5: tx_data <= forecast_lo;
                        3'd6: tx_data <= checksum;
                        default: tx_data <= 8'h00;
                    endcase

                    if (index == 3'd6) begin
                        busy  <= 1'b0;
                        index <= 3'd0;
                    end else begin
                        index <= index + 3'd1;
                    end
                end
            end
        end
    end
endmodule