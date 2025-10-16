# Definitional proc to organize widgets for parameters.
proc init_gui { IPINST } {
  ipgui::add_param $IPINST -name "Component_Name"
  #Adding Page
  set Page_0 [ipgui::add_page $IPINST -name "Page 0"]
  ipgui::add_param $IPINST -name "C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_AXI_Light_Master_ADDR_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_AXI_Light_Master_DATA_WIDTH" -parent ${Page_0} -widget comboBox
  ipgui::add_param $IPINST -name "C_AXI_Light_Master_TRANSACTIONS_NUM" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_AXI_Light_Slave_DATA_WIDTH" -parent ${Page_0} -widget comboBox
  ipgui::add_param $IPINST -name "C_AXI_Light_Slave_ADDR_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_AXI_Light_Slave_BASEADDR" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_AXI_Light_Slave_HIGHADDR" -parent ${Page_0}
  ipgui::add_param $IPINST -name "MEM_ADRESS_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "MEM_DATA_WIDTH" -parent ${Page_0}


}

proc update_PARAM_VALUE.MEM_ADRESS_WIDTH { PARAM_VALUE.MEM_ADRESS_WIDTH } {
	# Procedure called to update MEM_ADRESS_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.MEM_ADRESS_WIDTH { PARAM_VALUE.MEM_ADRESS_WIDTH } {
	# Procedure called to validate MEM_ADRESS_WIDTH
	return true
}

proc update_PARAM_VALUE.MEM_DATA_WIDTH { PARAM_VALUE.MEM_DATA_WIDTH } {
	# Procedure called to update MEM_DATA_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.MEM_DATA_WIDTH { PARAM_VALUE.MEM_DATA_WIDTH } {
	# Procedure called to validate MEM_DATA_WIDTH
	return true
}

proc update_PARAM_VALUE.C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR { PARAM_VALUE.C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR } {
	# Procedure called to update C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR { PARAM_VALUE.C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR } {
	# Procedure called to validate C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR
	return true
}

proc update_PARAM_VALUE.C_AXI_Light_Master_ADDR_WIDTH { PARAM_VALUE.C_AXI_Light_Master_ADDR_WIDTH } {
	# Procedure called to update C_AXI_Light_Master_ADDR_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXI_Light_Master_ADDR_WIDTH { PARAM_VALUE.C_AXI_Light_Master_ADDR_WIDTH } {
	# Procedure called to validate C_AXI_Light_Master_ADDR_WIDTH
	return true
}

proc update_PARAM_VALUE.C_AXI_Light_Master_DATA_WIDTH { PARAM_VALUE.C_AXI_Light_Master_DATA_WIDTH } {
	# Procedure called to update C_AXI_Light_Master_DATA_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXI_Light_Master_DATA_WIDTH { PARAM_VALUE.C_AXI_Light_Master_DATA_WIDTH } {
	# Procedure called to validate C_AXI_Light_Master_DATA_WIDTH
	return true
}

proc update_PARAM_VALUE.C_AXI_Light_Master_TRANSACTIONS_NUM { PARAM_VALUE.C_AXI_Light_Master_TRANSACTIONS_NUM } {
	# Procedure called to update C_AXI_Light_Master_TRANSACTIONS_NUM when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXI_Light_Master_TRANSACTIONS_NUM { PARAM_VALUE.C_AXI_Light_Master_TRANSACTIONS_NUM } {
	# Procedure called to validate C_AXI_Light_Master_TRANSACTIONS_NUM
	return true
}

proc update_PARAM_VALUE.C_AXI_Light_Slave_DATA_WIDTH { PARAM_VALUE.C_AXI_Light_Slave_DATA_WIDTH } {
	# Procedure called to update C_AXI_Light_Slave_DATA_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXI_Light_Slave_DATA_WIDTH { PARAM_VALUE.C_AXI_Light_Slave_DATA_WIDTH } {
	# Procedure called to validate C_AXI_Light_Slave_DATA_WIDTH
	return true
}

