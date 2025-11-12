
set build_dir "../memory_evaluator"
set project_name "memory_evaluator"
set export_dir "${build_dir}/export/platform"
set block_design_name "main_block_design"
set cpu "cortexa53"
set core 0

file mkdir $export_dir

puts "INFO: Open Project ${build_dir}/export/${project_name}.xsa and generate platform for psu_${cpu}_${core}"

platform create \
    -name $project_name \
    -hw "${build_dir}/export/${project_name}.xsa" \
    -arch 64-bit \
    -fsbl-target "psu_${cpu}_${core}" \
    -out $export_dir

platform write

puts "INFO: Create Domain"
domain create \
    -name "standalone_psu_${cpu}_${core}" \
    -display-name "standalone_psu_${cpu}_${core}" \
    -os standalone \
    -proc "psu_${cpu}_${core}" \
    -runtime cpp \
    -arch 64-bit \
    -support-app lwip_echo_server

platform write

platform active "${project_name}"
puts "INFO: Activate Domains"
domain active {zynqmp_fsbl}
domain active {zynqmp_pmufw}
domain active "standalone_psu_${cpu}_${core}"

puts "INFO: Build standalone library"

platform generate
puts "INFO: Platform generation done"