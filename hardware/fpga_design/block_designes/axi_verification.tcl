
################################################################
# This is a generated script based on design: axi_verification
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
set scripts_vivado_version 2022.2
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
# source axi_verification_script.tcl

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
set design_name axi_verification

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
xilinx.com:ip:axi_vip:1.1\
seceng.fim.uni-passau.de:seceng.fim.uni-passau.de:ps_pl_interface:1.0\
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
  set areset [ create_bd_port -dir I -type rst areset ]
  set ceDrivenRead [ create_bd_port -dir O ceDrivenRead ]
  set ce_driven [ create_bd_port -dir O ce_driven ]
  set clk [ create_bd_port -dir I -type clk -freq_hz 100000000 clk ]
  set cmd [ create_bd_port -dir O -from 7 -to 0 cmd ]
  set cmd_ready [ create_bd_port -dir O cmd_ready ]
  set full_frame [ create_bd_port -dir O -from 639 -to 0 full_frame ]
  set hammeringDistance [ create_bd_port -dir O -from 15 -to 0 hammeringDistance ]
  set hammeringIterations [ create_bd_port -dir O -from 15 -to 0 hammeringIterations ]
  set init_value [ create_bd_port -dir O -from 15 -to 0 init_value ]
  set puf_type [ create_bd_port -dir O -from 7 -to 0 puf_type ]
  set start_addr [ create_bd_port -dir O -from 31 -to 0 start_addr ]
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
  set tWaitBetweenHammering [ create_bd_port -dir O -from 15 -to 0 tWaitBetweenHammering ]
  set tahReadAdjusted [ create_bd_port -dir O -from 15 -to 0 tahReadAdjusted ]
  set tahReadDefault [ create_bd_port -dir O -from 15 -to 0 tahReadDefault ]
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
  set twaitAfterInit [ create_bd_port -dir O -from 15 -to 0 twaitAfterInit ]
  set write_map_out [ create_bd_port -dir O -from 19 -to 0 write_map_out ]

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

  # Create instance: axi_vip_0_axi_periph, and set properties
  set axi_vip_0_axi_periph [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_vip_0_axi_periph ]
  set_property -dict [ list \
   CONFIG.NUM_MI {1} \
 ] $axi_vip_0_axi_periph

  # Create instance: ps_pl_interface_0, and set properties
  set ps_pl_interface_0 [ create_bd_cell -type ip -vlnv seceng.fim.uni-passau.de:seceng.fim.uni-passau.de:ps_pl_interface:1.0 ps_pl_interface_0 ]

  # Create interface connections
  connect_bd_intf_net -intf_net axi_vip_0_M_AXI [get_bd_intf_pins axi_vip_0/M_AXI] [get_bd_intf_pins axi_vip_0_axi_periph/S00_AXI]
  connect_bd_intf_net -intf_net axi_vip_0_axi_periph_M00_AXI [get_bd_intf_pins axi_vip_0_axi_periph/M00_AXI] [get_bd_intf_pins ps_pl_interface_0/AXI_Light_Slave]

  # Create port connections
  connect_bd_net -net aresetn_0_1 [get_bd_ports areset] [get_bd_pins axi_vip_0/aresetn] [get_bd_pins axi_vip_0_axi_periph/ARESETN] [get_bd_pins axi_vip_0_axi_periph/M00_ARESETN] [get_bd_pins axi_vip_0_axi_periph/S00_ARESETN] [get_bd_pins ps_pl_interface_0/axi_light_master_aresetn] [get_bd_pins ps_pl_interface_0/axi_light_slave_aresetn]
  connect_bd_net -net clk_wiz_clk_out1 [get_bd_ports clk] [get_bd_pins axi_vip_0/aclk] [get_bd_pins axi_vip_0_axi_periph/ACLK] [get_bd_pins axi_vip_0_axi_periph/M00_ACLK] [get_bd_pins axi_vip_0_axi_periph/S00_ACLK] [get_bd_pins ps_pl_interface_0/axi_light_master_aclk] [get_bd_pins ps_pl_interface_0/axi_light_slave_aclk]
  connect_bd_net -net ps_pl_interface_0_ceDrivenRead [get_bd_ports ceDrivenRead] [get_bd_pins ps_pl_interface_0/ceDrivenRead]
  connect_bd_net -net ps_pl_interface_0_ce_driven [get_bd_ports ce_driven] [get_bd_pins ps_pl_interface_0/ce_driven]
  connect_bd_net -net ps_pl_interface_0_cmd [get_bd_ports cmd] [get_bd_pins ps_pl_interface_0/cmd]
  connect_bd_net -net ps_pl_interface_0_cmd_ready [get_bd_ports cmd_ready] [get_bd_pins ps_pl_interface_0/cmd_ready]
  connect_bd_net -net ps_pl_interface_0_full_frame [get_bd_ports full_frame] [get_bd_pins ps_pl_interface_0/full_frame]
  connect_bd_net -net ps_pl_interface_0_hammeringDistance [get_bd_ports hammeringDistance] [get_bd_pins ps_pl_interface_0/hammeringDistance]
  connect_bd_net -net ps_pl_interface_0_hammeringIterations [get_bd_ports hammeringIterations] [get_bd_pins ps_pl_interface_0/hammeringIterations]
  connect_bd_net -net ps_pl_interface_0_init_value [get_bd_ports init_value] [get_bd_pins ps_pl_interface_0/init_value]
  connect_bd_net -net ps_pl_interface_0_puf_type [get_bd_ports puf_type] [get_bd_pins ps_pl_interface_0/puf_type]
  connect_bd_net -net ps_pl_interface_0_start_addr [get_bd_ports start_addr] [get_bd_pins ps_pl_interface_0/start_addr]
  connect_bd_net -net ps_pl_interface_0_stop_addr [get_bd_ports stop_addr] [get_bd_pins ps_pl_interface_0/stop_addr]
  connect_bd_net -net ps_pl_interface_0_tACAdjusted [get_bd_ports tACAdjusted] [get_bd_pins ps_pl_interface_0/tACAdjusted]
  connect_bd_net -net ps_pl_interface_0_tACDefault [get_bd_ports tACDefault] [get_bd_pins ps_pl_interface_0/tACDefault]
  connect_bd_net -net ps_pl_interface_0_tAHAdjusted [get_bd_ports tAHAdjusted] [get_bd_pins ps_pl_interface_0/tAHAdjusted]
  connect_bd_net -net ps_pl_interface_0_tAHDefault [get_bd_ports tAHDefault] [get_bd_pins ps_pl_interface_0/tAHDefault]
  connect_bd_net -net ps_pl_interface_0_tASAdjusted [get_bd_ports tASAdjusted] [get_bd_pins ps_pl_interface_0/tASAdjusted]
  connect_bd_net -net ps_pl_interface_0_tASDefault [get_bd_ports tASDefault] [get_bd_pins ps_pl_interface_0/tASDefault]
  connect_bd_net -net ps_pl_interface_0_tDHAdjusted [get_bd_ports tDHAdjusted] [get_bd_pins ps_pl_interface_0/tDHAdjusted]
  connect_bd_net -net ps_pl_interface_0_tDHDefault [get_bd_ports tDHDefault] [get_bd_pins ps_pl_interface_0/tDHDefault]
  connect_bd_net -net ps_pl_interface_0_tDSAdjusted [get_bd_ports tDSAdjusted] [get_bd_pins ps_pl_interface_0/tDSAdjusted]
  connect_bd_net -net ps_pl_interface_0_tDSDefault [get_bd_ports tDSDefault] [get_bd_pins ps_pl_interface_0/tDSDefault]
  connect_bd_net -net ps_pl_interface_0_tNextRead [get_bd_ports tNextRead] [get_bd_pins ps_pl_interface_0/tNextRead]
  connect_bd_net -net ps_pl_interface_0_tNextWriteAdjusted [get_bd_ports tNextWriteAdjusted] [get_bd_pins ps_pl_interface_0/tNextWriteAdjusted]
  connect_bd_net -net ps_pl_interface_0_tPWDAdjusted [get_bd_ports tPWDAdjusted] [get_bd_pins ps_pl_interface_0/tPWDAdjusted]
  connect_bd_net -net ps_pl_interface_0_tPWDDefault [get_bd_ports tPWDDefault] [get_bd_pins ps_pl_interface_0/tPWDDefault]
  connect_bd_net -net ps_pl_interface_0_tStartAdjusted [get_bd_ports tStartAdjusted] [get_bd_pins ps_pl_interface_0/tStartAdjusted]
  connect_bd_net -net ps_pl_interface_0_tStartDefault [get_bd_ports tStartDefault] [get_bd_pins ps_pl_interface_0/tStartDefault]
  connect_bd_net -net ps_pl_interface_0_tStartReadAdjusted [get_bd_ports tStartReadAdjusted] [get_bd_pins ps_pl_interface_0/tStartReadAdjusted]
  connect_bd_net -net ps_pl_interface_0_tStartReadDefault [get_bd_ports tStartReadDefault] [get_bd_pins ps_pl_interface_0/tStartReadDefault]
  connect_bd_net -net ps_pl_interface_0_tWaitBetweenHammering [get_bd_ports tWaitBetweenHammering] [get_bd_pins ps_pl_interface_0/tWaitBetweenHammering]
  connect_bd_net -net ps_pl_interface_0_tahReadAdjusted [get_bd_ports tahReadAdjusted] [get_bd_pins ps_pl_interface_0/tahReadAdjusted]
  connect_bd_net -net ps_pl_interface_0_tahReadDefault [get_bd_ports tahReadDefault] [get_bd_pins ps_pl_interface_0/tahReadDefault]
  connect_bd_net -net ps_pl_interface_0_tasReadAdjusted [get_bd_ports tasReadAdjusted] [get_bd_pins ps_pl_interface_0/tasReadAdjusted]
  connect_bd_net -net ps_pl_interface_0_tasReadDefault [get_bd_ports tasReadDefault] [get_bd_pins ps_pl_interface_0/tasReadDefault]
  connect_bd_net -net ps_pl_interface_0_tceoeDisableAdjusted [get_bd_ports tceoeDisableAdjusted] [get_bd_pins ps_pl_interface_0/tceoeDisableAdjusted]
  connect_bd_net -net ps_pl_interface_0_tceoeDisableDefault [get_bd_ports tceoeDisableDefault] [get_bd_pins ps_pl_interface_0/tceoeDisableDefault]
  connect_bd_net -net ps_pl_interface_0_tceoeEnableAdjusted [get_bd_ports tceoeEnableAdjusted] [get_bd_pins ps_pl_interface_0/tceoeEnableAdjusted]
  connect_bd_net -net ps_pl_interface_0_tceoeEnableDefault [get_bd_ports tceoeEnableDefault] [get_bd_pins ps_pl_interface_0/tceoeEnableDefault]
  connect_bd_net -net ps_pl_interface_0_test_value [get_bd_ports test_value] [get_bd_pins ps_pl_interface_0/test_value]
  connect_bd_net -net ps_pl_interface_0_tnextWriteDefault [get_bd_ports tnextWriteDefault] [get_bd_pins ps_pl_interface_0/tnextWriteDefault]
  connect_bd_net -net ps_pl_interface_0_toedAdjusted [get_bd_ports toedAdjusted] [get_bd_pins ps_pl_interface_0/toedAdjusted]
  connect_bd_net -net ps_pl_interface_0_toedDefault [get_bd_ports toedDefault] [get_bd_pins ps_pl_interface_0/toedDefault]
  connect_bd_net -net ps_pl_interface_0_tprcAdjusted [get_bd_ports tprcAdjusted] [get_bd_pins ps_pl_interface_0/tprcAdjusted]
  connect_bd_net -net ps_pl_interface_0_tprcDefault [get_bd_ports tprcDefault] [get_bd_pins ps_pl_interface_0/tprcDefault]
  connect_bd_net -net ps_pl_interface_0_twaitAfterInit [get_bd_ports twaitAfterInit] [get_bd_pins ps_pl_interface_0/tWaitAfterInit]
  connect_bd_net -net ps_pl_interface_0_write_map_out [get_bd_ports write_map_out]

  # Create address segments
  assign_bd_address -offset 0x44A00000 -range 0x00010000 -target_address_space [get_bd_addr_spaces axi_vip_0/Master_AXI] [get_bd_addr_segs ps_pl_interface_0/AXI_Light_Slave/AXI_Light_Slave_reg] -force


  # Restore current instance
  current_bd_instance $oldCurInst

  save_bd_design
}
# End of create_root_design()


##################################################################
# MAIN FLOW
##################################################################

create_root_design ""


common::send_gid_msg -ssname BD::TCL -id 2053 -severity "WARNING" "This Tcl script was generated from a block design that has not been validated. It is possible that design <$design_name> may result in errors during validation."

