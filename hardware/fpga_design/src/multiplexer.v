`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/12/2024 02:14:09 PM
// Design Name: 
// Module Name: multiplexer
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


module multiplexer#(
    parameter integer ALINES_SIZE = 15,
    parameter integer DLINES_SIZE = 8
)(
    input wire clk,
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

    // Handle the bidirectional port correctly: assign dlines based on rw_select_in
    assign dlines = (!rw_select_in) ? dlines_in : {DLINES_SIZE{1'hz}};
    assign dlines_out = (rw_select_in) ? dlines : {DLINES_SIZE{1'h1}};
endmodule
