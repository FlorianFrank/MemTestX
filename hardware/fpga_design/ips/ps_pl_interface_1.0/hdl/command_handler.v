`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 02/23/2024 08:43:49 AM
// Design Name: 
// Module Name: command_handler
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

`define TIMING_BUS_WIDTH 16

module command_handler #(parameter C_AXI_Light_Slave_DATA_WIDTH = 32, parameter BUFF_LEN = 20) (
    input wire clk,
    input wire[(C_AXI_Light_Slave_DATA_WIDTH*BUFF_LEN) - 1: 0] received_data,
    input wire [BUFF_LEN-1:0] write_map,
    output reg [3:0] read_map,
    
    // Response
    output wire trigger_cmd_handler,
    output wire [7:0] output_state,

    output reg [7:0]   cmd,
    output reg [15:0]  init_value,
    output reg [15:0]  puf_value,
    output reg [31:0]  start_addr,
    output reg [31:0]  stop_addr,
    output wire cmd_ready,

    output reg[7:0] puf_type,
    output reg      ce_driven,
    output wire reset_out,

    // Default Timing
    output reg[`TIMING_BUS_WIDTH-1:0]   tWaitAfterInit,
    output reg[`TIMING_BUS_WIDTH-1:0]   tNextRead,
    output reg[`TIMING_BUS_WIDTH-1:0]   tStartDefault,
    output reg[`TIMING_BUS_WIDTH-1:0]   tnextWriteDefault,
    output reg[`TIMING_BUS_WIDTH-1:0]   tACDefault,
    output reg[`TIMING_BUS_WIDTH-1:0]   tASDefault,
    output reg[`TIMING_BUS_WIDTH-1:0]   tAHDefault,
    output reg[`TIMING_BUS_WIDTH-1:0]   tPWDDefault,
    output reg[`TIMING_BUS_WIDTH-1:0]   tDSDefault,
    output reg[`TIMING_BUS_WIDTH-1:0]   tDHDefault,

    // Read
    output reg ceDrivenRead,
    output reg[`TIMING_BUS_WIDTH-1:0] tStartReadDefault,
    output reg[`TIMING_BUS_WIDTH-1:0] tasReadDefault,
    output reg[`TIMING_BUS_WIDTH-1:0] tahReadDefault,
    output reg[`TIMING_BUS_WIDTH-1:0] toedDefault,
    output reg[`TIMING_BUS_WIDTH-1:0] tprcDefault,
    output reg[`TIMING_BUS_WIDTH-1:0] tceoeEnableDefault,
    output reg[`TIMING_BUS_WIDTH-1:0] tceoeDisableDefault,

    // Write Latency
    output reg[`TIMING_BUS_WIDTH-1:0]   tNextWriteAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0]   tStartAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0]   tACAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0]   tASAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0]   tAHAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0]   tDSAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0]   tDHAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0]   tPWDAdjusted,

    // Read Latency
    output reg[`TIMING_BUS_WIDTH-1:0] tStartReadAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0] tasReadAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0] tahReadAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0] toedAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0] tprcAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0] tceoeEnableAdjusted,
    output reg[`TIMING_BUS_WIDTH-1:0] tceoeDisableAdjusted,

    // Row-Hammering
    output reg[15:0] hammeringIterations,
    output reg[15:0] hammeringDistance,
    output reg[15:0] tWaitBetweenHammering

);

