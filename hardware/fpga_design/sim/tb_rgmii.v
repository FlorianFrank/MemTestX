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


module tb_rgmii(

    );
    
    
   reg clk;
   reg rgmii_start = 0;
   wire rgmii_active;
   reg[7:0] dummy_data = 8'h55;
   
   wire gtx_clk;
   wire tx_en;
   wire[3:0] tx_data;
   
   wire rx_clk;
   wire rx_ctrl;
   wire[3:0] rx_data;
   
   initial begin
    clk <= 0;
    rgmii_start <= 1;
    #10
    rgmii_start <= 0;
    #100
    $stop;
   end

    initial begin
        forever #1 clk <= ~ clk;
    end
    
    rgmii_controller 
    #(.OUT_DATA_BUS_WIDTH(4), .INPUT_DATA_WIDTH(8)) rgmii_inst (
        .clk_125(clk),
        .start(rgmii_start),
        .active(rgmii_active),

         .input_data(dummy_data),
         .gtx_clk(gtx_clk),
         .tx_en(tx_en),
         .tx_data(tx_data),

         .rx_clk(rx_clk),
         .rx_ctrl(rx_ctrl),
         .rx_data(rx_data)
        );
    
endmodule
