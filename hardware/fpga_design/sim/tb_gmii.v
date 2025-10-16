`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 02/06/2024 09:42:32 AM
// Design Name: 
// Module Name: tb_gmii
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


module tb_gmii(

    );
    
    
   reg clk;
   reg locked;
   wire[7:0] txd;
   wire tx_en;
   wire tx_er;
   wire tx_en;  
   
   reg rxd;
   reg rx_dv;
   reg rx_er;
   reg gmii_isolate;
   wire[3:0] state;
   wire clk_out;
   
   initial begin
    clk <= 0;
    rxd <= 0;
    rx_dv <= 0;
    rx_er <= 0;
    gmii_isolate <= 0;
    locked <= 0;
    #5
    locked <= 1;
    #100
    $stop;
   end

    initial begin
        forever #1 clk <= ~ clk;
    end
    
gmii gmiiModule(
    .clk_125(clk),
    .locked(locked),
    .txd(txd), 
    .tx_en(tx_en),
    .tx_er(tx_er), 
    .rxd(rxd),
    .rx_dv(rx_dv),
    .rx_er(rx_er),
    .gmii_isolate(gmii_isolate),
    .state_out(state),
    .clk_out(clk_out)
    );
    
endmodule
