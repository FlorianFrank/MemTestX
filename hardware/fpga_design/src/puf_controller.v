//////////////////////////////////////////////////////////////////////////////////
// Company: University of Passau – Chair of Computer Engineering
// Engineer: Florian Frank
// 
// Create Date: 03/12/2024 02:14:09 PM
// Design Name: puf_controller.v
// Module Name: puf_controller
// Project Name: memory_evaluator
// Target Device: Xilinx ZCU102
// Tool Version: Vivado 2022.2
// 
// Description: 
// This module receives a set of configuration parameters for PUF experiments 
// and controls the initialization and execution of memory operations through 
// interaction with the memory controller. It implements experiment execution 
// using dedicated state machines. Currently, row hammering experiments and 
// timing variation experiments (e.g., reliable read/write operations) are 
// supported. The module also synchronizes with the AXI controller to transmit 
// measurement data obtained from the memory reader.
// 
// Revision History:
// Rev. 0.01 - File Created
//
//////////////////////////////////////////////////////////////////////////////////

`define TIMING_PARAMETER_WIDTH              16
`define HAMMERING_ITERATION_BIT_WIDTH       16
`define HAMMERING_DISTANCE_BIT_WIDTH        16
`define NR_STATES                           10


module puf_execution_controller#(
    parameter integer GENERAL_DATA_SIZE = 16,
    parameter integer GENERAL_ADDRESS_SIZE = 32,
    parameter integer MEMORY_MODULE_ADDRESS_SIZE = 15,
    parameter integer AXI_OUTPUT_DATA_SIZE = 16,
    parameter integer AXI_OUTPUT_ADDRESS_SIZE = 32,
    parameter integer MEMORY_MODULE_DATA_SIZE = 8,
    parameter integer DELAY_READ_WRITE=2,
    parameter integer MAX_ADDRESS= 23'h7fff
)(
    input wire clk,
    input wire locked,
    
    input wire[7:0] puf_type,    
    
    input wire [GENERAL_DATA_SIZE-1:0] init_value, // PUF initialization value
    input wire [GENERAL_DATA_SIZE-1:0] test_value,
    input wire [MEMORY_MODULE_DATA_SIZE-1:0] data_in, // Data received from the memory read controller
    input wire [GENERAL_ADDRESS_SIZE-1:0] start_addr,
    input wire [GENERAL_ADDRESS_SIZE-1:0] end_addr,
    
    
    output wire [AXI_OUTPUT_ADDRESS_SIZE-1:0] output_address, // Address transmitted to the AXI controller
    output wire [AXI_OUTPUT_DATA_SIZE-1:0] output_data, // Data transmitted to the AXI Controller
    output reg [MEMORY_MODULE_ADDRESS_SIZE-1:0] address_write,
    output reg [MEMORY_MODULE_ADDRESS_SIZE-1:0] max_address,
    output reg  [MEMORY_MODULE_ADDRESS_SIZE-1:0] address_read,
    output reg  [MEMORY_MODULE_DATA_SIZE-1:0] value_write,
    
    output reg trigger_axi_master_start, // transmission of data via the AXI interface
    output reg start_read, // Trigger start memory read module
    output reg start_write, // Trigger start memory write module
    output reg rw_select, // Select either read or write direction, required by the multiplexer 0 indicates writing 1 indicates reading
    output reg write_continuously, // Write full memory space at once until done is returned by the memory controller, otherwise write address by address.

    input wire axi_master_done, // Indicates that data was successfully transmitted via the AXI interface
    input wire axi_active, // AXI is currently active and no further requirests can be scheduled
    input wire simulate_test_button, // Test button used to start a test without interaction with the PL
    input wire disable_axi_switch, // Switch to disable the AXI interface in order to not block the test execution for test purposes
    input wire axi_transmission_active,
    input wire write_active, 
    input wire read_active,
    input wire read_done,
    input wire write_done,
    input wire set_back,
    
    input wire ceDrivenIn,
    input wire ceDrivenReadIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tnextWriteDefaultIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tStartDefaultIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tACDefaultIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tASDefaultIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tAHDefaultIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tDSDefaultIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tDHDefaultIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tPWDDefaultIn,
    
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tnextWriteAdjustedIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tStartAdjustedIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tACAdjustedIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tASAdjustedIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tAHAdjustedIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tDSAdjustedIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tDHAdjustedIn,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tPWDAdjustedIn,
    
    input wire [`TIMING_PARAMETER_WIDTH-1:0] tWaitAfterInit,
    input wire [`TIMING_PARAMETER_WIDTH-1:0] tNextRead,
    
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tStartReadDefault,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tasReadDefault,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tahReadDefault,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] toedDefault,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tprcDefault,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tceoeEnableDefault,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tceoeDisableDefault,
    
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tStartReadAdjusted,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tasReadAdjusted,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tahReadAdjusted,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] toedAdjusted,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tprcAdjusted,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tceoeEnableAdjusted,
    input wire[`TIMING_PARAMETER_WIDTH-1:0] tceoeDisableAdjusted,
    
    
    output reg ceDriven, // If 1 the memory module is driven by the CE signal. Therefore a read or write request is initiated by active CE. Otherwise active OE or WE is used.
    output reg ceDrivenRead,

    output reg [`TIMING_PARAMETER_WIDTH-1:0] tnext,   // Delay between two write operations
    output reg [`TIMING_PARAMETER_WIDTH-1:0] tStart, // Delay before start
    output reg [`TIMING_PARAMETER_WIDTH-1:0] tac,    // Access time
    output reg [`TIMING_PARAMETER_WIDTH-1:0] tas,    // Address setup time
    output reg [`TIMING_PARAMETER_WIDTH-1:0] tah,    // Address hold time
    output reg [`TIMING_PARAMETER_WIDTH-1:0] tds,    // Data setup time
    output reg [`TIMING_PARAMETER_WIDTH-1:0] tdh,    // Data hold time
    output reg [`TIMING_PARAMETER_WIDTH-1:0] tpwd,   // Pulse width duration
    
    output reg[`TIMING_PARAMETER_WIDTH-1:0] tStartRead,
    output reg[`TIMING_PARAMETER_WIDTH-1:0] tasRead,
    output reg[`TIMING_PARAMETER_WIDTH-1:0] toed,
    output reg[`TIMING_PARAMETER_WIDTH-1:0] tprc,
    output reg[`TIMING_PARAMETER_WIDTH-1:0] tceoeEnable,
    output reg[`TIMING_PARAMETER_WIDTH-1:0] tceoeDisable,
    
    input wire [`TIMING_PARAMETER_WIDTH-1:0] tWaitBetweenHammering,
    input wire [`HAMMERING_ITERATION_BIT_WIDTH-1:0] hammeringIterations,
    input wire [`HAMMERING_DISTANCE_BIT_WIDTH-1:0] hammeringDistance
    
