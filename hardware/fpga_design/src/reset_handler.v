`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 02/05/2025 09:58:25 AM
// Design Name: 
// Module Name: reset_handler
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


module reset_handler(
        input clk,
        input clk_400_mhz,
        input wire reset1_active_high,
        input wire reset2_active_high,
        output wire reset_active_high,
        output wire reset_active_high_400_mhz
    );
    
    reg reset_tmp = 0;
    reg reset_400_mhz_tmp = 0;
    
    always @ (posedge clk) begin
       reset_tmp <= (reset1_active_high == 1 || reset2_active_high == 1);
    end
    
    always @ (posedge clk_400_mhz) begin
       reset_400_mhz_tmp <= (reset1_active_high == 1 || reset2_active_high == 1);
    end
    
    assign reset_active_high = reset_tmp;
    assign reset_active_high_400_mhz = reset_400_mhz_tmp; 
    
endmodule
