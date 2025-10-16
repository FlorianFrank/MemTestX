module tb_mdio();

reg clk_125MHz = 1'b0;
reg start = 1'b0;
wire active;
reg reset = 1'b1;
reg read_write = 1'b1; // WRITE
reg [4:0] phy_address = 5'b10101;
reg [4:0] register_address = 5'b10101;
reg [15:0] data = 16'b1010101010101010;
wire mdio_out;
wire mdc;
wire[3:0] state_mdio;

initial begin
    $dumpfile("tb_mdio.vcd");
    $dumpvars(0,tb_mdio);
    #1;
    start <= 1'b1;
    #8;
    start <= 1'b0;
    #400;
    $finish;
end

initial begin
    forever #1 clk_125MHz = ~clk_125MHz;
end

mdio #(.CLOCK_DIVIDER(1)) mdio_inst (
   .clk_125MHz(clk_125MHz),
   .start(start),
   .active(active),
   .reset(reset),

   .read_write(read_write),
   .phy_address(phy_address),
   .register_address(register_address),
   .data(data),

   .mdio(mdio_out),
   .mdc(mdc),
   .state_out(state_mdio)
);

endmodule