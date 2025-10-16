# Constraints must be coherent with the PCB adapter board


##
## *** Data Lines ***
##


# J5 Pin C10
set_property -dict {PACKAGE_PIN AC2 IOSTANDARD LVCMOS18} [get_ports {dlines[0]}]
# J5 Pin C11
set_property -dict {PACKAGE_PIN AC1 IOSTANDARD LVCMOS18} [get_ports {dlines[1]}]
# J5 Pin C14
set_property -dict {PACKAGE_PIN W5 IOSTANDARD LVCMOS18} [get_ports {dlines[2]}]
# J5 Pin C15
set_property -dict {PACKAGE_PIN W4 IOSTANDARD LVCMOS18} [get_ports {dlines[3]}]
# J5 Pin C18
set_property -dict {PACKAGE_PIN AC7 IOSTANDARD LVCMOS18} [get_ports {dlines[4]}]
# J5 Pin C19
set_property -dict {PACKAGE_PIN AC6 IOSTANDARD LVCMOS18} [get_ports {dlines[5]}]
# J5 Pin C22
set_property -dict {PACKAGE_PIN N9 IOSTANDARD LVCMOS18} [get_ports {dlines[6]}]
# J5 Pin C23
set_property -dict {PACKAGE_PIN N8 IOSTANDARD LVCMOS18} [get_ports {dlines[7]}]


# J5 Pin C26
set_property -dict {PACKAGE_PIN M10 IOSTANDARD LVCMOS18} [get_ports {dlines[8]}]
# J5 Pin C27
set_property -dict {PACKAGE_PIN L10 IOSTANDARD LVCMOS18} [get_ports {dlines[9]}]
# J5 Pin D8
set_property -dict {PACKAGE_PIN AB4 IOSTANDARD LVCMOS18} [get_ports {dlines[10]}]
# J5 Pin D9
set_property -dict {PACKAGE_PIN AC4 IOSTANDARD LVCMOS18} [get_ports {dlines[11]}]
# J5 Pin D11
set_property -dict {PACKAGE_PIN AB3 IOSTANDARD LVCMOS18} [get_ports {dlines[12]}]
# J5 Pin D12
set_property -dict {PACKAGE_PIN AC3 IOSTANDARD LVCMOS18} [get_ports {dlines[13]}]
# J5 Pin D14
set_property -dict {PACKAGE_PIN W2 IOSTANDARD LVCMOS18} [get_ports {dlines[14]}]
# J5 Pin D15
set_property -dict {PACKAGE_PIN W1 IOSTANDARD LVCMOS18} [get_ports {dlines[15]}]



##
## *** Address Lines ***
##

# J5 Pin D17
set_property -dict {PACKAGE_PIN AB8 IOSTANDARD LVCMOS18} [get_ports {alines[0]}]
# J5 Pin D18
set_property -dict {PACKAGE_PIN AC8 IOSTANDARD LVCMOS18} [get_ports {alines[1]}]
# J5 Pin D20
set_property -dict {PACKAGE_PIN P11 IOSTANDARD LVCMOS18} [get_ports {alines[2]}]
# J5 Pin D21
set_property -dict {PACKAGE_PIN N11 IOSTANDARD LVCMOS18} [get_ports {alines[3]}]
# J5 Pin D23
set_property -dict {PACKAGE_PIN L16 IOSTANDARD LVCMOS18} [get_ports {alines[4]}]
# J5 Pin D24
set_property -dict {PACKAGE_PIN K16 IOSTANDARD LVCMOS18} [get_ports {alines[5]}]
# J5 Pin D26
set_property -dict {PACKAGE_PIN L15 IOSTANDARD LVCMOS18} [get_ports {alines[6]}]
# J5 Pin D27
set_property -dict {PACKAGE_PIN K15 IOSTANDARD LVCMOS18} [get_ports {alines[7]}]

