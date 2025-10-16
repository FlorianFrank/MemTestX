`timescale 1ns / 1ps
`include "state_machine_definitions.vh"

//% \addtogroup memctr Memory Controller
//% @{


//% @brief This module is responsible to set the timing of the cs and 
//% It sets the OE, WE, CS as well as the address and datalines accordingly. 
//% @author Florian Frank
//% @copyright University of Passau - Chair of Computer Engineering
module read_sram_protocol #(
    //% Clock frequency which drives this module (is required to calculate the right timing)
    parameter integer CLK_FREQUENCY=400,
    parameter integer ADDRESS_BUS_SIZE=32,
    parameter integer DATA_BUS_SIZE=16,

    parameter [15:0] CLK_SYNCHRONIZATION=4,
    parameter integer CLOCK_CONFIG_WIDTH=16
)(
    //% Input clock which drives this module.
    input wire clk,

    input wire reset,
    
    input wire start,

    output reg[DATA_BUS_SIZE-1:0] value,

    input wire[DATA_BUS_SIZE-1:0] dlines,
    
    output wire[ADDRESS_BUS_SIZE-1:0] alines,
    
    input wire[ADDRESS_BUS_SIZE-1:0] address,


    //% chip enable (connect this to the chip enable of the memory chip)
    output reg ce,
    //% output enable (connect this to the chip enable of the memory chip)
    output reg oe,
    
    
    input wire ceDriven,
    // Timing Parameter
    input wire[CLOCK_CONFIG_WIDTH-1:0] tStart,
    //input wire[CLOCK_CONFIG_WIDTH-1:0] tah, // CURRENTLY not required
    input wire[CLOCK_CONFIG_WIDTH-1:0] tas,
    input wire[CLOCK_CONFIG_WIDTH-1:0] toed,
    input wire[CLOCK_CONFIG_WIDTH-1:0] tprc,
  //  input wire[CLOCK_CONFIG_WIDTH-1:0] tohi,
    input wire[CLOCK_CONFIG_WIDTH-1:0] tceoeEnable,
    input wire[CLOCK_CONFIG_WIDTH-1:0] tceoeDisable,
    
    
    
    
    //% this signal is raised for one clock cycle after the reading process is finished
    output reg signal_done,

    output reg active,

    output reg ready,

    input wire reduced_timing,

    output wire [3:0] state_out,

    output wire start_read_dbg_out
    
);

    reg[ADDRESS_BUS_SIZE-1:0] alines_tmp = {ADDRESS_BUS_SIZE{1'h0}};
    assign alines = alines_tmp;

    reg start_read_dbg_tmp = 0;
    assign start_read_dbg_out = start_read_dbg_tmp;


    integer counter = 0;
    integer counter2 = 0;
    integer counter3 = 0;
    
    reg readDone = 0;
    reg resetCEOEDone = 0;
    reg[3:0] state = `STATE_IDLE;
    assign state_out = state;

    initial begin
        active <= 1;
        signal_done <= 0;
        oe <= 1;
        ce <= 1;
        value <= 16'h0;
        counter <= 0;
    end
    
    reg started =  0;


    reg[3:0] finished_ctr = 0;
    

    //% @brief The always block executes the state machine to set the OE and CE  values accordingly.
    always@(posedge clk or posedge reset) begin
        if(reset == 1) begin 
            state <= `STATE_IDLE;
            started <= 0;
            counter <= 0;
            counter2 <= 0;
            counter3 <= 0;
    
            readDone <= 0;
            resetCEOEDone <= 0;

            ce <= 1;
            oe <= 1;
            active <= 0;
        end else begin 
            case (state)
                // Wait for incomming read request
                `STATE_IDLE:
                begin
                    signal_done <= 0;
                    oe <= 1'h1;
                    ce <= 1'h1;
                    start_read_dbg_tmp <= 1'h0;
                    
                    if (start == 1 || started == 1)
                        begin
                            started <= 1;
                            active <= 1;
                            signal_done <= 0;
                            if(tStart == 0 || counter < (tStart-1)) begin
                                started <= 0;
                                counter <= 0;
                                state <= `STATE_SET_CE_OE;
                            end else begin 
                               counter <= 0;
                          end  
                        end
                    else begin active <= 0;
                        counter <= 0;
                    end
                    ready <= 0;
                end
    
                `STATE_SET_CE_OE:
                begin
                    alines_tmp <= address;
                    if(tas == 0 || counter >= (tas -1)) begin 
                        if(ceDriven) begin 
                            ce <= 1'b0;
                            if (tceoeEnable != 0 && counter2 < tceoeEnable) begin
                                counter2 <= counter2 + 1; 
                            end else begin
                                oe <= 1'b0;
                                counter <= 0;
                                counter2 <= 0;
                                state <= `STATE_READ_DATA;   
                            end
                        end else begin
                            oe <= 1'b0;
                            if (tceoeEnable != 0 && counter2 < tceoeEnable) begin 
                                counter2 <= counter2 + 1;
                            end else begin
                                ce <= 1'b0;
                                counter <= 0;
                                counter2 <= 0;
                                state <= `STATE_READ_DATA;
                            end
                        end      
                    end else begin 
                        counter <= counter + 1;
                    end
                end
    
                // Use counter to wait for the read latency
                `STATE_READ_DATA:
                begin
                    if(toed == 0 || counter >= toed -1) begin 
                        value <= dlines; // Assign DLINES
                        start_read_dbg_tmp <= 1'h1;
                        counter <= 0;
                        readDone <= 1; 
                    end else begin 
                        counter <= counter + 1;
                        start_read_dbg_tmp <= 1'h0;
                    end 
                    
                    if(tprc == 0 || counter2 >= (tprc -1)) begin 
                       if(ceDriven) begin 
                            oe <= 1'b1;
                            if(tceoeDisable == 0 || counter3 > tceoeDisable) begin 
                                ce <= 1'b1;
                                resetCEOEDone <= 1'b1;
                            end else begin
                                counter3 <= counter3 + 1;
                            end
                        end else begin
                            ce <= 1'b1;
                            if(tceoeDisable == 0 || counter3 >= tceoeDisable) begin
                                oe <= 1'b1; 
                                resetCEOEDone <= 1'b1;
                            end else begin
                                counter3 <= counter3 + 1;
                            end
                        end
                    end else begin 
                        counter2 <= counter2 + 1;
                    end
                    
                    
                 if(readDone && resetCEOEDone) begin
                    readDone <= 1'b0;
                    resetCEOEDone <= 1'b0;
                    counter <= 0;
                    counter2 <= 0;
                    counter3 <= 0;
                    start_read_dbg_tmp <= 1'h0;
                    state <= `STATE_FINISHED;
                 end
                    
                end
                
    
                `STATE_FINISHED: begin
                    active <= 0;
                    signal_done <= 1;
                    if(counter >= (CLK_SYNCHRONIZATION-1)) begin
                        counter <= 0;
                        state <= `STATE_IDLE;
                    end else begin
                        counter <= counter + 1;
                    end
                end
            endcase
        end
    end

endmodule
//% @}