proc update_PARAM_VALUE.C_AXI_Light_Slave_ADDR_WIDTH { PARAM_VALUE.C_AXI_Light_Slave_ADDR_WIDTH } {
	# Procedure called to update C_AXI_Light_Slave_ADDR_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXI_Light_Slave_ADDR_WIDTH { PARAM_VALUE.C_AXI_Light_Slave_ADDR_WIDTH } {
	# Procedure called to validate C_AXI_Light_Slave_ADDR_WIDTH
	return true
}

proc update_PARAM_VALUE.C_AXI_Light_Slave_BASEADDR { PARAM_VALUE.C_AXI_Light_Slave_BASEADDR } {
	# Procedure called to update C_AXI_Light_Slave_BASEADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXI_Light_Slave_BASEADDR { PARAM_VALUE.C_AXI_Light_Slave_BASEADDR } {
	# Procedure called to validate C_AXI_Light_Slave_BASEADDR
	return true
}

proc update_PARAM_VALUE.C_AXI_Light_Slave_HIGHADDR { PARAM_VALUE.C_AXI_Light_Slave_HIGHADDR } {
	# Procedure called to update C_AXI_Light_Slave_HIGHADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXI_Light_Slave_HIGHADDR { PARAM_VALUE.C_AXI_Light_Slave_HIGHADDR } {
	# Procedure called to validate C_AXI_Light_Slave_HIGHADDR
	return true
}


proc update_MODELPARAM_VALUE.C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR { MODELPARAM_VALUE.C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR PARAM_VALUE.C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR}] ${MODELPARAM_VALUE.C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR}
}

proc update_MODELPARAM_VALUE.C_AXI_Light_Master_ADDR_WIDTH { MODELPARAM_VALUE.C_AXI_Light_Master_ADDR_WIDTH PARAM_VALUE.C_AXI_Light_Master_ADDR_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_AXI_Light_Master_ADDR_WIDTH}] ${MODELPARAM_VALUE.C_AXI_Light_Master_ADDR_WIDTH}
}

proc update_MODELPARAM_VALUE.C_AXI_Light_Master_DATA_WIDTH { MODELPARAM_VALUE.C_AXI_Light_Master_DATA_WIDTH PARAM_VALUE.C_AXI_Light_Master_DATA_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_AXI_Light_Master_DATA_WIDTH}] ${MODELPARAM_VALUE.C_AXI_Light_Master_DATA_WIDTH}
}

proc update_MODELPARAM_VALUE.C_AXI_Light_Master_TRANSACTIONS_NUM { MODELPARAM_VALUE.C_AXI_Light_Master_TRANSACTIONS_NUM PARAM_VALUE.C_AXI_Light_Master_TRANSACTIONS_NUM } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_AXI_Light_Master_TRANSACTIONS_NUM}] ${MODELPARAM_VALUE.C_AXI_Light_Master_TRANSACTIONS_NUM}
}

proc update_MODELPARAM_VALUE.C_AXI_Light_Slave_DATA_WIDTH { MODELPARAM_VALUE.C_AXI_Light_Slave_DATA_WIDTH PARAM_VALUE.C_AXI_Light_Slave_DATA_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_AXI_Light_Slave_DATA_WIDTH}] ${MODELPARAM_VALUE.C_AXI_Light_Slave_DATA_WIDTH}
}

proc update_MODELPARAM_VALUE.C_AXI_Light_Slave_ADDR_WIDTH { MODELPARAM_VALUE.C_AXI_Light_Slave_ADDR_WIDTH PARAM_VALUE.C_AXI_Light_Slave_ADDR_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_AXI_Light_Slave_ADDR_WIDTH}] ${MODELPARAM_VALUE.C_AXI_Light_Slave_ADDR_WIDTH}
}

proc update_MODELPARAM_VALUE.MEM_ADRESS_WIDTH { MODELPARAM_VALUE.MEM_ADRESS_WIDTH PARAM_VALUE.MEM_ADRESS_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.MEM_ADRESS_WIDTH}] ${MODELPARAM_VALUE.MEM_ADRESS_WIDTH}
}

proc update_MODELPARAM_VALUE.MEM_DATA_WIDTH { MODELPARAM_VALUE.MEM_DATA_WIDTH PARAM_VALUE.MEM_DATA_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.MEM_DATA_WIDTH}] ${MODELPARAM_VALUE.MEM_DATA_WIDTH}
}

