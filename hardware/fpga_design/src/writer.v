`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/22/2024 04:18:30 PM
// Design Name: 
// Module Name: writer
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


module writer #(
    parameter integer VALUE_SIZE = 8,
    parameter integer ADDRESS_SIZE = 15
)(
    input wire clk,
    input wire start,
    input wire active,
    output reg[VALUE_SIZE-1:0] value,
    output reg[ADDRESS_SIZE-1:0] address,
    output reg start_write,
    input wire ready_in,
    output reg done
    );
    
    assign rw_select = 1;
    
    initial begin
        value <= 8'h00;
        address <= 15'h1;
        start_write <= 0;
        done <= 0;
    end
    
    reg [3:0] address_short = 0;
    reg started = 0;
    reg stopped = 0;
    
    always @ (posedge clk) begin
    
         if (start && !active) begin
            start_write <= 1;
        end else begin
            start_write <= 0;
        end
        
        if (ready_in && !done) begin
            start_write <= 1;
        end
    
    end
    
    always @(posedge ready_in) begin
    
        //value <= value + 1;
        address <= address + 1;
    
    end
endmodule
