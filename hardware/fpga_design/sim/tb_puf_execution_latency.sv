`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/14/2025 08:54:23 AM
// Design Name: 
// Module Name: tb_puf_executor_write_latency
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

`define     RELIABLE        8'h00;
`define     WRITE_LATENCY   8'h01;
`define     READ_LATENCY    8'h02;
`define     ROW_HAMMERING   8'h03;

`define TIMING_BUS_WIDTH    16

module tb_puf_executor_write_latency;

    // Signal Declarations
    logic          clk;
    logic          clk2;
    logic          axi_master_done;
    logic          trigger_axi_master_start;
    logic  [31:0]  output_address;
    logic  [15:0]  output_data;
    logic          axi_active;
    logic          test_switch;
    
    logic  [14:0]  address_read;
    logic  [14:0]  address_write;
    logic  [14:0]  max_address;
    logic   [7:0]  value_write;
    logic          start_read;
    logic          start_write;
    logic   [7:0]  data_in;
    logic          read_done;
    logic          write_done;
    logic          rw_select;
    logic          locked;

    
    logic          reset;
    logic          write_active;
    logic          write_continously;
    logic          ceDriven;

    logic  [15:0]  tnext;
    logic  [15:0]  tStart; // Delay before start
    logic  [15:0]  tac;    // Access time
    logic  [15:0]  tas;    // Address setup time
    logic  [15:0]  tah;    // Address hold time
    logic  [15:0]  tds;    // Data setup time
    logic  [15:0]  tdh;    // Data hold time
    logic  [15:0]  tpwd;   // Pulse width duration

    logic   [7:0]  dlines;
    logic  [14:0]  alines;
    logic          ce;   
    logic          oe;
    logic          we;

    logic   [3:0]  state_mem;
    logic   [3:0]  read_state;
    logic   [3:0]  puf_executer_state;

    logic   [7:0]  init_value;
    logic   [7:0]  test_value;
    logic          simulate_test_button;
    logic          disable_axi_switch;
    
    logic   [8:0]  input_dlines;
    logic   [8:0]  output_alines;
    logic          ce_read;
    logic          oe_read;
       
    logic [15:0] hammeringIterations;
    logic [15:0] hammeringDistance;
    
    logic [7:0] puf_type;
    
    
    logic ceDrivenIn;
    
        // WriteTiming
    logic[`TIMING_BUS_WIDTH-1:0] tWaitAfterInit;        
        
    logic[`TIMING_BUS_WIDTH-1:0] tWaitBetweenHammering;
    logic[`TIMING_BUS_WIDTH-1:0] tNextRead;
    
    
    // Write Timing for initialization
    logic[`TIMING_BUS_WIDTH-1:0] tStartDefaultIn;
    logic[`TIMING_BUS_WIDTH-1:0] tnextWriteDefaultIn;    
    logic[`TIMING_BUS_WIDTH-1:0] tACDefaultIn;
    logic[`TIMING_BUS_WIDTH-1:0] tASDefaultIn;
    logic[`TIMING_BUS_WIDTH-1:0] tAHDefaultIn;
    logic[`TIMING_BUS_WIDTH-1:0] tDSDefaultIn;
    logic[`TIMING_BUS_WIDTH-1:0] tDHDefaultIn;
    logic[`TIMING_BUS_WIDTH-1:0] tPWDDefaultIn;
    
    // Write Timing for latency tests
    logic[`TIMING_BUS_WIDTH-1:0] tnextWriteAdjustedIn;
    logic[`TIMING_BUS_WIDTH-1:0] tStartAdjustedIn; 
    logic[`TIMING_BUS_WIDTH-1:0] tACAdjustedIn;
    logic[`TIMING_BUS_WIDTH-1:0] tASAdjustedIn;
    logic[`TIMING_BUS_WIDTH-1:0] tAHAdjustedIn;
    logic[`TIMING_BUS_WIDTH-1:0] tDSAdjustedIn;
    logic[`TIMING_BUS_WIDTH-1:0] tDHAdjustedIn;
    logic[`TIMING_BUS_WIDTH-1:0] tPWDAdjustedIn;
        
    
    
    

    // Clock Generation
    initial begin
        clk = 1'b0;
        forever #4 clk = ~clk;
    end
    
        // Clock Generation
    initial begin
        clk2 = 1'b0;
        forever #1 clk2 = ~clk2;
    end

    // Initialization
// Initialization
initial begin
    // Initialize Timing Parameters
    ceDrivenIn <= 1'h1;
    tStartDefaultIn <= 16'h2;
    tnextWriteDefaultIn <= 16'h10;    
    tACDefaultIn <= 16'h2;
    tASDefaultIn <= 16'h2;
    tAHDefaultIn <= 16'h2;
    tDSDefaultIn <= 16'h2;
    tDHDefaultIn <= 16'h2;
    tPWDDefaultIn <= 16'h2;
    
    tnextWriteAdjustedIn <= 16'h10;
    tStartAdjustedIn     <= 16'h1;
    tACAdjustedIn        <= 16'h1;
    tASAdjustedIn        <= 16'h1;
    tAHAdjustedIn        <= 16'h1;
    tDSAdjustedIn        <= 16'h1;
    tDHAdjustedIn        <= 16'h1;
    tPWDAdjustedIn       <= 16'h1;
    
    

    // Configuration Parameters
    puf_type               <= `ROW_HAMMERING; // RELIABLE MODE
    hammeringIterations     <= 16'h3;
    hammeringDistance       <= 16'h2;
    tWaitBetweenHammering   <= 16'h0;
    tWaitAfterInit          <= 16'h10;
    tNextRead               <= 8'h1;

    // Initial Values for Test and Memory
    init_value              <= 8'h55;
    test_value              <= 8'haa;
    input_dlines            <= 8'h55;

    // Control Signals
    clk                     <= 1'b0;
    read_done               <= 1'b0;
    locked                  <= 1'b1;
    reset                   <= 1'b0;
    axi_master_done         <= 1'b0;
    axi_active              <= 1'b0;
    test_switch             <= 1'b0;
    simulate_test_button    <= 1'b0;
    disable_axi_switch      <= 1'b1;

    // Trigger AXI activity
    #10 axi_active          <= 1'b1;
    #10 axi_active          <= 1'b0;

    // Finish Simulation
    #50000
    $finish;
end
    // Module Instantiations
    puf_exection_controller #(
        .MEMORY_MODULE_ADDRESS_SIZE(15), 
        .MEMORY_MODULE_DATA_SIZE(8),
        .MAX_ADDRESS(11)
    ) pufExecController (.*);

    memory_write_top_module #(
        .FREQ_CLK1(100), 
        .FREQ_CLK2(400), 
        .ADDRESS_BUS_SIZE(15), 
        .DATA_BUS_SIZE(8), 
        .DATA_BUS_SIZE_OUT(8), 
        .CLOCK_CONFIG_WIDTH(16)
    ) memory_write_module_inst (.*);

    memory_read_top_module #(
        .FREQ_CLK1(100),
        .FREQ_CLK2(400), 
        .ADDRESS_BUS_SIZE(15), 
        .DATA_BUS_SIZE_OUT(8), 
        .DATA_BUS_SIZE(8), 
        .SEPERATE_OE_CE(0), 
        .TSETUP(8), 
        .TAS(1), 
        .TOECE(1), 
        .TPRC(1), 
        .TPRC_REDUCED(30), 
        .TNEXT(1)
    ) memory_read_top_module_instance (
        .clk1(clk),
        .clk2(clk2), 
        .start(start_read), 
        .reset(reset), 
        .dlines(input_dlines), 
        .value(data_in), 
        .alines(output_alines), 
        .ce(ce_read), 
        .oe(oe_read), 
        .ready(read_done), 
        .sram_state(read_state), 
        .address(address_read)
    );

endmodule
