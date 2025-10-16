

proc generate {drv_handle} {
	xdefine_include_file $drv_handle "xparameters.h" "ps_pl_interface" "NUM_INSTANCES" "DEVICE_ID"  "C_AXI_Light_Slave_BASEADDR" "C_AXI_Light_Slave_HIGHADDR"
}
