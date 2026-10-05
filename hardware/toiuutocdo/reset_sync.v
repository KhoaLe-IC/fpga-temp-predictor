// -----------------------------------------------------------------------------
// reset_sync.v
// 2-flop synchronizer for an active-low asynchronous physical reset input.
// Output rst_n_sync is an active-low reset suitable for the synchronous RTL.
// Verilog-2001 compatible.
// -----------------------------------------------------------------------------
module reset_sync (
    input  wire clk,
    input  wire reset_n_in,
    output wire reset_n_sync
);
    reg [1:0] sync_ff;

    always @(posedge clk) begin
        sync_ff[0] <= reset_n_in;
        sync_ff[1] <= sync_ff[0];
    end

    assign reset_n_sync = sync_ff[1];
endmodule
