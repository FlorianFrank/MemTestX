
################################################################
# This is a generated script based on design: axi_verifier_full
#
# Though there are limitations about the generated script,
# the main purpose of this utility is to make learning
# IP Integrator Tcl commands easier.
################################################################

namespace eval _tcl {
proc get_script_folder {} {
   set script_path [file normalize [info script]]
   set script_folder [file dirname $script_path]
   return $script_folder
}
}
variable script_folder
set script_folder [_tcl::get_script_folder]

################################################################
# Check if script is running in correct Vivado version.
################################################################
set scripts_vivado_version 2022.1
set current_vivado_version [version -short]

if { [string first $scripts_vivado_version $current_vivado_version] == -1 } {
   puts ""
   catch {common::send_gid_msg -ssname BD::TCL -id 2041 -severity "ERROR" "This script was generated using Vivado <$scripts_vivado_version> and is being run in <$current_vivado_version> of Vivado. Please run the script in Vivado <$scripts_vivado_version> then open the design in Vivado <$current_vivado_version>. Upgrade the design by running \"Tools => Report => Report IP Status...\", then run write_bd_tcl to create an updated script."}

   return 1
}

################################################################
# START
################################################################

# To test this script, run the following commands from Vivado Tcl console:
# source axi_verifier_full_script.tcl


# The design that will be created by this Tcl script contains the following 
# module references:
# memory_read_top_module, memory_write_top_module, multiplexer, puf_execution_controller

# Please add the sources of those modules before sourcing this Tcl script.

# If there is no project opened, this script will create a
# project, but make sure you do not have an existing project
# <./myproj/project_1.xpr> in the current working folder.

set list_projs [get_projects -quiet]
if { $list_projs eq "" } {
   create_project project_1 myproj -part xczu9eg-ffvb1156-2-e
   set_property BOARD_PART xilinx.com:zcu102:part0:3.4 [current_project]
}


# CHANGE DESIGN NAME HERE
variable design_name
set design_name axi_verifier_full

# If you do not already have an existing IP Integrator design open,
# you can create a design using the following command:
#    create_bd_design $design_name

# Creating design if needed
set errMsg ""
set nRet 0

set cur_design [current_bd_design -quiet]
set list_cells [get_bd_cells -quiet]

if { ${design_name} eq "" } {
   # USE CASES:
   #    1) Design_name not set

   set errMsg "Please set the variable <design_name> to a non-empty value."
   set nRet 1

} elseif { ${cur_design} ne "" && ${list_cells} eq "" } {
   # USE CASES:
   #    2): Current design opened AND is empty AND names same.
   #    3): Current design opened AND is empty AND names diff; design_name NOT in project.
   #    4): Current design opened AND is empty AND names diff; design_name exists in project.

   if { $cur_design ne $design_name } {
      common::send_gid_msg -ssname BD::TCL -id 2001 -severity "INFO" "Changing value of <design_name> from <$design_name> to <$cur_design> since current design is empty."
      set design_name [get_property NAME $cur_design]
   }
   common::send_gid_msg -ssname BD::TCL -id 2002 -severity "INFO" "Constructing design in IPI design <$cur_design>..."

} elseif { ${cur_design} ne "" && $list_cells ne "" && $cur_design eq $design_name } {
   # USE CASES:
   #    5) Current design opened AND has components AND same names.

   set errMsg "Design <$design_name> already exists in your project, please set the variable <design_name> to another value."
   set nRet 1
} elseif { [get_files -quiet ${design_name}.bd] ne "" } {
   # USE CASES: 
   #    6) Current opened design, has components, but diff names, design_name exists in project.
   #    7) No opened design, design_name exists in project.

   set errMsg "Design <$design_name> already exists in your project, please set the variable <design_name> to another value."
   set nRet 2

} else {
   # USE CASES:
   #    8) No opened design, design_name not in project.
   #    9) Current opened design, has components, but diff names, design_name not in project.

   common::send_gid_msg -ssname BD::TCL -id 2003 -severity "INFO" "Currently there is no design <$design_name> in project, so creating one..."

   create_bd_design $design_name

   common::send_gid_msg -ssname BD::TCL -id 2004 -severity "INFO" "Making design <$design_name> as current_bd_design."
   current_bd_design $design_name

}

common::send_gid_msg -ssname BD::TCL -id 2005 -severity "INFO" "Currently the variable <design_name> is equal to \"$design_name\"."

if { $nRet != 0 } {
   catch {common::send_gid_msg -ssname BD::TCL -id 2006 -severity "ERROR" $errMsg}
   return $nRet
}

set bCheckIPsPassed 1
##################################################################
# CHECK IPs
##################################################################
set bCheckIPs 1
if { $bCheckIPs == 1 } {
   set list_check_ips "\ 
xilinx.com:ip:smartconnect:1.0\
xilinx.com:ip:axi_vip:1.1\
xilinx.com:ip:clk_wiz:6.0\
seceng.fim.uni-passau.de:seceng.fim.uni-passau.de:ps_pl_interface:1.0\
xilinx.com:ip:util_ds_buf:2.2\
"

   set list_ips_missing ""
   common::send_gid_msg -ssname BD::TCL -id 2011 -severity "INFO" "Checking if the following IPs exist in the project's IP catalog: $list_check_ips ."

   foreach ip_vlnv $list_check_ips {
      set ip_obj [get_ipdefs -all $ip_vlnv]
      if { $ip_obj eq "" } {
         lappend list_ips_missing $ip_vlnv
      }
   }

   if { $list_ips_missing ne "" } {
      catch {common::send_gid_msg -ssname BD::TCL -id 2012 -severity "ERROR" "The following IPs are not found in the IP Catalog:\n  $list_ips_missing\n\nResolution: Please add the repository containing the IP(s) to the project." }
      set bCheckIPsPassed 0
   }

}

