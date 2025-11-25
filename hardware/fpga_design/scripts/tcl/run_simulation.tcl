
set build_dir "../memory_evaluator"
set project_name "memory_evaluator"

open_project ${build_dir}/${project_name}.xpr
update_compile_order -fileset sim_1
launch_simulation -simset sim_1
current_fileset -simset sim_1

# Restart simulation cleanly
restart

# Run the simulation (modify as needed)
run 10000 ns

start_gui