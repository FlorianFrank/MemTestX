`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: University of Passau – Chair of Computer Engineering
// Engineer: Florian Frank
// 
// Design Name: reset_handler.v
// Module Name: reset_handler
// Project Name: memory_evaluator
// Target Device: Xilinx ZCU102
// Tool Version: Vivado 2022.2
// 
// Description: 
// This module manages reset signals for two clock domains: a system clock (clk) 
// and a high-speed 400 MHz clock (clk_400_mhz). It monitors two active-high 
// reset inputs (reset1_active_high and reset2_active_high) and generates 
// synchronized reset outputs for each clock domain.
// 
// Revision History:
// Rev. 0.01 - File Created
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
       reset_tmp <= (reset1_active_high || reset2_active_high );
    end
    
    always @ (posedge clk_400_mhz) begin
       reset_400_mhz_tmp <= (reset1_active_high || reset2_active_high);
    end
    
    assign reset_active_high = reset_tmp;
    assign reset_active_high_400_mhz = reset_400_mhz_tmp; 
    
endmodule
