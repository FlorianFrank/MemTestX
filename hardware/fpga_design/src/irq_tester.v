`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/06/2024 09:01:28 AM
// Design Name: 
// Module Name: irq_tester
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


module irq_tester(
        input wire clk, 
        output wire irq
    );
    
    reg irq_tmp = 1'b0;
    integer ctr = 0;
    
    always @ (posedge clk) begin
        if (ctr == 1000000000) begin
           irq_tmp <= 1'b1;
           ctr <= 0;   
        end
        else begin
            irq_tmp <= 0;
            ctr <= ctr + 1;
        end
    end
    
    assign irq = irq_tmp;
    
endmodule
