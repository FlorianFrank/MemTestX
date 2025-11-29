`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: University of Passau – Chair of Computer Engineering
// Engineer: Florian Frank
// 
// Create Date: 01/15/2025 06:37:55 PM
// Design Name: AXI Interface Testbench
// Module Name: tb_axi_interface
// Project Name: AXI Verification and Simulation
// Target Devices: [Specify Target Devices, e.g., Xilinx ZCU102]
// Tool Versions: Vivado 2022.2
// 
// Description: 
// Testbench to verify the basic functionality of an AXI interface. 
// This simulation exercises AXI read and write operations by driving 
// transactions through AXI VIP agents to the DUT. It initializes memory 
// locations, performs sequential writes, and optionally simulates row 
// hammering sequences. The focus is purely on testing correct AXI signaling, 
// timing, and transaction behavior.
//
// Dependencies: 
// - axi_vip_pkg
// - axi_verification_axi_vip_0_0_pkg
// - axi_verification_axi_vip_1_0_pkg
// 
// Revision History:
// Rev. 0.01 - File Created
//
//////////////////////////////////////////////////////////////////////////////////

import axi_vip_pkg::*;
import axi_verification_axi_vip_0_0_pkg::*;
import axi_verification_axi_vip_1_0_pkg::*;
 
module tb_axi_interface();

bit clk = 0, areset = 1;
bit [31:0] data, addr, base_addr = 32'h4000_0000;
xil_axi_resp_t 	resp;
logic clk;
logic dcm_locked;
logic [19:0] write_map_out;
logic [639:0]full_frame;
logic resetn = 1;
logic[31:0] slv_reg0; 
logic[9:0] test;

logic[7:0] puf_type;
logic[15:0] init_value;
logic[15:0] test_value;
logic[31:0] start_addr;
logic[31:0] stop_addr;



bit ce_driven;
logic [15:0] twaitAfterInit;
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

// Read
logic ceDrivenRead;
logic [15:0] tStartReadDefault;
logic [15:0] tasReadDefault;
logic [15:0] toedDefault;
logic [15:0] tprcDefault;
logic [15:0] tceoeEnableDefault;
logic [15:0] tceoeDisableDefault;
logic [15:0] tahReadDefault;

logic [15:0] tStartReadAdjusted;
logic [15:0] tasReadAdjusted;
logic [15:0] toedAdjusted;
logic [15:0] tprcAdjusted;
logic [15:0] tceoeEnableAdjusted;
logic [15:0] tceoeDisableAdjusted;
logic [15:0] tahReadAdjusted;

logic [15:0] sackl;

assign sackl = (write_map_out[12] == 1) ? full_frame[399:384] : 0;

// Row Hammering
logic [15:0]tWaitBetweenHammering;
logic [15:0]hammeringDistance;
logic [15:0]hammeringIterations;

bit cmd_ready;
logic [7:0] cmd;


    axi_verification_wrapper  UUT(.*);
    
initial begin 
  slv_reg0 <= 32'h0;
  dcm_locked <= 1;    
  areset = 0;
  #340ns
  areset = 1;
end

axi_verification_axi_vip_0_0_mst_t master_agent;
axi_verification_axi_vip_1_0_slv_mem_t slv_agent;
//
initial begin    
    master_agent = new("master vip agent", UUT.axi_verification_i.axi_vip_0.inst.IF);
    slv_agent = new("master vip agent", UUT.axi_verification_i.axi_vip_1.inst.IF);
    slv_agent.set_verbosity(400);


    master_agent.start_master();
    slv_agent.start_slave();

    wait (areset == 1'b1);
    #10
    addr = 32'h0;
  data = 32'h55_55_55_55;

  // Row hammering
  master_agent.AXI4LITE_WRITE_BURST(base_addr + 32'd36, 0, 32'h00_20_22_22, resp);
  master_agent.AXI4LITE_WRITE_BURST(base_addr + 32'd40, 0, 32'h00_00_00_09, resp);*/
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h0, 0, 32'h12_FF_02_01, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h4, 0, 32'h03_00_02_00, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h8, 0, 32'h05_00_04_00, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'hc, 0, 32'h07_00_06_00, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h10, 0, 32'h09_00_08_00, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h14, 0, 32'h55_00_0A_00, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h18, 0, 32'h78_AA_AA_55, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h1c, 0, 32'h32_12_34_56, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h20, 0, 32'hFF_98_76_54, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h24, 0, 32'h00_09_00_0A, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h28, 0, 32'h00_07_00_08, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h2c, 0, 32'h00_05_00_06, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h30, 0, 32'h00_00_00_04, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h34, 0, 32'h00_0A_00_0B, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h38, 0, 32'h00_07_00_08, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h3c, 0, 32'h00_05_00_06, resp);
 master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h40, 0, 32'h00_00_00_00, resp);

#4000
master_agent.AXI4LITE_WRITE_BURST(base_addr + addr, 0, 32'h00_22_03_01, resp);
  master_agent.AXI4LITE_WRITE_BURST(base_addr + 32'h4, 0, 32'h01_22_33_44, resp);
  master_agent.AXI4LITE_WRITE_BURST(base_addr + 32'h8, 0, 32'h55_66_77_88, resp);
  master_agent.AXI4LITE_WRITE_BURST(base_addr + 32'd12, 0, 32'h99_aa_bb_cc, resp);
  master_agent.AXI4LITE_WRITE_BURST(base_addr + 32'd16, 0, 32'hdd_ee_ff_00, resp);
  master_agent.AXI4LITE_WRITE_BURST(base_addr + 32'd20, 0, 32'h11_22_33_44, resp);
  master_agent.AXI4LITE_WRITE_BURST(base_addr + 32'd24, 0, 32'h55_66_77_88, resp);
  master_agent.AXI4LITE_WRITE_BURST(base_addr + 32'd28, 0, 32'h99_aa_bb_cc, resp);
  master_agent.AXI4LITE_WRITE_BURST(base_addr + 32'd32, 0, 32'hdd_ee_ff_00, resp);
  master_agent.AXI4LITE_WRITE_BURST(base_addr + 32'd36, 0, 32'h11_22_33_44, resp);

#2000
$finish;
end

initial begin 
 forever #10 clk = ~clk;
end


endmodule