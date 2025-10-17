set build_dir "../memory_evaluator"
set project_name "memory_evaluator"
set block_design_name "main_block_design"

puts "INFO: Open Project ${build_dir}/${project_name}.xpr"
open_project "${build_dir}/${project_name}.xpr"

puts "INFO: Define block design"
current_bd_design [get_bd_designs "${block_design_name}"]
set_property top "${block_design_name}_wrapper" [current_fileset]
update_compile_order -fileset sources_1

puts "INFO: Generate Block Design"
generate_target all [get_files "${build_dir}/${project_name}.srcs/sources_1/bd/${block_design_name}/${block_design_name}.bd"]


# RUNSynthesis
puts "INFO: Launch Synthesis"
launch_runs synth_1
wait_on_run synth_1

puts "INFO: Synthesis Done. Load file"
open_run synth_1

puts "INFO: Run Implementation and bitstream generation"
launch_run impl_1 -to_step write_bitstream
wait_on_run impl_1

puts "INFO: Bitstream generated"
