`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: University of Passau – Chair of Computer Engineering
// Engineer: Florian Frank
// 
// Create Date: 03/12/2024 02:14:09 PM
// Design Name: multiplexer.v
// Module Name: multiplexer
// Project Name: memory_evaluator
// Target Device: Xilinx ZCU102
// Tool Version: Vivado 2022.2
// 
// Description: 
// Implements the control logic for bidirectional data lines and multiplexes 
// access to the shared address and control lines. Additionally, it manages 
// the dual-supply bus transceivers based on the current operation mode 
// (read or write), ensuring correct signal direction and voltage-level 
// interfacing between the FPGA and external memory.
// 
// Revision History:
// Rev. 0.01 - File Created
//
//////////////////////////////////////////////////////////////////////////////////


module multiplexer#(
    parameter integer ALINES_SIZE = 15,
    parameter integer DLINES_SIZE = 8
)(
    input wire[ALINES_SIZE-1:0] alines_write,
    input wire[ALINES_SIZE-1:0] alines_read,
    input wire[DLINES_SIZE-1:0] dlines_in,
    output wire[DLINES_SIZE-1:0] dlines_out,
    output wire[ALINES_SIZE-1:0] alines,
    output wire oe,
    output wire ce,
    output wire we,
    input wire oe_write,
    input wire ce_write,
    input wire we_write,
    input wire oe_read,
    input wire ce_read,
    input wire we_read,
    input wire rw_select_in,
    inout wire[DLINES_SIZE-1:0] dlines,
    
    // Level shifter
    output wire dir_const,
    output wire dir_var,
    output wire en_const,
    output wire en_var,
    output wire ref_vcc,
    output wire ref_vcc2
);

    assign dir_const = 1'b1;
    assign dir_var = rw_select_in ? 1'b0 : 1'b1; 
    
    assign en_var = 1'b0;
    assign en_const = 1'b0;

    assign ref_vcc = 1'b1;
    assign ref_vcc2 = 1'b1;

    assign alines = !rw_select_in ? alines_write : alines_read;
    assign oe = !rw_select_in ? oe_write : oe_read;
    assign ce = !rw_select_in ? ce_write : ce_read;
    assign we = !rw_select_in ? we_write : we_read;

    // Handle the bidirectional data port correctly by assigning dlines based on the current read/write mode.
    assign dlines = (!rw_select_in) ? dlines_in : {DLINES_SIZE{1'hz}};
    assign dlines_out = (rw_select_in) ? dlines : {DLINES_SIZE{1'h1}};
endmodule
