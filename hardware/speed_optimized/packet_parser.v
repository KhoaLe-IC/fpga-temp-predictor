// -----------------------------------------------------------------------------
// packet_parser.v
//
// Host -> FPGA packet:
//   AA 55 01 02 TEMP_H TEMP_L CHK
//
// CHK = 01 ^ 02 ^ TEMP_H ^ TEMP_L
//
// TEMP is signed Q8.8, big-endian.
// Example: +25.50 C = 25.5*256 = 0x1980
// packet bytes: AA 55 01 02 19 80 B0
//
// parser_temp_valid is a one-cycle request. It remains pending internally
// until parser_temp_ready is asserted, so the predictor controls acceptance.
// Verilog-2001 compatible.
// -----------------------------------------------------------------------------
module packet_parser (
    input  wire       clk,
    input  wire       rst_n,

    input  wire [7:0] rx_data,
    input  wire       rx_valid,

    output reg signed [15:0] temp_out,
    output reg               temp_valid,
    input  wire               temp_ready,

    output reg               packet_error
);

    localparam ST_IDLE   = 3'd0;
    localparam ST_55     = 3'd1;
    localparam ST_TYPE   = 3'd2;
    localparam ST_LEN    = 3'd3;
    localparam ST_TEMP_H = 3'd4;
    localparam ST_TEMP_L = 3'd5;
    localparam ST_CHK    = 3'd6;

    reg [2:0] state;
    reg [7:0] temp_hi;
    reg [7:0] temp_lo;
    reg [7:0] checksum;

    reg signed [15:0] pending_temp;
    reg pending;

    always @(posedge clk) begin
        if (!rst_n) begin
            state         <= ST_IDLE;
            temp_hi       <= 8'd0;
            temp_lo       <= 8'd0;
            checksum      <= 8'd0;
            pending_temp  <= 16'sd0;
            pending       <= 1'b0;
            temp_out      <= 16'sd0;
            temp_valid    <= 1'b0;
            packet_error  <= 1'b0;
        end else begin
            temp_valid   <= 1'b0;
            packet_error <= 1'b0;

            if (pending && temp_ready) begin
                temp_out   <= pending_temp;
                temp_valid <= 1'b1;
                pending    <= 1'b0;
            end

            if (rx_valid) begin
                case (state)
                    ST_IDLE: begin
                        if (rx_data == 8'hAA)
                            state <= ST_55;
                    end

                    ST_55: begin
                        if (rx_data == 8'h55)
                            state <= ST_TYPE;
                        else if (rx_data == 8'hAA)
                            state <= ST_55;
                        else
                            state <= ST_IDLE;
                    end

                    ST_TYPE: begin
                        if (rx_data == 8'h01)
                            state <= ST_LEN;
                        else
                            state <= ST_IDLE;
                    end

                    ST_LEN: begin
                        if (rx_data == 8'h02)
                            state <= ST_TEMP_H;
                        else
                            state <= ST_IDLE;
                    end

                    ST_TEMP_H: begin
                        temp_hi  <= rx_data;
                        checksum <= 8'h01 ^ 8'h02 ^ rx_data;
                        state    <= ST_TEMP_L;
                    end

                    ST_TEMP_L: begin
                        temp_lo  <= rx_data;
                        checksum <= checksum ^ rx_data;
                        state    <= ST_CHK;
                    end

                    ST_CHK: begin
                        state <= ST_IDLE;

                        if (rx_data == (checksum)) begin
                            if (!pending) begin
                                pending_temp <= {temp_hi, temp_lo};
                                pending      <= 1'b1;
                            end else begin
                                packet_error <= 1'b1;
                            end
                        end else begin
                            packet_error <= 1'b1;
                        end
                    end

                    default: state <= ST_IDLE;
                endcase
            end
        end
    end
endmodule
