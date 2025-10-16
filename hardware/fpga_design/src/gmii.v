`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 02/06/2024 08:43:03 AM
// Design Name: 
// Module Name: gmii
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


module gmii(

    input wire clk_125,
    input wire start,
    output wire active,

     output reg[7:0] txd, 
     output reg tx_en,
     output reg tx_er, 
     
     input wire rxd,
     input wire rx_dv,
     input wire rx_er,
     
     input wire rxd_out,
     input wire rx_dv_out,
     input wire rx_er_out,
     
     
     input wire gmii_isolate,
     output wire[3:0] state_out,
     output wire clk_out
    );
    
    // Constant definition
    // TODO replace with actual payload
    reg[7:0]  PREAMBLE    = 8'b10101010;
    reg[7:0]  SFD         = 8'b10101011;
    reg[47:0] DEST_MAC    = 48'h001122334455;
    reg[47:0] SRC_MAC     = 48'haabbccddeeff;
    reg[15:0] TYPE_LENGTH = 16'h0800;
    reg[87:0] DATA        = 88'h48656C6C6F20576F726C64;
    reg[31:0] CRC         = 32'h12345678;
    
    
    // States definition
    parameter START_STATE       = 5'h0;
    parameter PREAMBLE_STATE    = 5'h1;
    parameter SFD_STATE         = 5'h2;
    parameter DEST_MAC_STATE    = 5'h3;
    parameter SRC_MAC_STATE     = 5'h4;
    parameter TYPE_LENGTH_STATE = 5'h5;
    parameter DATA_STATE        = 5'h6;
    parameter CRC_STATE         = 5'h7;
    parameter FINISH_STATE      = 5'h8;
    
    reg[4:0] waitCtr = 5'h0;
    reg[4:0] state = START_STATE;
        
    initial begin
        active <= 0;
        tx_en <= 0;
        tx_er <= 0;
        txd <= 8'h0;
    end     
    
        
    always @ (posedge clk_125) begin
    
        case(state)
            START_STATE: begin
                if (start == 1) begin
                    active <= 1;
                    state <= PREAMBLE_STATE;
                end
            end
        
            PREAMBLE_STATE: begin 
                tx_er <= 1'b0;
                tx_en <= 1'b1;
                txd <= PREAMBLE;
                if (waitCtr >= 8) begin 
                    state <= SFD_STATE;
                    waitCtr = 0;
                    end
                waitCtr = waitCtr + 1;
                end 
                
            SFD_STATE: begin
                txd <= SFD;
                state <= DEST_MAC_STATE;
            end
            
            DEST_MAC_STATE: begin
                if(waitCtr >= 6) begin
                    state <= SRC_MAC_STATE;
                    waitCtr = 0;
                end 
                txd <= DEST_MAC[waitCtr*8+:8];
                waitCtr = waitCtr + 1;
            end
            
           SRC_MAC_STATE: begin
                if(waitCtr >= 6) begin
                    state <= TYPE_LENGTH_STATE;
                    waitCtr = 0;
                end 
                txd <= SRC_MAC[waitCtr*8+:8];
                waitCtr = waitCtr + 1;
            end
            
                        
           TYPE_LENGTH_STATE: begin
                if(waitCtr >= 2) begin
                    state <= DATA_STATE;
                    waitCtr = 0;
                end 
                txd <= TYPE_LENGTH[waitCtr*8+:8];
                waitCtr = waitCtr + 1;
            end
            
            DATA_STATE: begin
                if(waitCtr >= 11) begin
                    state <= CRC_STATE;
                    waitCtr = 0;
                end 
                txd <= DATA[waitCtr*8+:8];
                waitCtr = waitCtr + 1;
            end
            
            CRC_STATE: begin
                if(waitCtr >= 4) begin
                    state <= FINISH_STATE;
                    tx_en <= 1'b0;
                    waitCtr = 0;      
                end 
                txd <= CRC[waitCtr*8+:8];
                waitCtr = waitCtr + 1;
            end

            FINISH_STATE: begin
                active <= 0;
                state <= START_STATE;
            end
            
        endcase  
    
    end
    
    assign state_out = state;
    assign clk_out = clk_125;
    
         
     assign rxd_out = rxd;
     assign rx_dv_out = rx_dv; 
     assign rx_er_out = rx_er;
     
    
endmodule
