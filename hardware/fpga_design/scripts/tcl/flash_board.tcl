
set device_part "xczu9_0"
set build_dir "../memory_evaluator"
set bit_file "${build_dir}/export/memory_evaluator.bit"

puts "INFO: Opening hardware manager and connecting to HW server..."
open_hw_manager
connect_hw_server -allow_non_jtag

puts "INFO: Opening hardware target..."
open_hw_target

set xczu9 [lindex [get_hw_devices $device_part] 0]
set arm_dap [lindex [get_hw_devices arm_dap_1] 0]
puts "INFO: Refreshing devices..."
refresh_hw_device -update_hw_probes false $xczu9
refresh_hw_device -update_hw_probes false $arm_dap

current_hw_device $xczu9

puts "INFO: Clearing probe files..."
set_property PROBES.FILE {} $xczu9
set_property FULL_PROBES.FILE {} $xczu9

puts "INFO: Programming XCZU9 with bitstream: $bit_file"
set_property PROGRAM.FILE $bit_file $xczu9
program_hw_devices $xczu9

puts "INFO: Hardware programming completed."