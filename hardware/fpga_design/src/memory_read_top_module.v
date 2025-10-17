//////////////////////////////////////////////////////////////////////////////////
// Company: University of Passau – Chair of Computer Engineering
// Engineer: Florian Frank
// 
// Create Date: 03/12/2024 02:14:09 PM
// Design Name: memory_read_top_module.v
// Module Name: memory_read_top_module
// Project Name: memory_evaluator
// Target Device: Xilinx ZCU102
// Tool Version: Vivado 2022.2
// 
// Description: 
// Top-level module for reading data from memory using a microcontroller-compatible
// SRAM protocol. The module manages read operations, handles timing parameters,
// and provides synchronization between a management module and the memory controller.
// It uses a state machine to trigger read operations, wait for completion, and
// notify the management controller when a read is finished. The module supports
// configurable address and data bus widths, clock frequencies, and timing parameters.
// 
// Revision History:
// Rev. 0.01 - File Created
//
//////////////////////////////////////////////////////////////////////////////////

`timescale 1ns / 1ps

`include "state_machine_definitions.vh"

module memory_read_top_module #(
    //% Frequency of the clock driving the management module. (used for synchronization purposes)
    parameter integer FREQ_CLK1=100,
    //% Frequency of the clock driving the memory controller. (used for synchronization purposes)
    parameter integer FREQ_CLK2=400,
    //% Data setup time defines how much time is waited until a read operation is executed.
    parameter integer ADDRESS_BUS_SIZE=15,
    parameter integer DATA_BUS_SIZE_OUT = 16,
    parameter integer DATA_BUS_SIZE=64,    
    parameter integer CLOCK_CONFIG_WIDTH = 16

)(

    //% Input clock which drives the memory controller.
    input wire clk1,
    
    input wire clk2,

    input wire start,

    input wire reset,

    //% The value which should be read from the // TODO.
    output  reg[DATA_BUS_SIZE-1:0] value,
    

    //% Data lines from which the data should be read
    input wire[DATA_BUS_SIZE_OUT-1:0] dlines,

    input wire[ADDRESS_BUS_SIZE-1:0] address,

    //% Address lines specifying the address currently used. (only the Rohm FRAM is supported with an address width of 15 bit)
    output wire[ADDRESS_BUS_SIZE-1:0] alines,

    //% Chip enable signal.
    output wire ce,

    //% Output enable signal.
    output wire oe,

    //% Write enable signal
    output wire we,
   
    input wire ceDriven,
    // Timing Parameter
    input wire[CLOCK_CONFIG_WIDTH-1:0] tStart,
    //input wire[CLOCK_CONFIG_WIDTH-1:0] tah,
    input wire[CLOCK_CONFIG_WIDTH-1:0] tas,
    input wire[CLOCK_CONFIG_WIDTH-1:0] toed,
    input wire[CLOCK_CONFIG_WIDTH-1:0] tprc,
    //input wire[CLOCK_CONFIG_WIDTH-1:0] tohi,
    input wire[CLOCK_CONFIG_WIDTH-1:0] tceoeEnable,
    input wire[CLOCK_CONFIG_WIDTH-1:0] tceoeDisable,
    
    output reg read_active,

    output reg ready,    
    
    output wire[3:0] sram_state,
    output wire[3:0] outer_state,
    output wire start_read_dbg_out
);

    wire[3:0] sram_state_in;
    assign sram_state = sram_state_in;
    
    reg signal_start = 0;

    reg[ADDRESS_BUS_SIZE-1:0] address_tmp = {ADDRESS_BUS_SIZE{1'h0}};

    assign we = 1;

    //% Signal form the underlysing read logic to indicate that the read operation is finished.
    wire signal_done;


    //% State counter stores the current state of the state machine used within the always block.
    reg[2:0] state = `IDLE;
    
    
    reg[7:0] read_ctr = 8'h0;
    
    
    wire[DATA_BUS_SIZE_OUT-1:0] value_tmp;
    
    integer counter = 0;
    
    reg start_triggered = 0;
    
    integer delayCtr = 0;
    
    
    assign outer_state = state;
    
    
    //% @brief Initial block initializes all registers at startup.
    initial begin
        state <= `IDLE;
        address_tmp <= 0;

        ready <= 0;
        read_active <= 0;
        counter <= 0;
    end



    //% Always block executes the state machine.
    always @(posedge clk1)// or posedge reset)
    begin
        if(reset == 1) begin 
            state <= `IDLE;
            address_tmp <= 0;    
            read_ctr <= 0;
            signal_start <= 0;
            start_triggered <= 0;
            delayCtr <= 0;
            counter <= 0;
        end else begin 
            case(state)
    
                // Wait for notification from ethernet controller to start reading
                `IDLE:
                begin
                    if(start == 1) begin
                        address_tmp <= address;
                        start_triggered <= 1;
                    end else begin 
                        delayCtr <= 0;
                    end
    
                    if(start_triggered == 1) begin
                        read_active <= 1;
                        signal_start <= 0;
                        state <= `TRIGGER_READ_OPERATION;
                    end else read_active <= 0;
                    
                    ready <= 0;
                    read_ctr <= 0;
                end
                
                `NEXT_READ: begin
                    address_tmp <= address_tmp + 1;
                    read_ctr <= read_ctr + 1;
                    state <= `TRIGGER_READ_OPERATION;
                end
    
                // Send trigger to read controller to start read operation
                `TRIGGER_READ_OPERATION:
                begin
                    start_triggered <= 0;
                    signal_start <= 1;
                    state <= `WAIT_FOR_READ_FINISHED;
                end
    
                // Wait for finished signal
                `WAIT_FOR_READ_FINISHED:
                begin
                    signal_start <= 0;
                    // Disable ethernet module
                    if (signal_done == 1) begin
                        state <= `NOTIFY_MANAGEMENT_CONTROLLER;
                        value <= value_tmp;
                    end
                end
    
                // In this step a synchronization command is sent to the ethernet controller
                `NOTIFY_MANAGEMENT_CONTROLLER:
                begin
                    signal_start <= 0;
                    if(signal_done == 0) begin
                        state <= `IDLE;
                        ready <= 1;
                        read_active <= 0;
                    end
                end
            endcase
        end
    end


    // Reading module of the micro controller
    read_sram_protocol #(
    .CLK_FREQUENCY(FREQ_CLK2),
    .ADDRESS_BUS_SIZE(ADDRESS_BUS_SIZE),
    .DATA_BUS_SIZE(DATA_BUS_SIZE_OUT),
    .CLOCK_CONFIG_WIDTH(CLOCK_CONFIG_WIDTH), 
    .CLK_SYNCHRONIZATION(4)
    )
    memorycontroller_read (
        .clk(clk2),
        .start(signal_start),
        .ce(ce),
        .oe(oe),
        .address(address_tmp),
        .alines(alines),
        .reset(reset),
        
        .ceDriven(ceDriven),
        .tStart(tStart),
        //.tah(tah),
        .tas(tas),
        .toed(toed),
        .tprc(tprc),
        //.tohi(tohi),
        .tceoeEnable(tceoeEnable),
        .tceoeDisable(tceoeDisable),
        
        .signal_done(signal_done),
        .value(value_tmp),
        .dlines(dlines),
        .state_out(sram_state_in),
        .start_read_dbg_out(start_read_dbg_out)
        );
   


endmodule
//% @}