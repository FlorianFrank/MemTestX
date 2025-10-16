`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/22/2025 03:49:54 PM
// Design Name: 
// Module Name: tb_memory_read
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

`define CLOCK_CONFIG_WIDTH 16
`define ADDRESS_BUS_WIDTH  32
`define DATA_BUS_WIDTH      16

module tb_memory_read();


    //% Input clock which drives the memory controller.
    logic clk1;
    logic clk2;
    logic start;
    logic reset;

    //% The value which should be read from the // TODO.
    logic[`ADDRESS_BUS_WIDTH:0] value;
    

    //% Data lines from which the data should be read
    logic[15:0] dlines;

    logic[`ADDRESS_BUS_WIDTH-1:0] address;

    //% Address lines specifying the address currently used. (only the Rohm FRAM is supported with an address width of 15 bit)
    logic[`ADDRESS_BUS_WIDTH-1:0] alines;

    //% Chip enable signal.
    logic ce;

    //% Output enable signal.
    logic oe;

    //% Write enable signal
    logic we;
   
    logic ceDriven;
    // Timing Parameter
    logic[`CLOCK_CONFIG_WIDTH-1:0] tStart;
    //input wire[CLOCK_CONFIG_WIDTH-1:0] tah,
    logic[`CLOCK_CONFIG_WIDTH-1:0] tas;
    logic[`CLOCK_CONFIG_WIDTH-1:0] toed;
    logic[`CLOCK_CONFIG_WIDTH-1:0] tprc;
    //input wire[CLOCK_CONFIG_WIDTH-1:0] tohi,
    logic[`CLOCK_CONFIG_WIDTH-1:0] tceoeEnable;
    logic[`CLOCK_CONFIG_WIDTH-1:0] tceoeDisable;
    
    logic active;

    logic ready;    
    
    logic[3:0] sram_state;
    logic[3:0] outer_state;
    logic start_read_dbg_out;


     memory_read_top_module memory_read_top_module_inst(.*);
     
     
     initial begin
         
        clk1 <= 1;
        clk2 <= 1;
        start <= 0;
        reset <= 0;
        value <= 16'h5555;
        ceDriven <= 1'h1;
        start_read_dbg_out <= 1'h0;
        
        // Set timing
        tStart <= 16'h0;
        tas <= 16'h0;
        // t_ah 
        toed <= 16'd24; // we choose 60 ns 
        // toed + tprc = teleh 
        tprc = 16'd28; // 10 ns to in total 70 ns of teleh 
        tceoeEnable <= 15'h1;
        tceoeDisable <= 15'h1;
                
        reset <= 1'h0;
        #10
        start <= 1'h1;
        #10
        start <= 1'h0;
        #300
        $finish;
     end 
     
     // 400 MHz Clk
     initial begin 
        forever #1.25ns clk2 = ~clk2;
     end
     
     // 100 MHz Clk
     initial begin 
        forever #5 clk1 = ~clk1;
      end
     
endmodule
