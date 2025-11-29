`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: University of Passau - Chair of Computer Engineering
// Engineer: Florian Frank
// 
// Create Date: 01/15/2025 06:37:55 PM
// Design Name: AXI Full Interface Testbench
// Module Name: tb_axi_full
// Project Name: AXI Verification and Simulation
// Target Devices: [Specify Target Devices, e.g., Xilinx ZCU102]
// Tool Versions: Vivado 2022.2
// 
// Description: 
// Testbench to simulate specific PUF (Physically Unclonable Function) tests. 
// The simulation starts with AXI transactions to configure and write initial data 
// into memory, followed by controlled memory read and write operations. The testbench 
// drives the DUT through AXI VIP agents, verifies correct AXI communication, 
// and allows evaluation of memory-based PUF behavior. Timing parameters, read/write 
// operations, or row hammering sequences are included for thorough testing.
//
// Dependencies: 
// - axi_vip_pkg
// - axi_verifier_full_axi_vip_0_0_pkg
// - axi_verifier_full_axi_vip_1_0_pkg
// 
// Revision History:
// Rev. 0.01 - File Created
//
//////////////////////////////////////////////////////////////////////////////////

import axi_vip_pkg::*;
import axi_verifier_full_axi_vip_0_0_pkg::*;
import axi_verifier_full_axi_vip_1_0_pkg::*;
 
module tb_axi_full();

bit disable_axi_switch = 0;
bit simulate_test_button = 0;

logic[23:0] address_write;
logic[23:0] address_read;

logic[23:0] alines;
wire[15:0] dlines;
logic zz;
logic ub;
logic lb;
logic dir_const;
logic dir_var;
logic en_const;
logic en_var;
logic ref_vcc;
logic ref_vcc2;


logic oe, ce, we; 
logic[31:0] data, addr, base_addr = 32'h4000_0000;
xil_axi_resp_t 	resp;
logic clk = 0;
logic locked;
logic dcm_locked;
logic [639:0]full_frame;
logic reset = 0, aresetn= 0;
logic[31:0] slv_reg0; 

logic[7:0] puf_type;
logic[15:0] init_value;
logic[15:0] test_value;
logic[31:0] start_addr;
logic[31:0] stop_addr;
logic [3:0] outer_state;
logic [3:0] sram_state;
logic [23:0] alines_write;
logic rw_select;
logic axi_light_master_txn_done;
logic axi_test_wire = 1;

bit ce_driven;
bit start_read_dbg_out;
logic [15:0] tNextRead;
logic [15:0] tStartDefault;
logic [15:0] tStartDefault;
logic [15:0] tACDefault;
logic [15:0] tASDefault;
logic [15:0] tAHDefault;
logic [15:0] tPWDDefault;
logic [15:0] tDHDefault;
logic [15:0] tDSDefault;
logic [15:0] tnextWriteDefault;

 logic [15:0] tNextWriteAdjusted;
 logic [15:0] tStartAdjusted;
 logic [15:0] tACAdjusted;
 logic [15:0] tASAdjusted;
 logic [15:0] tAHAdjusted;
 logic [15:0] tDSAdjusted;
 logic [15:0] tDHAdjusted;
 logic [15:0] tPWDAdjusted;
 logic [15:0] tWaitAfterInit;

 		// Read Timing 
  logic ceDrivenRead;
  logic [15:0] tStartReadDefault;
  logic [15:0] tasReadDefault;
  logic [15:0] toedDefault;
  logic [15:0] tprcDefault;
  logic [15:0] tceoeEnableDefault;
  logic [15:0] tceoeDisableDefault;

  logic [15:0] tStartReadAdjusted;
  logic [15:0] tasReadAdjusted;
  logic [15:0] toedAdjusted;
  logic [15:0] tprcAdjusted;
  logic [15:0] tceoeEnableAdjusted;
  logic [15:0] tceoeDisableAdjusted;
  
  //logic [15:0] tohi;
  //logic [15:0] tah;

// Row Hammering
logic [15:0]tWaitBetweenHammering;
logic [15:0]hammeringDistance;
logic [15:0]hammeringIterations;

bit cmd_ready;
logic [7:0] cmd;
logic trigger_axi_master_start;

    axi_verifier_full_wrapper  UUT(.*);
    
initial begin 
  slv_reg0 <= 32'h0;
  dcm_locked <= 1;    
  aresetn = 0;
  #340ns
  aresetn = 1;
end

axi_verifier_full_axi_vip_0_0_mst_t master_agent;
axi_verifier_full_axi_vip_1_0_slv_mem_t slv_agent;


initial begin    
    data = 32'h0;
    addr = 32'h0;
    master_agent = new("master vip agent", UUT.axi_verifier_full_i.axi_vip_0.inst.IF);
    slv_agent = new("master vip agent", UUT.axi_verifier_full_i.axi_vip_1.inst.IF);
    slv_agent.set_verbosity(400);

    slv_agent.start_slave();
    master_agent.start_master();
    

    wait (aresetn == 1'b1);
    #10
    addr = 32'h0;
  data = 32'h55_55_55_55;

// AXI interface definition. See readme md or ps_pl interface documentation for more information
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h0, 0, 32'h0A_FF_00_01, resp);
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h4, 0, 32'h03_03_E8_00, resp);
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h8, 0, 32'h00_01_F4_00, resp);
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'hc, 0, 32'h00_00_00_00, resp);
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h10, 0, 32'h0A_00_08_00, resp);
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h14, 0, 32'h55_00_00_00, resp);
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h18, 0, 32'h00_AA_AA_55, resp);
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h1c, 0, 32'hFF_00_00_00, resp);
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h20, 0, 32'hFF_00_00_7F, resp);
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h24, 0, 32'h00_09_00_0A, resp);
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h28, 0, 32'h00_1E_00_08, resp);
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h2c, 0, 32'h00_00_00_1F, resp);
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h30, 0, 32'h00_00_00_00, resp);
#12000

$finish;
end

initial begin 
 forever #5 clk = ~clk;
end


endmodule