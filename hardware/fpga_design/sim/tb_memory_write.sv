`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/31/2025 02:49:29 PM
// Design Name: 
// Module Name: tb_memory_write
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module tb_memory_write();
    
    
    localparam DATA_BUS_SIZE = 8;
    localparam ADDRESS_BUS_SIZE = 15;
    localparam CLOCK_CONFIG_WIDTH = 16;
    localparam DATA_BUS_SIZE_OUT = 8;
    
    logic clk;
    logic reset;
    logic start_write;

    logic [DATA_BUS_SIZE-1:0] value_write;
    logic [ADDRESS_BUS_SIZE-1:0] address_write;


    logic [DATA_BUS_SIZE_OUT-1:0] dlines;
    //% Address lines to select the specific cell.
    logic [ADDRESS_BUS_SIZE-1:0] alines;
    //% Chip enable signal which is set accordingly.
    logic ce;
    //% Output enable signal set by the memory controller.
    logic oe;
    //% Write enable signal set by the memory controller.
    logic we;


    logic[ADDRESS_BUS_SIZE-1:0] max_address;

    //% Wire indicating whether the data was written.
    logic write_continously;
    logic ceDriven;
    logic [CLOCK_CONFIG_WIDTH-1:0] tnext;
    logic [CLOCK_CONFIG_WIDTH-1:0] tStart; // Delay before start
    logic [CLOCK_CONFIG_WIDTH-1:0] tac;    // Access time
    logic [CLOCK_CONFIG_WIDTH-1:0] tas;     // Address setup time
    logic [CLOCK_CONFIG_WIDTH-1:0] tah;     // Address hold time
    logic [CLOCK_CONFIG_WIDTH-1:0] tds;     // Data setup time
    logic [CLOCK_CONFIG_WIDTH-1:0] tdh;     // Data hold time
    logic [CLOCK_CONFIG_WIDTH-1:0] tpwd;    // Pulse width duration

    logic write_active;
    logic write_done;
    logic[3:0] state_mem;

    initial begin
    
    clk <= 1;
    reset <= 0;
    start_write <= 0;

    value_write <= 8'h55;
    address_write <= 15'h2;

    dlines <= {DATA_BUS_SIZE_OUT{1'h0}};
    alines <= {ADDRESS_BUS_SIZE{1'h0}};
    ce <= 1'h1;
    oe <= 1'h1;
    we <= 1'h1;


    max_address <= 15'h0a;

    write_active <= 1'h0;
    write_done <= 1'h0;
    state_mem <= 4'h0;
    
    //% Wire indicating whether the data was written.
    write_continously <= 1'h1;
    ceDriven <= 1'h1;
    tas <= 16'h1;
    tah <= 16'd4; // TODO not implemented
    tac <= 16'd12; // at least 30 ns    //tac + tds = cycle = TELEH 70 ns
    tds <= 16'd16; // at least 40 ns 
    tdh <= 16'h1; // zero but wait one clock cycle 
    tnext <= 16'd32; // tELEH at least 80 ns
    tStart <= 16'h0; 
    tpwd <= 16'h0; // not implemented
    
    #5
    start_write <= 1'h1;
    #5
    start_write <= 1'h0;
    #500
    $finish;
    end
    
    initial begin 
        forever #1.25 clk = ~clk;
    end

    memory_write_top_module  #(.FREQ_CLK1(100), .FREQ_CLK2(400), .ADDRESS_BUS_SIZE(15), .DATA_BUS_SIZE(8), .DATA_BUS_SIZE_OUT(8), .CLOCK_CONFIG_WIDTH(16)) mem_write_top_module (.*);
  
  
endmodule
