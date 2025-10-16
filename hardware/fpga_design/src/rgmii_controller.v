`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 02/18/2024 12:43:04 PM
// Design Name: 
// Module Name: rgmii_controller
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


module rgmii_controller 
    #(parameter OUT_DATA_BUS_WIDTH=4,
      parameter INPUT_DATA_WIDTH=8)
    (
    input wire clk_125,
    input wire start,
    output reg active,
    
    input wire[INPUT_DATA_WIDTH-1:0] input_data,
    
    
    output wire gtx_clk,
    output reg tx_en,
    
    output reg[OUT_DATA_BUS_WIDTH-1:0] tx_data,
    
    output wire rx_clk,
    output wire rx_ctrl,
    input wire[OUT_DATA_BUS_WIDTH-1:0] rx_data,
    
    output reg tx_er,
    output reg tx_clk
    );
        
      // Constant definition
    // TODO replace with actual payload
    reg[55:0]  PREAMBLE    = 56'b10101010101010101010101010101010101010101010101010101010;
    reg[7:0]  SFD         = 8'b10101011;
    reg[47:0] DEST_MAC    = 48'h001122334455;
    reg[47:0] SRC_MAC     = 48'haabbccddeeff;
    reg[15:0] TYPE_LENGTH = 16'h0800;
    reg[87:0] DATA        = 88'h48656C6C6F20576F726C64;
    reg[31:0] CRC         = 32'h12345678;
    
    
    // States definition
    localparam START_STATE       = 5'h0;
    localparam PREAMBLE_STATE    = 5'h1;
    localparam SFD_STATE         = 5'h2;
    localparam DEST_MAC_STATE    = 5'h3;
    localparam SRC_MAC_STATE     = 5'h4;
    localparam TYPE_LENGTH_STATE = 5'h5;
    localparam DATA_STATE        = 5'h6;
    localparam CRC_STATE         = 5'h7;
    localparam FINISH_STATE      = 5'h8;
    
    reg[4:0] waitCtr = 5'h0;
    reg[4:0] state = START_STATE;
        
    initial begin
        active <= 0;
        tx_en <= 0;
        tx_er <= 0;
        tx_data <= 8'h0;
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
                tx_data <= PREAMBLE[waitCtr*OUT_DATA_BUS_WIDTH+:OUT_DATA_BUS_WIDTH];
                if (waitCtr >= 2) begin
                    state <= SFD_STATE;
                    waitCtr = 0;
                    end
                waitCtr = waitCtr + 1;
                end 
                
            SFD_STATE: begin
                if (waitCtr >= 8/OUT_DATA_BUS_WIDTH) begin
                    state <= DEST_MAC_STATE;
                    waitCtr = 0;
                    end
                tx_data <= SFD[waitCtr*OUT_DATA_BUS_WIDTH+:OUT_DATA_BUS_WIDTH];
                waitCtr = waitCtr + 1;
                end
            
            DEST_MAC_STATE: begin
                if(waitCtr >= 48/OUT_DATA_BUS_WIDTH) begin
                    state <= SRC_MAC_STATE;
                    waitCtr = 0;
                end 
                tx_data <= DEST_MAC[waitCtr*OUT_DATA_BUS_WIDTH+:OUT_DATA_BUS_WIDTH];
                waitCtr = waitCtr + 1;
            end
            
           SRC_MAC_STATE: begin
                if(waitCtr >= 48/OUT_DATA_BUS_WIDTH) begin
                    state <= TYPE_LENGTH_STATE;
                    waitCtr = 0;
                end 
                tx_data <= SRC_MAC[waitCtr*OUT_DATA_BUS_WIDTH+:OUT_DATA_BUS_WIDTH];
                waitCtr = waitCtr + 1;
            end
            
                        
           TYPE_LENGTH_STATE: begin
                if(waitCtr >= 16/OUT_DATA_BUS_WIDTH) begin
                    state <= DATA_STATE;
                    waitCtr = 0;
                end 
                tx_data <= TYPE_LENGTH[waitCtr*OUT_DATA_BUS_WIDTH+:OUT_DATA_BUS_WIDTH];
                waitCtr = waitCtr + 1;
            end
            
            DATA_STATE: begin
                if(waitCtr >= 88/OUT_DATA_BUS_WIDTH) begin
                    state <= CRC_STATE;
                    waitCtr = 0;
                end 
                tx_data <= DATA[waitCtr*OUT_DATA_BUS_WIDTH+:OUT_DATA_BUS_WIDTH];
                waitCtr = waitCtr + 1;
            end
            
            CRC_STATE: begin
                if(waitCtr >= 32/OUT_DATA_BUS_WIDTH) begin
                    state <= FINISH_STATE;
                    tx_en <= 1'b0;
                    waitCtr = 0;      
                end 
                tx_data <= CRC[waitCtr*OUT_DATA_BUS_WIDTH+:OUT_DATA_BUS_WIDTH];
                waitCtr = waitCtr + 1;
            end

            FINISH_STATE: begin 
                tx_en <= 1'b1;
                active <= 0;
                state <= START_STATE;
            end
        endcase  
    
    end
    
    
    assign gtx_clk = clk_125;
    
    
endmodule
