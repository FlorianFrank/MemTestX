`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: University of Passau
// Engineer: Florian Frank
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


module ip_core_controller #(parameter A = 0)(
        input wire clk_125Mhz,
        input wire locked,

        output wire gtx_clk,
        
        output wire tx_en,
        output wire tx_d0,
        output wire tx_d1,
        output wire tx_d2,
        output wire tx_d3,
        
        
        input wire rx_clk,
        input wire rx_ctrl,
        
        input wire rx_d0,
        input wire rx_d1,
        input wire rx_d2,
        input wire rx_d3,
            
        
        // MDIO interface signals
        output wire mdio_mdc,
        inout wire mdio_in_out,

        output wire[3:0] state_out
  );

    // State machine definitions
    localparam INIT_STATE          = 2'h0;
    localparam WRITE_CONFIGURATION = 2'h1;
    localparam START_GMII_MODULE   = 2'h2;
    localparam NEXT_STATE          = 2'h3;

    // Counter for the state machine
    reg[2:0] state;
    reg start_gmii = 1'b0;


    always @ (posedge clk_125Mhz) begin
        case(state)
            INIT_STATE: begin
                state <= WRITE_CONFIGURATION;
            end

            WRITE_CONFIGURATION: begin
                // This signal is valid only when the MDIO interface is present.
                // The rising edge of this signal is the enable signal to overwrite
                // the Register 0 contents that were written from the MDIO interface.
                if(locked) begin
                    start_gmii <= 1;
                    state <= START_GMII_MODULE;
                end

            end

            START_GMII_MODULE: begin
                start_gmii <= 0;
                state <= NEXT_STATE;
            end

            NEXT_STATE: begin

               // TODO should we stay here forever?
            end

        endcase
    end



    // TODO fill parameters
    reg mdio_start;
    wire mdio_active;
    reg mdio_reset;
    reg mdio_read_write;
    reg[4:0] mdio_phy_address;
    reg [4:0] mdio_register_address;
    reg [15:0] mdio_data;
    reg[3:0] mdio_state_out;
    wire [3:0] state_mdio;

    
    mdio #(.CLOCK_DIVIDER(1)) mdio_inst (
        .clk_125MHz(clk_125Mhz),
        .start(mdio_start),
        .active(mdio_active),
        .reset(mdio_reset),

        .read_write(mdio_read_write),
        .phy_address(mdio_phy_address),
        .register_address(mdio_register_address),
        .data(mdio_data),

        .mdio(mdio_in_out),
        .mdc(mdio_mdc),
        .state_out(state_mdio));


    reg rgmii_start = 1;
    wire rgmii_active;
    reg[7:0] dummy_data = 8'h55;
    wire[3:0] tx_data;
    wire[3:0] rx_data;

    rgmii_controller #(.OUT_DATA_BUS_WIDTH(4), .INPUT_DATA_WIDTH(8)) rgmii_inst (
        .clk_125(clk_125Mhz),
        .start(rgmii_start),
        .active(rgmii_active),

         .input_data(dummy_data),
         .gtx_clk(gtx_clk),
         .tx_en(tx_en),
         .tx_data(tx_data),

         .rx_clk(rx_clk),
         .rx_ctrl(rx_ctrl),
         .rx_data(rx_data)
        );

     assign tx_d0 = tx_data[0];
     assign tx_d1 = tx_data[1];
     assign tx_d2 = tx_data[2];
     assign tx_d3 = tx_data[3];

     assign rx_data[0] = rx_d0;
     assign rx_data[1] = rx_d1;
     assign rx_data[2] = rx_d2;
     assign rx_data[3] = rx_d3;

     endmodule
   