##################################################################
# CHECK Modules
##################################################################
set bCheckModules 1
if { $bCheckModules == 1 } {
   set list_check_mods "\ 
memory_read_top_module\
memory_write_top_module\
multiplexer\
puf_execution_controller\
"

   set list_mods_missing ""
   common::send_gid_msg -ssname BD::TCL -id 2020 -severity "INFO" "Checking if the following modules exist in the project's sources: $list_check_mods ."

   foreach mod_vlnv $list_check_mods {
      if { [can_resolve_reference $mod_vlnv] == 0 } {
         lappend list_mods_missing $mod_vlnv
      }
   }

   if { $list_mods_missing ne "" } {
      catch {common::send_gid_msg -ssname BD::TCL -id 2021 -severity "ERROR" "The following module(s) are not found in the project: $list_mods_missing" }
      common::send_gid_msg -ssname BD::TCL -id 2022 -severity "INFO" "Please add source files for the missing module(s) above."
      set bCheckIPsPassed 0
   }
}

if { $bCheckIPsPassed != 1 } {
  common::send_gid_msg -ssname BD::TCL -id 2023 -severity "WARNING" "Will not continue with creation of design due to the error(s) above."
  return 3
}

##################################################################
# DESIGN PROCs
##################################################################



# Procedure to create entire design; Provide argument to make
# procedure reusable. If parentCell is "", will use root.
proc create_root_design { parentCell } {

  variable script_folder
  variable design_name

  if { $parentCell eq "" } {
     set parentCell [get_bd_cells /]
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2090 -severity "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2091 -severity "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj


  # Create interface ports

  # Create ports
  set address_read [ create_bd_port -dir O -from 14 -to 0 address_read ]
  set address_write [ create_bd_port -dir O -from 14 -to 0 address_write ]
  set alines [ create_bd_port -dir O -from 14 -to 0 alines ]
  set alines_write [ create_bd_port -dir O -from 14 -to 0 alines_write ]
  set aresetn [ create_bd_port -dir I -type rst aresetn ]
  set_property -dict [ list \
   CONFIG.POLARITY {ACTIVE_LOW} \
 ] $aresetn
  set axi_light_master_txn_done [ create_bd_port -dir O axi_light_master_txn_done ]
  set axi_test_wire [ create_bd_port -dir I axi_test_wire ]
  set ce [ create_bd_port -dir O ce ]
  set ceDrivenRead [ create_bd_port -dir O ceDrivenRead ]
  set ce_driven [ create_bd_port -dir O ce_driven ]
  set clk [ create_bd_port -dir I -type clk clk ]
  set_property -dict [ list \
   CONFIG.ASSOCIATED_RESET {aresetn} \
 ] $clk
  set cmd [ create_bd_port -dir O -from 7 -to 0 cmd ]
  set cmd_ready [ create_bd_port -dir O cmd_ready ]
  set disable_axi_switch [ create_bd_port -dir I disable_axi_switch ]
  set dlines [ create_bd_port -dir IO -from 7 -to 0 dlines ]
  set full_frame [ create_bd_port -dir O -from 639 -to 0 full_frame ]
  set hammeringDistance [ create_bd_port -dir O -from 15 -to 0 hammeringDistance ]
  set hammeringIterations [ create_bd_port -dir O -from 15 -to 0 hammeringIterations ]
  set init_value [ create_bd_port -dir O -from 15 -to 0 init_value ]
  set locked [ create_bd_port -dir O locked ]
  set oe [ create_bd_port -dir O oe ]
  set outer_state [ create_bd_port -dir O -from 3 -to 0 outer_state ]
  set puf_type [ create_bd_port -dir O -from 7 -to 0 puf_type ]
  set reset [ create_bd_port -dir I -type rst reset ]
  set_property -dict [ list \
   CONFIG.POLARITY {ACTIVE_HIGH} \
 ] $reset
  set rw_select [ create_bd_port -dir O rw_select ]
  set simulate_test_button [ create_bd_port -dir I simulate_test_button ]
  set sram_state [ create_bd_port -dir O -from 3 -to 0 sram_state ]
  set start_addr [ create_bd_port -dir O -from 31 -to 0 start_addr ]
  set start_read_dbg_out [ create_bd_port -dir O start_read_dbg_out ]
  set stop_addr [ create_bd_port -dir O -from 31 -to 0 stop_addr ]
  set tACAdjusted [ create_bd_port -dir O -from 15 -to 0 tACAdjusted ]
  set tACDefault [ create_bd_port -dir O -from 15 -to 0 tACDefault ]
  set tAHAdjusted [ create_bd_port -dir O -from 15 -to 0 tAHAdjusted ]
  set tAHDefault [ create_bd_port -dir O -from 15 -to 0 tAHDefault ]
  set tASAdjusted [ create_bd_port -dir O -from 15 -to 0 tASAdjusted ]
  set tASDefault [ create_bd_port -dir O -from 15 -to 0 tASDefault ]
  set tDHAdjusted [ create_bd_port -dir O -from 15 -to 0 tDHAdjusted ]
  set tDHDefault [ create_bd_port -dir O -from 15 -to 0 tDHDefault ]
  set tDSAdjusted [ create_bd_port -dir O -from 15 -to 0 tDSAdjusted ]
  set tDSDefault [ create_bd_port -dir O -from 15 -to 0 tDSDefault ]
  set tNextRead [ create_bd_port -dir O -from 15 -to 0 tNextRead ]
  set tNextWriteAdjusted [ create_bd_port -dir O -from 15 -to 0 tNextWriteAdjusted ]
  set tPWDAdjusted [ create_bd_port -dir O -from 15 -to 0 tPWDAdjusted ]
  set tPWDDefault [ create_bd_port -dir O -from 15 -to 0 tPWDDefault ]
  set tStartAdjusted [ create_bd_port -dir O -from 15 -to 0 tStartAdjusted ]
  set tStartDefault [ create_bd_port -dir O -from 15 -to 0 tStartDefault ]
  set tStartReadAdjusted [ create_bd_port -dir O -from 15 -to 0 tStartReadAdjusted ]
  set tStartReadDefault [ create_bd_port -dir O -from 15 -to 0 tStartReadDefault ]
  set tWaitAfterInit [ create_bd_port -dir O -from 15 -to 0 tWaitAfterInit ]
  set tWaitBetweenHammering [ create_bd_port -dir O -from 15 -to 0 tWaitBetweenHammering ]
  set tasReadAdjusted [ create_bd_port -dir O -from 15 -to 0 tasReadAdjusted ]
  set tasReadDefault [ create_bd_port -dir O -from 15 -to 0 tasReadDefault ]
  set tceoeDisableAdjusted [ create_bd_port -dir O -from 15 -to 0 tceoeDisableAdjusted ]
  set tceoeDisableDefault [ create_bd_port -dir O -from 15 -to 0 tceoeDisableDefault ]
  set tceoeEnableAdjusted [ create_bd_port -dir O -from 15 -to 0 tceoeEnableAdjusted ]
  set tceoeEnableDefault [ create_bd_port -dir O -from 15 -to 0 tceoeEnableDefault ]
  set test_value [ create_bd_port -dir O -from 15 -to 0 test_value ]
  set tnextWriteDefault [ create_bd_port -dir O -from 15 -to 0 tnextWriteDefault ]
  set toedAdjusted [ create_bd_port -dir O -from 15 -to 0 toedAdjusted ]
  set toedDefault [ create_bd_port -dir O -from 15 -to 0 toedDefault ]
  set tprcAdjusted [ create_bd_port -dir O -from 15 -to 0 tprcAdjusted ]
  set tprcDefault [ create_bd_port -dir O -from 15 -to 0 tprcDefault ]
  set trigger_axi_master_start [ create_bd_port -dir O trigger_axi_master_start ]
  set we [ create_bd_port -dir O we ]

  # Create instance: axi_smc, and set properties
  set axi_smc [ create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect:1.0 axi_smc ]
  set_property -dict [ list \
   CONFIG.NUM_SI {1} \
 ] $axi_smc

  # Create instance: axi_vip_0, and set properties
  set axi_vip_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_vip:1.1 axi_vip_0 ]
  set_property -dict [ list \
   CONFIG.ADDR_WIDTH {32} \
   CONFIG.ARUSER_WIDTH {0} \
   CONFIG.AWUSER_WIDTH {0} \
   CONFIG.BUSER_WIDTH {0} \
   CONFIG.DATA_WIDTH {32} \
   CONFIG.HAS_BRESP {1} \
   CONFIG.HAS_BURST {0} \
   CONFIG.HAS_CACHE {0} \
   CONFIG.HAS_LOCK {0} \
   CONFIG.HAS_PROT {1} \
   CONFIG.HAS_QOS {0} \
   CONFIG.HAS_REGION {0} \
   CONFIG.HAS_RRESP {1} \
   CONFIG.HAS_WSTRB {1} \
   CONFIG.ID_WIDTH {0} \
   CONFIG.INTERFACE_MODE {MASTER} \
   CONFIG.PROTOCOL {AXI4LITE} \
   CONFIG.READ_WRITE_MODE {READ_WRITE} \
   CONFIG.RUSER_BITS_PER_BYTE {0} \
   CONFIG.RUSER_WIDTH {0} \
   CONFIG.SUPPORTS_NARROW {0} \
   CONFIG.WUSER_BITS_PER_BYTE {0} \
   CONFIG.WUSER_WIDTH {0} \
 ] $axi_vip_0

  # Create instance: axi_vip_1, and set properties
  set axi_vip_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_vip:1.1 axi_vip_1 ]
  set_property -dict [ list \
   CONFIG.INTERFACE_MODE {SLAVE} \
 ] $axi_vip_1

  # Create instance: clk_wiz_0, and set properties
  set clk_wiz_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wiz:6.0 clk_wiz_0 ]
  set_property -dict [ list \
   CONFIG.CLKIN1_JITTER_PS {100.0} \
   CONFIG.CLKIN2_JITTER_PS {100.0} \
   CONFIG.CLKOUT1_JITTER {90.074} \
   CONFIG.CLKOUT1_PHASE_ERROR {87.180} \
   CONFIG.CLKOUT1_REQUESTED_OUT_FREQ {400} \
   CONFIG.CLKOUT2_JITTER {115.831} \
   CONFIG.CLKOUT2_PHASE_ERROR {87.180} \
   CONFIG.CLKOUT2_USED {true} \
   CONFIG.MMCM_CLKIN1_PERIOD {10.000} \
   CONFIG.MMCM_CLKIN2_PERIOD {10.000} \
   CONFIG.MMCM_CLKOUT0_DIVIDE_F {3.000} \
   CONFIG.MMCM_CLKOUT1_DIVIDE {12} \
   CONFIG.NUM_OUT_CLKS {2} \
   CONFIG.OPTIMIZE_CLOCKING_STRUCTURE_EN {true} \
   CONFIG.PRIM_IN_FREQ {100} \
   CONFIG.PRIM_SOURCE {Single_ended_clock_capable_pin} \
   CONFIG.RESET_BOARD_INTERFACE {reset} \
   CONFIG.SECONDARY_SOURCE {Single_ended_clock_capable_pin} \
   CONFIG.USE_BOARD_FLOW {true} \
   CONFIG.USE_INCLK_SWITCHOVER {false} \
 ] $clk_wiz_0

  # Create instance: memory_read_top_modu_0, and set properties
  set block_name memory_read_top_module
  set block_cell_name memory_read_top_modu_0
  if { [catch {set memory_read_top_modu_0 [create_bd_cell -type module -reference $block_name $block_cell_name] } errmsg] } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2095 -severity "ERROR" "Unable to add referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   } elseif { $memory_read_top_modu_0 eq "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2096 -severity "ERROR" "Unable to referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   }
    set_property -dict [ list \
   CONFIG.DATA_BUS_SIZE {8} \
   CONFIG.DATA_BUS_SIZE_OUT {8} \
   CONFIG.FREQ_CLK2 {400} \
 ] $memory_read_top_modu_0

  # Create instance: memory_write_top_mod_0, and set properties
  set block_name memory_write_top_module
  set block_cell_name memory_write_top_mod_0
  if { [catch {set memory_write_top_mod_0 [create_bd_cell -type module -reference $block_name $block_cell_name] } errmsg] } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2095 -severity "ERROR" "Unable to add referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   } elseif { $memory_write_top_mod_0 eq "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2096 -severity "ERROR" "Unable to referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   }
    set_property -dict [ list \
   CONFIG.DATA_BUS_SIZE {8} \
   CONFIG.DATA_BUS_SIZE_OUT {8} \
   CONFIG.FREQ_CLK2 {400} \
 ] $memory_write_top_mod_0

  # Create instance: multiplexer_0, and set properties
  set block_name multiplexer
  set block_cell_name multiplexer_0
  if { [catch {set multiplexer_0 [create_bd_cell -type module -reference $block_name $block_cell_name] } errmsg] } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2095 -severity "ERROR" "Unable to add referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   } elseif { $multiplexer_0 eq "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2096 -severity "ERROR" "Unable to referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   }
  
  # Create instance: ps8_0_axi_periph, and set properties
  set ps8_0_axi_periph [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 ps8_0_axi_periph ]
  set_property -dict [ list \
   CONFIG.NUM_MI {1} \
   CONFIG.NUM_SI {1} \
 ] $ps8_0_axi_periph

  # Create instance: ps_pl_interface_0, and set properties
  set ps_pl_interface_0 [ create_bd_cell -type ip -vlnv seceng.fim.uni-passau.de:seceng.fim.uni-passau.de:ps_pl_interface:1.0 ps_pl_interface_0 ]
  set_property -dict [ list \
   CONFIG.C_AXI_Light_Master_TRANSACTIONS_NUM {4} \
 ] $ps_pl_interface_0

  # Create instance: puf_exection_control_0_upgraded_ipi, and set properties
  set block_name puf_execution_controller
  set block_cell_name puf_exection_control_0_upgraded_ipi
  if { [catch {set puf_exection_control_0_upgraded_ipi [create_bd_cell -type module -reference $block_name $block_cell_name] } errmsg] } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2095 -severity "ERROR" "Unable to add referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   } elseif { $puf_exection_control_0_upgraded_ipi eq "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2096 -severity "ERROR" "Unable to referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   }
  
  # Create instance: util_ds_buf_0, and set properties
  set util_ds_buf_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_ds_buf:2.2 util_ds_buf_0 ]
  set_property -dict [ list \
   CONFIG.C_BUF_TYPE {IOBUF} \
   CONFIG.C_SIZE {8} \
 ] $util_ds_buf_0

  # Create interface connections
  connect_bd_intf_net -intf_net S00_AXI_1 [get_bd_intf_pins axi_vip_0/M_AXI] [get_bd_intf_pins ps8_0_axi_periph/S00_AXI]
  connect_bd_intf_net -intf_net axi_smc_M00_AXI [get_bd_intf_pins axi_smc/M00_AXI] [get_bd_intf_pins axi_vip_1/S_AXI]
  connect_bd_intf_net -intf_net ps8_0_axi_periph_M00_AXI [get_bd_intf_pins ps8_0_axi_periph/M00_AXI] [get_bd_intf_pins ps_pl_interface_0/AXI_Light_Slave]
  connect_bd_intf_net -intf_net ps_pl_interface_0_AXI_Light_Master [get_bd_intf_pins axi_smc/S00_AXI] [get_bd_intf_pins ps_pl_interface_0/AXI_Light_Master]

  # Create port connections
  connect_bd_net -net Net [get_bd_ports dlines] [get_bd_pins util_ds_buf_0/IOBUF_IO_IO]
  connect_bd_net -net Net1 [get_bd_ports rw_select] [get_bd_pins multiplexer_0/rw_select_in] [get_bd_pins puf_exection_control_0_upgraded_ipi/rw_select] [get_bd_pins util_ds_buf_0/IOBUF_IO_T]
  connect_bd_net -net axi_test_wire_1 [get_bd_ports axi_test_wire]
  connect_bd_net -net clk_wiz_0_clk_out1 [get_bd_pins clk_wiz_0/clk_out1] [get_bd_pins memory_read_top_modu_0/clk2] [get_bd_pins memory_write_top_mod_0/clk] 
  connect_bd_net -net clk_wiz_0_clk_out2 [get_bd_ports clk] [get_bd_pins axi_smc/aclk] [get_bd_pins axi_vip_0/aclk] [get_bd_pins axi_vip_1/aclk] [get_bd_pins clk_wiz_0/clk_in1] [get_bd_pins memory_read_top_modu_0/clk1] [get_bd_pins ps8_0_axi_periph/ACLK] [get_bd_pins ps8_0_axi_periph/M00_ACLK] [get_bd_pins ps8_0_axi_periph/S00_ACLK] [get_bd_pins ps_pl_interface_0/axi_light_master_aclk] [get_bd_pins ps_pl_interface_0/axi_light_slave_aclk] [get_bd_pins puf_exection_control_0_upgraded_ipi/clk]
  connect_bd_net -net clk_wiz_0_locked [get_bd_ports locked] [get_bd_pins clk_wiz_0/locked] [get_bd_pins puf_exection_control_0_upgraded_ipi/locked]
  connect_bd_net -net disable_axi_switch_0_1 [get_bd_ports disable_axi_switch] [get_bd_pins puf_exection_control_0_upgraded_ipi/disable_axi_switch]
  connect_bd_net -net memory_read_top_modu_0_alines [get_bd_pins memory_read_top_modu_0/alines] [get_bd_pins multiplexer_0/alines_read]
  connect_bd_net -net memory_read_top_modu_0_ce [get_bd_pins memory_read_top_modu_0/ce] [get_bd_pins multiplexer_0/ce_read]
  connect_bd_net -net memory_read_top_modu_0_oe [get_bd_pins memory_read_top_modu_0/oe] [get_bd_pins multiplexer_0/oe_read]
  connect_bd_net -net memory_read_top_modu_0_outer_state [get_bd_ports outer_state] [get_bd_pins memory_read_top_modu_0/outer_state]
  connect_bd_net -net memory_read_top_modu_0_ready [get_bd_pins memory_read_top_modu_0/ready] [get_bd_pins puf_exection_control_0_upgraded_ipi/read_done]
  connect_bd_net -net memory_read_top_modu_0_sram_state [get_bd_ports sram_state] [get_bd_pins memory_read_top_modu_0/sram_state]
  connect_bd_net -net memory_read_top_modu_0_start_read_dbg_out [get_bd_ports start_read_dbg_out] [get_bd_pins memory_read_top_modu_0/start_read_dbg_out]
  connect_bd_net -net memory_read_top_modu_0_value [get_bd_pins memory_read_top_modu_0/value] [get_bd_pins puf_exection_control_0_upgraded_ipi/data_in]
  connect_bd_net -net memory_read_top_modu_0_we [get_bd_pins memory_read_top_modu_0/we] [get_bd_pins multiplexer_0/we_read]
  connect_bd_net -net memory_write_top_mod_0_active [get_bd_pins memory_write_top_mod_0/write_active] [get_bd_pins puf_exection_control_0_upgraded_ipi/write_active]
  connect_bd_net -net memory_write_top_mod_0_alines [get_bd_ports alines_write] [get_bd_pins memory_write_top_mod_0/alines] [get_bd_pins multiplexer_0/alines_write]
  connect_bd_net -net memory_write_top_mod_0_ce [get_bd_pins memory_write_top_mod_0/ce] [get_bd_pins multiplexer_0/ce_write]
  connect_bd_net -net memory_write_top_mod_0_dlines [get_bd_pins memory_write_top_mod_0/dlines] [get_bd_pins util_ds_buf_0/IOBUF_IO_I]
  connect_bd_net -net memory_write_top_mod_0_oe [get_bd_pins memory_write_top_mod_0/oe] [get_bd_pins multiplexer_0/oe_write]
  connect_bd_net -net memory_write_top_mod_0_ready [get_bd_pins memory_write_top_mod_0/write_done] [get_bd_pins puf_exection_control_0_upgraded_ipi/write_done]
  connect_bd_net -net memory_write_top_mod_0_we [get_bd_pins memory_write_top_mod_0/we] [get_bd_pins multiplexer_0/we_write]
  connect_bd_net -net multiplexer_0_alines [get_bd_ports alines] [get_bd_pins multiplexer_0/alines]
  connect_bd_net -net multiplexer_0_ce [get_bd_ports ce] [get_bd_pins multiplexer_0/ce]
  connect_bd_net -net multiplexer_0_oe [get_bd_ports oe] [get_bd_pins multiplexer_0/oe]
  connect_bd_net -net multiplexer_0_we [get_bd_ports we] [get_bd_pins multiplexer_0/we]
  connect_bd_net -net ps_pl_interface_0_axi_light_master_txn_done [get_bd_ports axi_light_master_txn_done] [get_bd_pins ps_pl_interface_0/axi_light_master_txn_done] [get_bd_pins puf_exection_control_0_upgraded_ipi/axi_master_done]
  connect_bd_net -net ps_pl_interface_0_ceDrivenRead [get_bd_ports ceDrivenRead] [get_bd_pins ps_pl_interface_0/ceDrivenRead] [get_bd_pins puf_exection_control_0_upgraded_ipi/ceDrivenReadIn]
  connect_bd_net -net ps_pl_interface_0_ce_driven [get_bd_ports ce_driven] [get_bd_pins ps_pl_interface_0/ce_driven] [get_bd_pins puf_exection_control_0_upgraded_ipi/ceDrivenIn]
  connect_bd_net -net ps_pl_interface_0_cmd [get_bd_ports cmd] [get_bd_pins ps_pl_interface_0/cmd]
  connect_bd_net -net ps_pl_interface_0_cmd_ready [get_bd_ports cmd_ready] [get_bd_pins ps_pl_interface_0/cmd_ready] [get_bd_pins puf_exection_control_0_upgraded_ipi/axi_active]
  connect_bd_net -net ps_pl_interface_0_full_frame [get_bd_ports full_frame] [get_bd_pins ps_pl_interface_0/full_frame]
  connect_bd_net -net ps_pl_interface_0_hammeringDistance [get_bd_ports hammeringDistance] [get_bd_pins ps_pl_interface_0/hammeringDistance] [get_bd_pins puf_exection_control_0_upgraded_ipi/hammeringDistance]
  connect_bd_net -net ps_pl_interface_0_hammeringIterations [get_bd_ports hammeringIterations] [get_bd_pins ps_pl_interface_0/hammeringIterations] [get_bd_pins puf_exection_control_0_upgraded_ipi/hammeringIterations]
  connect_bd_net -net ps_pl_interface_0_init_value [get_bd_ports init_value] [get_bd_pins ps_pl_interface_0/init_value] [get_bd_pins puf_exection_control_0_upgraded_ipi/init_value]
  connect_bd_net -net ps_pl_interface_0_puf_type [get_bd_ports puf_type] [get_bd_pins ps_pl_interface_0/puf_type] [get_bd_pins puf_exection_control_0_upgraded_ipi/puf_type]
  connect_bd_net -net ps_pl_interface_0_start_addr [get_bd_ports start_addr] [get_bd_pins ps_pl_interface_0/start_addr] [get_bd_pins puf_exection_control_0_upgraded_ipi/start_addr]
  connect_bd_net -net ps_pl_interface_0_stop_addr [get_bd_ports stop_addr] [get_bd_pins ps_pl_interface_0/stop_addr] [get_bd_pins puf_exection_control_0_upgraded_ipi/end_addr]
  connect_bd_net -net ps_pl_interface_0_tACAdjusted [get_bd_ports tACAdjusted] [get_bd_pins ps_pl_interface_0/tACAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tACAdjustedIn]
  connect_bd_net -net ps_pl_interface_0_tACDefault [get_bd_ports tACDefault] [get_bd_pins ps_pl_interface_0/tACDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tACDefaultIn]
  connect_bd_net -net ps_pl_interface_0_tAHAdjusted [get_bd_ports tAHAdjusted] [get_bd_pins ps_pl_interface_0/tAHAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tAHAdjustedIn]
  connect_bd_net -net ps_pl_interface_0_tAHDefault [get_bd_ports tAHDefault] [get_bd_pins ps_pl_interface_0/tAHDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tAHDefaultIn]
  connect_bd_net -net ps_pl_interface_0_tASAdjusted [get_bd_ports tASAdjusted] [get_bd_pins ps_pl_interface_0/tASAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tASAdjustedIn]
  connect_bd_net -net ps_pl_interface_0_tASDefault [get_bd_ports tASDefault] [get_bd_pins ps_pl_interface_0/tASDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tASDefaultIn]
  connect_bd_net -net ps_pl_interface_0_tDHAdjusted [get_bd_ports tDHAdjusted] [get_bd_pins ps_pl_interface_0/tDHAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tDHAdjustedIn]
  connect_bd_net -net ps_pl_interface_0_tDHDefault [get_bd_ports tDHDefault] [get_bd_pins ps_pl_interface_0/tDHDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tDHDefaultIn]
  connect_bd_net -net ps_pl_interface_0_tDSAdjusted [get_bd_ports tDSAdjusted] [get_bd_pins ps_pl_interface_0/tDSAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tDSAdjustedIn]
  connect_bd_net -net ps_pl_interface_0_tDSDefault [get_bd_ports tDSDefault] [get_bd_pins ps_pl_interface_0/tDSDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tDSDefaultIn]
  connect_bd_net -net ps_pl_interface_0_tNextRead [get_bd_ports tNextRead] [get_bd_pins ps_pl_interface_0/tNextRead] [get_bd_pins puf_exection_control_0_upgraded_ipi/tNextRead]
  connect_bd_net -net ps_pl_interface_0_tPWDAdjusted [get_bd_ports tPWDAdjusted] [get_bd_pins ps_pl_interface_0/tPWDAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tPWDAdjustedIn]
  connect_bd_net -net ps_pl_interface_0_tPWDDefault [get_bd_ports tPWDDefault] [get_bd_pins ps_pl_interface_0/tPWDDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tPWDDefaultIn]
  connect_bd_net -net ps_pl_interface_0_tStartAdjusted [get_bd_ports tStartAdjusted] [get_bd_pins ps_pl_interface_0/tStartAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tStartAdjustedIn]
  connect_bd_net -net ps_pl_interface_0_tStartDefault [get_bd_ports tStartDefault] [get_bd_pins ps_pl_interface_0/tStartDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tStartDefaultIn]
  connect_bd_net -net ps_pl_interface_0_tStartReadAdjusted [get_bd_ports tStartReadAdjusted] [get_bd_pins ps_pl_interface_0/tStartReadAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tStartReadAdjusted]
  connect_bd_net -net ps_pl_interface_0_tStartReadDefault [get_bd_ports tStartReadDefault] [get_bd_pins ps_pl_interface_0/tStartReadDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tStartReadDefault]
  connect_bd_net -net ps_pl_interface_0_tWaitBetweenHammering [get_bd_ports tWaitBetweenHammering] [get_bd_pins ps_pl_interface_0/tWaitBetweenHammering] [get_bd_pins puf_exection_control_0_upgraded_ipi/tWaitBetweenHammering]
  connect_bd_net -net ps_pl_interface_0_tasReadAdjusted [get_bd_ports tasReadAdjusted] [get_bd_pins ps_pl_interface_0/tasReadAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tasReadAdjusted]
  connect_bd_net -net ps_pl_interface_0_tasReadDefault [get_bd_ports tasReadDefault] [get_bd_pins ps_pl_interface_0/tasReadDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tasReadDefault]
  connect_bd_net -net ps_pl_interface_0_tceoeDisableAdjusted [get_bd_ports tceoeDisableAdjusted] [get_bd_pins ps_pl_interface_0/tceoeDisableAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tceoeDisableAdjusted]
  connect_bd_net -net ps_pl_interface_0_tceoeDisableDefault [get_bd_ports tceoeDisableDefault] [get_bd_pins ps_pl_interface_0/tceoeDisableDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tceoeDisableDefault]
  connect_bd_net -net ps_pl_interface_0_tceoeEnableAdjusted [get_bd_ports tceoeEnableAdjusted] [get_bd_pins ps_pl_interface_0/tceoeEnableAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tceoeEnableAdjusted]
  connect_bd_net -net ps_pl_interface_0_tceoeEnableDefault [get_bd_ports tceoeEnableDefault] [get_bd_pins ps_pl_interface_0/tceoeEnableDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tceoeEnableDefault]
  connect_bd_net -net ps_pl_interface_0_test_value [get_bd_ports test_value] [get_bd_pins ps_pl_interface_0/test_value] [get_bd_pins puf_exection_control_0_upgraded_ipi/test_value]
  connect_bd_net -net ps_pl_interface_0_tnextWriteAdjusted [get_bd_ports tNextWriteAdjusted] [get_bd_pins ps_pl_interface_0/tNextWriteAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tnextWriteAdjustedIn]
  connect_bd_net -net ps_pl_interface_0_tnextWriteDefault [get_bd_ports tnextWriteDefault] [get_bd_pins ps_pl_interface_0/tnextWriteDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tnextWriteDefaultIn]
  connect_bd_net -net ps_pl_interface_0_toedAdjusted [get_bd_ports toedAdjusted] [get_bd_pins ps_pl_interface_0/toedAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/toedAdjusted]
  connect_bd_net -net ps_pl_interface_0_toedDefault [get_bd_ports toedDefault] [get_bd_pins ps_pl_interface_0/toedDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/toedDefault]
  connect_bd_net -net ps_pl_interface_0_tprcAdjusted [get_bd_ports tprcAdjusted] [get_bd_pins ps_pl_interface_0/tprcAdjusted] [get_bd_pins puf_exection_control_0_upgraded_ipi/tprcAdjusted]
  connect_bd_net -net ps_pl_interface_0_tprcDefault [get_bd_ports tprcDefault] [get_bd_pins ps_pl_interface_0/tprcDefault] [get_bd_pins puf_exection_control_0_upgraded_ipi/tprcDefault]
  connect_bd_net -net ps_pl_interface_0_twaitAfterInit [get_bd_ports tWaitAfterInit] [get_bd_pins ps_pl_interface_0/tWaitAfterInit] [get_bd_pins puf_exection_control_0_upgraded_ipi/tWaitAfterInit]
  connect_bd_net -net ps_pl_trigger_0_output_data [get_bd_pins ps_pl_interface_0/input_data] [get_bd_pins puf_exection_control_0_upgraded_ipi/output_data]
  connect_bd_net -net ps_pl_trigger_0_value_to_write [get_bd_pins ps_pl_interface_0/input_address] [get_bd_pins puf_exection_control_0_upgraded_ipi/output_address]
  connect_bd_net -net puf_exection_control_0_address_read [get_bd_ports address_read] [get_bd_pins memory_read_top_modu_0/address] [get_bd_pins puf_exection_control_0_upgraded_ipi/address_read]
  connect_bd_net -net puf_exection_control_0_address_write [get_bd_ports address_write] [get_bd_pins memory_write_top_mod_0/address_write] [get_bd_pins puf_exection_control_0_upgraded_ipi/address_write]
  connect_bd_net -net puf_exection_control_0_ceDriven [get_bd_pins memory_write_top_mod_0/ceDriven] [get_bd_pins puf_exection_control_0_upgraded_ipi/ceDriven]
  connect_bd_net -net puf_exection_control_0_max_address [get_bd_pins memory_write_top_mod_0/max_address] [get_bd_pins puf_exection_control_0_upgraded_ipi/max_address]
  connect_bd_net -net puf_exection_control_0_start_read [get_bd_pins memory_read_top_modu_0/start] [get_bd_pins puf_exection_control_0_upgraded_ipi/start_read]
  connect_bd_net -net puf_exection_control_0_tStart [get_bd_pins memory_write_top_mod_0/tStart] [get_bd_pins puf_exection_control_0_upgraded_ipi/tStart]
  connect_bd_net -net puf_exection_control_0_tac [get_bd_pins memory_write_top_mod_0/tac] [get_bd_pins puf_exection_control_0_upgraded_ipi/tac]
  connect_bd_net -net puf_exection_control_0_tah [get_bd_pins memory_write_top_mod_0/tah] [get_bd_pins puf_exection_control_0_upgraded_ipi/tah]
  connect_bd_net -net puf_exection_control_0_tas [get_bd_pins memory_write_top_mod_0/tas] [get_bd_pins puf_exection_control_0_upgraded_ipi/tas]
  connect_bd_net -net puf_exection_control_0_tdh [get_bd_pins memory_write_top_mod_0/tdh] [get_bd_pins puf_exection_control_0_upgraded_ipi/tdh]
  connect_bd_net -net puf_exection_control_0_tds [get_bd_pins memory_write_top_mod_0/tds] [get_bd_pins puf_exection_control_0_upgraded_ipi/tds]
  connect_bd_net -net puf_exection_control_0_tnext [get_bd_pins memory_write_top_mod_0/tnext] [get_bd_pins puf_exection_control_0_upgraded_ipi/tnext]
  connect_bd_net -net puf_exection_control_0_tpwd [get_bd_pins memory_write_top_mod_0/tpwd] [get_bd_pins puf_exection_control_0_upgraded_ipi/tpwd]
  connect_bd_net -net puf_exection_control_0_trigger_axi_master_start [get_bd_ports trigger_axi_master_start] [get_bd_pins ps_pl_interface_0/axi_light_master_init_axi_txn] [get_bd_pins puf_exection_control_0_upgraded_ipi/trigger_axi_master_start]
  connect_bd_net -net puf_exection_control_0_upgraded_ipi_ceDrivenRead [get_bd_pins memory_read_top_modu_0/ceDriven] [get_bd_pins puf_exection_control_0_upgraded_ipi/ceDrivenRead]
  connect_bd_net -net puf_exection_control_0_upgraded_ipi_tStartRead [get_bd_pins memory_read_top_modu_0/tStart] [get_bd_pins puf_exection_control_0_upgraded_ipi/tStartRead]
  connect_bd_net -net puf_exection_control_0_upgraded_ipi_tasRead [get_bd_pins memory_read_top_modu_0/tas] [get_bd_pins puf_exection_control_0_upgraded_ipi/tasRead]
  connect_bd_net -net puf_exection_control_0_upgraded_ipi_tceoeDisable [get_bd_pins memory_read_top_modu_0/tceoeDisable] [get_bd_pins puf_exection_control_0_upgraded_ipi/tceoeDisable]
  connect_bd_net -net puf_exection_control_0_upgraded_ipi_tceoeEnable [get_bd_pins memory_read_top_modu_0/tceoeEnable] [get_bd_pins puf_exection_control_0_upgraded_ipi/tceoeEnable]
  connect_bd_net -net puf_exection_control_0_upgraded_ipi_toed [get_bd_pins memory_read_top_modu_0/toed] [get_bd_pins puf_exection_control_0_upgraded_ipi/toed]
  connect_bd_net -net puf_exection_control_0_upgraded_ipi_tprc [get_bd_pins memory_read_top_modu_0/tprc] [get_bd_pins puf_exection_control_0_upgraded_ipi/tprc]
  connect_bd_net -net puf_exection_control_0_value_write [get_bd_pins memory_write_top_mod_0/value_write] [get_bd_pins puf_exection_control_0_upgraded_ipi/value_write]
  connect_bd_net -net puf_exection_control_0_write_continously [get_bd_pins memory_write_top_mod_0/write_continously] [get_bd_pins puf_exection_control_0_upgraded_ipi/write_continously]
  connect_bd_net -net reset_1 [get_bd_ports reset] [get_bd_pins clk_wiz_0/reset]
  connect_bd_net -net rst_ps8_0_96M_peripheral_aresetn [get_bd_ports aresetn] [get_bd_pins axi_smc/aresetn] [get_bd_pins axi_vip_0/aresetn] [get_bd_pins axi_vip_1/aresetn] [get_bd_pins ps8_0_axi_periph/ARESETN] [get_bd_pins ps8_0_axi_periph/M00_ARESETN] [get_bd_pins ps8_0_axi_periph/S00_ARESETN] [get_bd_pins ps_pl_interface_0/axi_light_master_aresetn] [get_bd_pins ps_pl_interface_0/axi_light_slave_aresetn]
  connect_bd_net -net test_switch_0_1 [get_bd_ports simulate_test_button] [get_bd_pins puf_exection_control_0_upgraded_ipi/simulate_test_button]
  connect_bd_net -net util_ds_buf_0_IOBUF_IO_O [get_bd_pins memory_read_top_modu_0/dlines] [get_bd_pins multiplexer_0/dlines_in] [get_bd_pins util_ds_buf_0/IOBUF_IO_O]
  connect_bd_net -net writer_0_start_write [get_bd_pins memory_write_top_mod_0/start_write] [get_bd_pins puf_exection_control_0_upgraded_ipi/start_write]

  # Create address segments
  assign_bd_address -offset 0x40000000 -range 0x00010000 -target_address_space [get_bd_addr_spaces axi_vip_0/Master_AXI] [get_bd_addr_segs ps_pl_interface_0/AXI_Light_Slave/AXI_Light_Slave_reg] -force
  assign_bd_address -offset 0x44A00000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps_pl_interface_0/AXI_Light_Master] [get_bd_addr_segs axi_vip_1/S_AXI/Reg] -force


  # Restore current instance
  current_bd_instance $oldCurInst

  validate_bd_design
  save_bd_design
}
# End of create_root_design()


##################################################################
# MAIN FLOW
##################################################################

create_root_design ""