# J5 Pin G6
set_property -dict {PACKAGE_PIN Y4 IOSTANDARD LVCMOS18} [get_ports {alines[8]}]
# J5 Pin G7
set_property -dict {PACKAGE_PIN Y3 IOSTANDARD LVCMOS18} [get_ports {alines[9]}]
# J5 Pin G9
set_property -dict {PACKAGE_PIN Y2 IOSTANDARD LVCMOS18} [get_ports {alines[10]}]
# J5 Pin G10
set_property -dict {PACKAGE_PIN Y1 IOSTANDARD LVCMOS18} [get_ports {alines[11]}]
# J5 Pin G12
set_property -dict {PACKAGE_PIN V4 IOSTANDARD LVCMOS18} [get_ports {alines[12]}]
# J5 Pin G13
set_property -dict {PACKAGE_PIN V3 IOSTANDARD LVCMOS18} [get_ports {alines[13]}]
# J5 Pin G15
set_property -dict {PACKAGE_PIN W7 IOSTANDARD LVCMOS18} [get_ports {alines[14]}]
# J5 Pin G16
set_property -dict {PACKAGE_PIN W6 IOSTANDARD LVCMOS18} [get_ports {alines[15]}]

# J5 Pin G18
set_property -dict {PACKAGE_PIN Y12 IOSTANDARD LVCMOS18} [get_ports {alines[16]}]
# J5 Pin G19
set_property -dict {PACKAGE_PIN AA12 IOSTANDARD LVCMOS18} [get_ports {alines[17]}]
# J5 Pin G21
set_property -dict {PACKAGE_PIN N13 IOSTANDARD LVCMOS18} [get_ports {alines[18]}]
# J5 Pin G22
set_property -dict {PACKAGE_PIN M13 IOSTANDARD LVCMOS18} [get_ports {alines[19]}]
# J5 Pin G24
set_property -dict {PACKAGE_PIN M15 IOSTANDARD LVCMOS18} [get_ports {alines[20]}]
# J5 Pin G25
set_property -dict {PACKAGE_PIN M14 IOSTANDARD LVCMOS18} [get_ports {alines[21]}]
# J5 Pin G27
set_property -dict {PACKAGE_PIN M11 IOSTANDARD LVCMOS18} [get_ports {alines[22]}]
# J5 Pin G28
set_property -dict {PACKAGE_PIN L11 IOSTANDARD LVCMOS18} [get_ports {alines[23]}]


##
## *** Memory Control Lines ***
##

# J5 Pin G30
set_property -dict {PACKAGE_PIN U9 IOSTANDARD LVCMOS18} [get_ports {oe}]
# J5 Pin G31
set_property -dict {PACKAGE_PIN U8 IOSTANDARD LVCMOS18} [get_ports {we}]
# J5 Pin G33
set_property -dict {PACKAGE_PIN V8 IOSTANDARD LVCMOS18} [get_ports {ce}]
# J5 Pin G34
set_property -dict {PACKAGE_PIN V7 IOSTANDARD LVCMOS18} [get_ports {lb}]
# J5 Pin G36
set_property -dict {PACKAGE_PIN V12 IOSTANDARD LVCMOS18} [get_ports {ub}]
# J5 Pin G37
set_property -dict {PACKAGE_PIN V11 IOSTANDARD LVCMOS18} [get_ports {zz}]


##
## *** TI Transceivers Config Lines ***
##

# J5 Pin H8
set_property -dict {PACKAGE_PIN V1 IOSTANDARD LVCMOS18} [get_ports {dir_var}]
# J5 Pin H10
set_property -dict {PACKAGE_PIN AA2 IOSTANDARD LVCMOS18} [get_ports {dir_const}]
# J5 Pin H7
set_property -dict {PACKAGE_PIN V2 IOSTANDARD LVCMOS18} [get_ports {en_const}]


##
## *** Debugging and Further Configuration ***
##

## Switches SW13
set_property -dict {PACKAGE_PIN AN14 IOSTANDARD LVCMOS33} [get_ports {disable_axi_switch}]
# Push Button
set_property -dict {PACKAGE_PIN AG15 IOSTANDARD LVCMOS33} [get_ports {simulate_test_button}]
# J5 H29
set_property -dict {PACKAGE_PIN K12 IOSTANDARD LVCMOS18} [get_ports {en_var}]
# J5 H31
set_property -dict {PACKAGE_PIN T7  IOSTANDARD LVCMOS18} [get_ports {ref_vcc}]
# J5 H32
set_property -dict {PACKAGE_PIN T6 IOSTANDARD LVCMOS18} [get_ports {ref_vcc2}]
