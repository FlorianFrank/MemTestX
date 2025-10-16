`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/12/2024 10:45:19 AM
// Design Name: 
// Module Name: read_starter
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


module read_starter(
    input wire clk,
    input wire[7:0] data_in,
    output reg[14:0] address_read,
    output reg start_read,
    output reg[15:0] value_axi,
    output reg[31:0] address_axi,
    input wire read_done,
    input wire ps_pl_trigger
    );
    
    parameter [3:0] READ_DATA = 4'h00;
    parameter [3:0] WAIT_FOR_NEXT_READ = 4'h01;
    parameter [3:0] SET_LINES = 4'h02;
    parameter [3:0] WAIT_FINISH = 4'h03;
    parameter [3:0] SLEEP = 4'h04;
    parameter [3:0] DONE = 4'h05;
    
    reg [3:0] state = READ_DATA;
    
    initial begin
        address_read <= 0;
        value_axi <= 0;
        
    end
    
    always @(posedge clk) begin
        case (state)
        
            READ_DATA: begin
                start_read <= 1;
                state <= SET_LINES;
            end
            
            SET_LINES: begin
                if (read_done) begin
                    value_axi <= 1;
                end
            end
        
            WAIT_FOR_NEXT_READ: begin
                address_read <= address_read + 1;
                start_read <= 0;
                if (sleep_state) begin
                    state <= READ_DATA;
                end
            end
        
        endcase
        
    end
    
endmodule
