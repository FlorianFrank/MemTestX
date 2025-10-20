set build_dir "../memory_evaluator"
set project_name "memory_evaluator"
set block_design_name "main_block_design"

file mkdir "$build_dir/export"
file mkdir "$build_dir/checkpoints"

puts "INFO: Open Project ${build_dir}/${project_name}.xpr"
open_project "${build_dir}/${project_name}.xpr"

puts "INFO: Open block design"
open_bd_design "${build_dir}/${project_name}.srcs/sources_1/bd/${block_design_name}/${block_design_name}.bd"

puts "INFO: Set top module and update compile order"
set_property top "${block_design_name}_wrapper" [current_fileset]
update_compile_order -fileset sources_1

read_xdc "${build_dir}/constraints/constraints.xdc"

puts "INFO: Generate Block Design"
generate_target all [get_files "${build_dir}/${project_name}.srcs/sources_1/bd/${block_design_name}/${block_design_name}.bd"]

# Synthesis
puts "INFO: Launch Synthesis"
if {[llength [get_runs synth_1]] > 0} {
    puts "INFO: Synthesis run 'synth_1' already exists. Resetting run..."
    reset_run synth_1
} else {
    puts "INFO: Creating synthesis run 'synth_1'"
    create_run synth_1 -flow {SYNTHESIS}
}

# Launch synthesis
launch_runs synth_1
wait_on_run synth_1
open_run synth_1
puts "INFO: Load synthesis run"
write_checkpoint -force "${build_dir}/checkpoints/post_synth.dcp"

# Optimization
open_checkpoint "${build_dir}/checkpoints/post_synth.dcp"
puts "INFO: Optimize design"
opt_design
report_methodology -file $build_dir/export/post_opt_methodology.rpt

place_design
phys_opt_design
write_checkpoint -force "${build_dir}/checkpoints/post_place.dcp"
report_timing_summary -file $build_dir/export/post_place_timing_summary.rpt

route_design
write_bitstream -force "${build_dir}/export/${project_name}.bit"

puts "INFO: Bitstream generated"