reg reset_tmp = 0;


    initial begin

        cmd <= 8'h0;

        // General PUF definitions
        puf_type <= 8'h0;
        init_value <= 16'h0;
        puf_value <= 16'h0;
        start_addr <= 32'h00;
        stop_addr <= 32'h00;
        ce_driven <= 0;

        // Timing
        // Write
        tWaitAfterInit <= 15'h0;
        tNextRead <= 15'h0;
        tStartDefault <= 15'h0;
        tnextWriteDefault <= 15'h0;
        tACDefault <= 15'h0;
        tASDefault <= 15'h0;
        tAHDefault <= 15'h0;
        tPWDDefault <= 15'h0;
        tDSDefault <= 15'h0;
        tDHDefault <= 15'h0;

        tNextWriteAdjusted <= 15'h0;
        tStartAdjusted <= 15'h0;
        tACAdjusted<= 15'h0;
        tASAdjusted<= 15'h0;
        tAHAdjusted<= 15'h0;
        tDSAdjusted<= 15'h0;
        tDHAdjusted<= 15'h0;
        tPWDAdjusted<= 15'h0;

        // Read
        ceDrivenRead <= 1'h0;
        tStartReadDefault  <= 15'h0;
        tasReadDefault  <= 15'h0;
        toedDefault  <= 15'h0;
        tprcDefault  <= 15'h0;
        tceoeEnableDefault  <= 15'h0;
        tceoeDisableDefault  <= 15'h0;
        tahReadDefault <= 15'h0;


        tStartReadAdjusted <= 15'h0;
        tasReadAdjusted <= 15'h0;
        toedAdjusted <= 15'h0;
        tprcAdjusted <= 15'h0;
        tceoeEnableAdjusted <= 15'h0;
        tceoeDisableAdjusted <= 15'h0;


        // Row-Hammering
        hammeringIterations <= 16'h0;
        hammeringDistance <= 16'h0;
        tWaitBetweenHammering <= 16'h0;
    end



    reg [(C_AXI_Light_Slave_DATA_WIDTH*BUFF_LEN)-1:0] command_buffer;
    reg [11:0] buffer_ctr = 12'h0;
    reg flush_buffer = 1'b0;

    reg[7:0] tmp_cmd = 0;
    reg flush_cmd = 0;
    reg trigger_cmd_handler_tmp = 0;
    reg[7:0] output_state_reg = 8'h0;
    
    assign trigger_cmd_handler = trigger_cmd_handler_tmp;
    assign output_state = output_state_reg;
    
    localparam STATUS_OK = 8'h00;
    localparam PROCESSING = 8'h01;
    localparam READY = 8'h02;
    localparam ERROR = 8'h03; 

    localparam IDN = 8'h00;
    localparam START_MEASUREMENT = 8'h01;
    localparam STOP_MEASUREMENT = 8'h01;
    localparam RETRIEVE_STATUS = 8'h03;
    localparam RESET = 8'h04;


    localparam RELIABLE      = 8'h00;
    localparam WRITE_LATENCY = 8'h01;
    localparam READ_LATENCY  = 8'h02;
    localparam ROW_HAMMERING = 8'h03;

    task setDefaultTimingParameters;
        begin
            $display("write_map = %b", write_map);
            ce_driven <= (received_data[23:16] > 8'h0) ? 1'b1 : 1'b0;
            if(write_map[1] == 1) begin
                tWaitAfterInit <= received_data[39:24];
                tNextRead <= received_data[55:40];
            end
            if(write_map[2] == 1) begin
                tStartDefault <= received_data[71:56];
                tnextWriteDefault <= received_data[87:72];
            end
            if(write_map[3] == 1) begin
                tACDefault <= received_data[103:88];
                tASDefault <= received_data[119:104];
            end
            if(write_map[4] == 1) begin
                tAHDefault <= received_data[135:120];
                tPWDDefault <= received_data[151:136];
            end
            if(write_map[5] == 1) begin
                tDSDefault <= received_data[167:152];
                tDHDefault <= received_data[183:168];
            end
            if(write_map[6] == 1) begin
                init_value <= received_data[199:184];
                puf_value <= received_data[215:200];
            end
            if(write_map[7] == 1) begin
                start_addr <= received_data[247:216];
            end
            if(write_map[8] == 1) begin
                stop_addr <= received_data[279:248];
                ceDrivenRead <= (received_data[287:280] > 8'h0) ? 1'b1 : 1'b0;
            end
            if(write_map[9] == 1) begin
                tStartReadDefault <= received_data[303:288];
                tasReadDefault <= received_data[319:304];
            end
            if(write_map[10] == 1) begin
                tahReadDefault <= received_data[335:320];
                toedDefault <= received_data[351:336];

            end
            if(write_map[11] == 1) begin

                tprcDefault <= received_data[367:352];
                tceoeEnableDefault <= received_data[383:368];

            end
            if(write_map[12] == 1) begin
                tceoeDisableDefault <= received_data[399:384];
                if(puf_type == RELIABLE)
                    flush_cmd <= 1'b1;
            end
        end
    endtask

    task setParametersRowHammering;
        begin
            if(write_map[13] == 1) begin
                hammeringIterations  <= received_data[431:416];
                hammeringDistance  <= received_data[447:432];
            end
            if(write_map[14] == 1) begin
                tWaitBetweenHammering <= received_data[463:448];
                flush_cmd <= 1'b1;
            end
        end
    endtask


    task setParametersWriteLatency;
        begin
            if(write_map[13] == 1) begin
                tNextWriteAdjusted <= received_data[431:416];
                tStartAdjusted <= received_data[447:432];
            end
            if(write_map[14] == 1) begin
                tACAdjusted  <= received_data[463:448];
                tASAdjusted  <= received_data[479:464];
            end
            if(write_map[15] == 1) begin
                tAHAdjusted  <= received_data[495:480];
                tDSAdjusted  <= received_data[511:496];
            end
            if(write_map[16] == 1) begin
                tDHAdjusted  <= received_data[527:512];
                tPWDAdjusted <= received_data[543:528];
                flush_cmd <= 1'b1;
            end
        end
    endtask

    task setParametersReadLatency;
        begin
            if(write_map[13] == 1) begin
                tStartReadAdjusted <= received_data[431:416];
                tasReadAdjusted <= received_data[447:432];
            end
            if(write_map[14] == 1) begin
                toedAdjusted  <= received_data[463:448];
                tprcAdjusted  <= received_data[479:464];
            end
            if(write_map[15] == 1) begin
                tceoeEnableAdjusted  <= received_data[495:480];
                tceoeDisableAdjusted  <= received_data[511:496];
                flush_cmd <= 1'b1;
            end
        end
    endtask


    always @ (posedge clk) begin
        if(flush_cmd == 1'h0) begin
            if(write_map[0] == 1) begin
                cmd <= received_data[7:0];


                if(received_data[7:0] == START_MEASUREMENT) begin
                    puf_type <= received_data[15:8];
                    setDefaultTimingParameters();
                    if(received_data[15:8] == ROW_HAMMERING) begin
                        setParametersRowHammering();
                    end

                    if(received_data[15:8] == WRITE_LATENCY) begin
                        setParametersWriteLatency();
                    end

                    if(received_data[15:8] == READ_LATENCY) begin
                        setParametersReadLatency();
                    end
                end

                if(received_data[7:0] == STOP_MEASUREMENT) begin
                    // Not fully tested
                    cmd <= received_data[7:0];
                end
                
                if(received_data[7:0] == IDN) begin
                    trigger_cmd_handler_tmp = 1;
                    output_state_reg <= STATUS_OK;
                    flush_cmd <= 1'b1;
                end
                if(received_data[7:0] == RETRIEVE_STATUS) begin
                    trigger_cmd_handler_tmp = 1;
                    output_state_reg <= STATUS_OK;
                    flush_cmd <= 1'b1;
                end

                if(received_data[7:0] == RESET) begin
                    reset_tmp <= 1'h1;
                      // General PUF definitions
                    puf_type <= 8'h0;
                    init_value <= 16'h0;
                    puf_value <= 16'h0;
                    start_addr <= 32'h00;
                    stop_addr <= 32'h00;
                    ce_driven <= 0;
            
                    // Timing
                    // Write
                    tWaitAfterInit <= 15'h0;
                    tNextRead <= 15'h0;
                    tStartDefault <= 15'h0;
                    tnextWriteDefault <= 15'h0;
                    tACDefault <= 15'h0;
                    tASDefault <= 15'h0;
                    tAHDefault <= 15'h0;
                    tPWDDefault <= 15'h0;
                    tDSDefault <= 15'h0;
                    tDHDefault <= 15'h0;
            
                    tNextWriteAdjusted <= 15'h0;
                    tStartAdjusted <= 15'h0;
                    tACAdjusted<= 15'h0;
                    tASAdjusted<= 15'h0;
                    tAHAdjusted<= 15'h0;
                    tDSAdjusted<= 15'h0;
                    tDHAdjusted<= 15'h0;
                    tPWDAdjusted<= 15'h0;
            
                    // Read
                    ceDrivenRead <= 1'h0;
                    tStartReadDefault  <= 15'h0;
                    tasReadDefault  <= 15'h0;
                    toedDefault  <= 15'h0;
                    tprcDefault  <= 15'h0;
                    tceoeEnableDefault  <= 15'h0;
                    tceoeDisableDefault  <= 15'h0;
                    tahReadDefault <= 15'h0;
            
            
                    tStartReadAdjusted <= 15'h0;
                    tasReadAdjusted <= 15'h0;
                    toedAdjusted <= 15'h0;
                    tprcAdjusted <= 15'h0;
                    tceoeEnableAdjusted <= 15'h0;
                    tceoeDisableAdjusted <= 15'h0;
            
            
                    // Row-Hammering
                    hammeringIterations <= 16'h0;
                    hammeringDistance <= 16'h0;
                    tWaitBetweenHammering <= 16'h0;
                    flush_cmd <= 1'b1;
                    
                    
                end
            end
        end else begin
            flush_cmd <= 1'h0;
            reset_tmp <= 1'h0;
            trigger_cmd_handler_tmp <= 8'h0;
        end
    end

    assign reset_out = reset_tmp;
    assign cmd_ready = flush_cmd;
endmodule
