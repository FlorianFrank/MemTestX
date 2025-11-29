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
    parameter integer ALINES_SIZE = 24,
    parameter integer DLINES_SIZE = 16,
    parameter SET_ZZ_PIN = 1,
    parameter ENABLE_LB_UB = 0
 )(
 
    input wire clk,
    input wire set_back,
 
    input wire start_write,
    input wire start_read, 
    
    input wire read_done,
    input wire write_done,
    
    input wire[ALINES_SIZE-1:0] alines_write,
    input wire[ALINES_SIZE-1:0] alines_read,
    input wire[DLINES_SIZE-1:0] dlines_in,
    output wire[DLINES_SIZE-1:0] dlines_out,
    output wire[ALINES_SIZE-1:0] alines,
    output wire oe,
    output wire ce,
    output wire we,
    output wire zz,
    output wire lb,
    output wire ub,
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

    reg ub_lb_indicator = 1'h0; 
    reg[DLINES_SIZE-1:0] dlines_out_reg;


    always @(posedge clk or posedge set_back) begin
        if (set_back) begin 
            ub_lb_indicator <= 1'b0;
            dlines_out_reg <= {DLINES_SIZE{1'b0}};
        end else if (start_write || start_read) begin 
            ub_lb_indicator <= 1'h1;
        end else begin
            // Set input data when reading is enabled 
            if (!rw_select_in)
                dlines_out_reg <= dlines_in;
            if (read_done || write_done) begin 
                ub_lb_indicator <= 1'h0;
            end else begin 
                ub_lb_indicator <= ub_lb_indicator;
            end 
        end
    end


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
    assign dlines = (!rw_select_in) ? dlines_out_reg : {DLINES_SIZE{1'hz}};
    assign dlines_out = (rw_select_in) ? dlines : {DLINES_SIZE{1'h1}};
    
    // Set these pins to default values
    assign zz = SET_ZZ_PIN;
    assign lb = (ENABLE_LB_UB) ? ((ub_lb_indicator) ? 1'h0 : 1'h1) : 0;
    assign ub = (ENABLE_LB_UB) ? ((ub_lb_indicator && DLINES_SIZE == 16) ? 1'h0 : 1'h1) : 0;
    
endmodule