`ifdef DEBUG
    ,
    output wire [$clog2(`NR_STATES)-1:0] puf_executer_state
`endif
);


    // State Definitions
    localparam INIT                     = 4'h0;
    localparam TRANSMIT_TO_PS           = 4'h1;
    localparam WAIT_FOR_START           = 4'h2;
    localparam WAIT_PS_TRANSMISSION_DONE = 4'h3;
    localparam SLEEP_BETWEEN_READS      = 4'h4;
    localparam DONE                     = 4'h5;
    localparam START_READ               = 4'h6;
    localparam WAIT_READ_FINISH         = 4'h7;
    localparam START_WRITE              = 4'h8;
    localparam WAIT_WRITE_FINISH        = 4'h9;
    localparam START_WRITE_REDUCED      = 4'h0A;
    localparam START_ROW_HAMMERING      = 4'h0B;
    localparam START_READ_REDUCED        = 4'h0C;


    localparam RELIABLE      = 8'h00;
    localparam WRITE_LATENCY = 8'h01;
    localparam READ_LATENCY  = 8'h02;
    localparam ROW_HAMMERING = 8'h03;

    // Internal Signals
    reg [$clog2(`NR_STATES)-1:0] state = INIT;
    integer timing_ctr = 0;
    reg[`HAMMERING_ITERATION_BIT_WIDTH-1:0] hammering_iterations_ctr = 0;
    
    
    reg [AXI_OUTPUT_ADDRESS_SIZE-1:0] output_address_tmp = {AXI_OUTPUT_ADDRESS_SIZE{1'h0}};
    reg [AXI_OUTPUT_DATA_SIZE-1:0] output_data_tmp = {AXI_OUTPUT_DATA_SIZE{1'h0}};
    
    reg axi_triggered = 0;
    integer hammerCtr = 0;
    

`ifdef DEBUG
    reg [AXI_OUTPUT_ADDRESS_SIZE-1:0] output_address_tmp_ctr = 0; 

    assign output_address = output_address_tmp_ctr; 
    //assign max_address = MAX_ADDRESS;
  //  assign address_write = (write_continuously == 1'b1) ? 15'h0 : output_address_tmp[MEMORY_MODULE_ADDRESS_SIZE-1:0];
    assign output_data = ~output_address_tmp_ctr;
    
    always @ (posedge axi_master_done) begin 
        output_address_tmp_ctr <= output_address_tmp_ctr + 32'h1;
    end
`else
    assign output_address = output_address_tmp; 
    //assign max_address = MAX_ADDRESS;
  //  assign address_write = (write_continuously == 1'b1) ? 15'h0 : output_address_tmp[MEMORY_MODULE_ADDRESS_SIZE-1:0];
    assign output_data = output_data_tmp;
`endif     
    reg test_done = 0;
    reg first_test_run = 1;
    reg lock_hammering_iteration = 0;
    
    
    
    initial begin
        max_address <= MAX_ADDRESS;
        rw_select <= 1'b0;
        start_read <= 1'b0;
        start_write <= 1'b0;
        value_write <= {AXI_OUTPUT_DATA_SIZE/8{8'h55}};
        address_read <= {MEMORY_MODULE_ADDRESS_SIZE{1'h0}};
        
        write_continuously <= 1'h1;
        ceDriven <= 1'h1;
        tnext <= `TIMING_PARAMETER_WIDTH'd5;
        tStart <= `TIMING_PARAMETER_WIDTH'd0;
        tas <= `TIMING_PARAMETER_WIDTH'd2;
        tah <= `TIMING_PARAMETER_WIDTH'd2;
        tac <= `TIMING_PARAMETER_WIDTH'd2;
        tdh <= `TIMING_PARAMETER_WIDTH'd2;
        tpwd <= `TIMING_PARAMETER_WIDTH'd0;
        tds <= `TIMING_PARAMETER_WIDTH'd0;
        address_write <= {MEMORY_MODULE_ADDRESS_SIZE{1'h0}};
        address_read <= {MEMORY_MODULE_ADDRESS_SIZE{1'h0}};
    end


    task startInitWrite;
    begin 
    
        // Set Default Timing Specification    
        tnext <=  tnextWriteDefaultIn;
        tStart <= tStartDefaultIn;
        tac <= tACDefaultIn;
        tas <= tASDefaultIn;
        tah <= tAHDefaultIn;
        tds <= tDSDefaultIn;
        tdh <= tDHDefaultIn;
        tpwd <= tPWDDefaultIn;  
    
        max_address <= end_addr[MEMORY_MODULE_ADDRESS_SIZE-1:0];
        address_write <= start_addr[MEMORY_MODULE_ADDRESS_SIZE-1:0];
        
        
        rw_select <= 0;
        write_continuously <= 1'b1;
        value_write <= init_value[7:0];
        if(write_active) begin
            start_write <= 0;
            state <= WAIT_WRITE_FINISH;
        end else begin 
            start_write <= 1;
        end
        end
    endtask
    
    task startWriteReduced;
        begin 
        
        // Set Default Timing Specification    
        tnext <=  tnextWriteAdjustedIn; // TODO adjusted
        tStart <= tStartDefaultIn; // TODO Adjusted
        tac <= tACAdjustedIn;
        tas <= tASAdjustedIn;
        tah <= tAHAdjustedIn;
        tds <= tDSAdjustedIn;
        tdh <= tDHAdjustedIn;
        tpwd <= tPWDAdjustedIn;  
        
        
        max_address <= end_addr[MEMORY_MODULE_ADDRESS_SIZE-1:0];
        address_write <= start_addr[MEMORY_MODULE_ADDRESS_SIZE-1:0];
        
        
        if(timing_ctr < tWaitAfterInit) begin 
            timing_ctr <= timing_ctr + 1;
        end else begin
            timing_ctr <= 0;
            rw_select <= 0;
            write_continuously <= 1'b1;
            value_write <= test_value[7:0];
            if(write_active) begin
                start_write <= 0;
                test_done <= 1'h1;
                state <= WAIT_WRITE_FINISH;
            end else begin 
                start_write <= 1;
            end
        end
        end
    endtask
    
    
task startRowHammering;
    begin
        if (first_test_run) begin
            // Initialize the maximum address and write address
            max_address <= hammeringDistance-1;
            address_write <= start_addr[MEMORY_MODULE_ADDRESS_SIZE-1:0];
            $display("SET MAX ADDRESS %x, %x", max_address, address_write);

            // Increment timing counter until it reaches the wait threshold
            if (timing_ctr < tWaitAfterInit) begin
                timing_ctr <= timing_ctr + 1;
            end else begin

                // Reset timing counter and configure for writing
                rw_select <= 1'b0; // Set read/write selection to write mode
                write_continuously <= 1'b1;
                value_write <= test_value[7:0];

                // Handle write operation based on active write state
                if (write_active) begin
                    timing_ctr <= 0;
                    // Set first_test_run to false after initial setup
                    first_test_run <= 1'b0;
                    start_write <= 1'b0;
                    hammering_iterations_ctr <= hammering_iterations_ctr + 1; 
                    state <= WAIT_WRITE_FINISH;
                end else begin
                    start_write <= 1'b1;
                end
            end
        end else begin
                    // Increment timing counter until it reaches the wait threshold
            if (timing_ctr < tWaitBetweenHammering) begin
                timing_ctr <= timing_ctr + 1;
            end else begin
                
                if(lock_hammering_iteration == 1'h0) begin
                    if(hammering_iterations_ctr >= hammeringIterations) begin
                        if(max_address == end_addr[MEMORY_MODULE_ADDRESS_SIZE-1:0]) begin 
                            test_done <= 1'h1;
                        //end else if(max_address + (2*hammeringDistance)> end_addr) begin 
                         //   max_address <= end_addr;
                          //  address_write <= (end_addr - hammeringDistance) + 1; // TODO Double check;
                        end else begin
                            // If no full read cycle avilable at the end use the remaining space for further hammering
                            if( max_address + (3*hammeringDistance) > end_addr[MEMORY_MODULE_ADDRESS_SIZE-1:0]) 
                                max_address <= end_addr[MEMORY_MODULE_ADDRESS_SIZE-1:0];
                            else 
                                max_address <= max_address + (2*hammeringDistance);
                            address_write <= address_write + (2*hammeringDistance);
                        end 
                        $display("INCREMENT_ADDRESS %x %x", address_write, max_address);
                        hammering_iterations_ctr <= 1;
                    end else begin 
                        $display("HAMMER Iteration %x/%x", hammering_iterations_ctr, hammeringIterations);
                        hammering_iterations_ctr <= hammering_iterations_ctr + 1; 
                    end
                end begin 
                    lock_hammering_iteration <= 1'h1;
                end                
                rw_select <= 1'b0; // Set read/write selection to write mode
                write_continuously <= 1'b1;
                value_write <= test_value[7:0];

                // Handle write operation based on active write state
                if (write_active) begin
                    timing_ctr <= 0;
                    start_write <= 1'b0;
                    state <= WAIT_WRITE_FINISH;
                end else begin
                    start_write <= 1'b1;
                end
            end
        end
    end
endtask

    task waitFinishInitWrite;
    begin
        lock_hammering_iteration <= 1'h0;
        if (write_done) begin
            rw_select <= 0;
            if(puf_type == WRITE_LATENCY && test_done != 1) begin
                    timing_ctr <= 0; 
                    state <= START_WRITE_REDUCED;
            end else if(puf_type == READ_LATENCY) begin 
                state <= START_READ_REDUCED;
                timing_ctr <= 0;
            end else if (puf_type == ROW_HAMMERING && test_done != 1) begin
                    timing_ctr <= 0; 
                    state <= START_ROW_HAMMERING;
             end
            
            if (timing_ctr < DELAY_READ_WRITE)
                timing_ctr <= timing_ctr + 1;
            else begin
                if(puf_type == RELIABLE || (puf_type != READ_LATENCY && test_done == 1'h1)) begin
                   state <= START_READ;
                end
                timing_ctr <= 0;
            end
        end
      end
    endtask
    
    task startGenericRead;
    begin
    
        tStartRead <= tStartReadDefault; 
        tasRead <= tasReadDefault;    
        toed <= toedDefault;       
        tprc <= tprcDefault;       
        tceoeEnable <= tceoeEnableDefault;
        tceoeDisable <= tceoeDisableDefault;
    
        rw_select <= 1;
        address_read <= output_address_tmp[MEMORY_MODULE_ADDRESS_SIZE-1:0];
        start_read <= 1;
        state <= WAIT_READ_FINISH;
    end
    endtask
    
    task startReadReduced;
    begin
    
        tStartRead <= tStartReadAdjusted; 
        tasRead <= tasReadAdjusted;    
        toed <= toedAdjusted;       
        tprc <= tprcAdjusted;       
        tceoeEnable <= tceoeEnableAdjusted;
        tceoeDisable <= tceoeDisableAdjusted;
    
        rw_select <= 1;
        address_read <= output_address_tmp[MEMORY_MODULE_ADDRESS_SIZE-1:0];
        start_read <= 1;
        state <= WAIT_READ_FINISH;
    end
    endtask
    
    task waitReadDone;
    begin
            start_read <= 0;
        if (read_done) begin
            output_data_tmp[7:0] <= data_in;
            output_data_tmp[15:8] <= 8'h0;
            state <= TRANSMIT_TO_PS;
        end
    end
    endtask
    
    task sleepBetweenReads;
    begin
      if (timing_ctr < (tNextRead * 100))
            timing_ctr <= timing_ctr + 1;
        else begin
            timing_ctr <= 0;
            if(puf_type == READ_LATENCY)
                state <= START_READ_REDUCED;
            else 
                state <= START_READ;
        end
    end
    endtask
   
    
    task transmitToPS;
        begin
        if(axi_triggered == 0)
            trigger_axi_master_start <= 1'b1;
            
                if(axi_master_done == 1'b0 || disable_axi_switch == 1'b1) begin
                    axi_triggered <= 1;
                    if(axi_triggered == 1) begin 
                        trigger_axi_master_start <= 1'b0;
                        state <= WAIT_PS_TRANSMISSION_DONE;
                    end 
                end
                else
                    trigger_axi_master_start <= 1'b1;
          end
     endtask
     
     
     task waitPSTransmissionDone;
        begin 
                          if (axi_master_done == 1'b1 || disable_axi_switch == 1'b1) begin
                                trigger_axi_master_start <= 1'b0;
                                
                                if (puf_type == ROW_HAMMERING) begin
                                    
                                    if(hammerCtr == hammeringDistance - 1) begin 
                                        hammerCtr <= 0;
                                        output_address_tmp <= output_address_tmp + hammeringDistance + 1;
                                    end else begin
                                        output_address_tmp <= output_address_tmp + 1;
                                        hammerCtr <= hammerCtr + 1;
                                    end 
                                end else begin
                                    output_address_tmp <= output_address_tmp + 1;
                                end
                    
                    if(output_address_tmp < max_address)
                        state <= SLEEP_BETWEEN_READS;
                    else begin
                        output_address_tmp <= start_addr[MEMORY_MODULE_ADDRESS_SIZE-1:0];
                        state <= INIT;
                    end
                end
        end
     endtask


    always @(posedge clk) begin //or posedge reset) begin
        if(set_back == 1) begin 
            state <= INIT;
            output_address_tmp <= {AXI_OUTPUT_ADDRESS_SIZE{1'h0}};
            output_data_tmp <= {AXI_OUTPUT_DATA_SIZE{1'h0}}; 
            timing_ctr <= 0;
            axi_triggered <= 0;
            test_done <= 0;
            hammering_iterations_ctr <= 0;
            first_test_run <= 1;
        lock_hammering_iteration <= 0;
        end else begin 
        case (state)
            INIT: begin
                test_done <= 0;
                first_test_run <= 1;
                trigger_axi_master_start <= 1'b0;
                    if((simulate_test_button == 1'b1 || axi_active == 1'b1) && locked) begin
                        timing_ctr <= 0;
                        
                        if(puf_type == ROW_HAMMERING) 
                            output_address_tmp <= start_addr[MEMORY_MODULE_ADDRESS_SIZE-1:0] + hammeringDistance;
                        else
                            output_address_tmp <= start_addr[MEMORY_MODULE_ADDRESS_SIZE-1:0];

                        
                        ceDrivenRead <= ceDrivenReadIn;
                        ceDriven <= ceDrivenIn;
                         state <= START_WRITE;
                end
            end

                /* Initial Fill memory with known value */
                START_WRITE: begin
                    startInitWrite();
                end
    
                WAIT_WRITE_FINISH: begin
                    waitFinishInitWrite();
                end
    
    
    
                /* READ results */
                START_READ: begin
                    startGenericRead();
                end
                
                START_READ_REDUCED: begin 
                    startReadReduced();
                end
    
                WAIT_READ_FINISH: begin
                    waitReadDone();
                end
    
                SLEEP_BETWEEN_READS: begin
                    sleepBetweenReads();
                end
    
    
                // States for the test execution
                START_WRITE_REDUCED: begin 
                    startWriteReduced();
                end
                
                START_ROW_HAMMERING: begin 
                    startRowHammering();
                end
    
                    
                /* Transmit result value to PS via AXI bus*/
                TRANSMIT_TO_PS: begin
                    transmitToPS();
                end
    
                WAIT_PS_TRANSMISSION_DONE: begin
                    waitPSTransmissionDone();
                end
    
    
            endcase
        end
    end
    
`ifdef DEBUG
    assign puf_executer_state = state;
`endif
    
endmodule
