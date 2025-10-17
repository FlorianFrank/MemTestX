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

if {[llength [get_runs synth_1]] == 0} {
    create_run synth_1 -flow {SYNTHESIS}
} else {
    puts "INFO: Synthesis run 'synth_1' already exists. Using existing run."
}

# Launch synthesis
launch_runs synth_1
wait_on_run synth_1

# Create checkpoints directory
file mkdir -p "${build_dir}/checkpoints"
write_checkpoint -force "${build_dir}/checkpoints/post_synth.dcp"

puts "INFO: Load synthesis run"
open_run synth_1


# Optimization
puts "INFO: Optimize design"
opt_design

report_methodology -file $build_dir/export/post_opt_methodology.rpt

phys_opt_design
write_checkpoint -force $build_dir/checkpoints/post_place
report_timing_summary -file $build_dir/export/post_place_timing_summary.rpt

# Implementation
puts "INFO: Run Implementation and bitstream generation"
if {[llength [get_runs impl_1]] == 0} {
    create_run impl_1 -flow {IMPLEMENTATION}
} else {
    puts "INFO: Implementation run 'impl_1' already exists. Using existing run."
}
launch_runs impl_1 -to_step write_bitstream
wait_on_run impl_1

puts "INFO: Bitstream generated"