set vitis_path "/opt/Xilinx/Vitis/2022.2"
set cpu "A53"
set core "#0"
set project_name "memory_evaluator"
set bit_stream_path "../platform/hw/"  
set boot_path "../platform/export/${project_name}/sw/${project_name}/boot"  
set elf_file "../memory_controller/out/${project_name}.elf"  
set hw_server_ip "127.0.0.1"
set hw_server_port "3121"

puts "INFO: Connecting to hardware server tcp:${hw_server_ip}:${hw_server_port}"
connect -url "tcp:${hw_server_ip}:${hw_server_port}"
source "${vitis_path}/scripts/vitis/util/zynqmp_utils.tcl"
targets -set -nocase -filter {name =~"RPU*"}
enable_split_mode

puts "INFO: Selecting APU targets..."
targets -set -nocase -filter {name =~"APU*"}
loadhw -hw "${bit_stream_path}/${project_name}.xsa" -mem-ranges [list {0x80000000 0xbfffffff} {0x400000000 0x5ffffffff} {0x1000000000 0x7fffffffff}] -regs
configparams force-mem-access 1
targets -set -nocase -filter {name =~"APU*"}

puts "INFO: Reading mode register..."
set mode [expr [mrd -value 0xFF5E0200] & 0xf]

puts "INFO: Selecting CPU ${cpu}${core}..."
targets -set -nocase -filter {name =~ "*${cpu}*${core}"}

puts "INFO: Resetting processor..."
rst -processor
dow ${boot_path}/fsbl.elf

puts "INFO: Setting breakpoint at XFsbl_Exit... (May later be removed!)"
set bp_29_41_fsbl_bp [bpadd -addr &XFsbl_Exit]

puts "INFO: Continuing execution until FSBL exit (blocking)..."
con -block -timeout 60
bpremove $bp_29_41_fsbl_bp
targets -set -nocase -filter {name =~ "*${cpu}*${core}"}
rst -processor

puts "INFO: Downloading ELF file: ${elf_file}"
dow "${elf_file}"
configparams force-mem-access 0

con
