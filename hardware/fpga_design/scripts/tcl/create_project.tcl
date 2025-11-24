# -------------------------------------------------
#
# Project: Memory Evaluator
# Institute: University of Passau
# Author: Florian Frank
# -------------------------------------------------


# Define Project settings
set project_name "memory_evaluator"
set project_dir "../memory_evaluator"
set part_name "xczu9eg-ffvb1156-2-e"
set bd_name "main_block_design"
set bd_verification_name "axi_verifier_full"
set tb_top_file "tb_axi_full"
set bd_file "../block_designes/${bd_name}.tcl"
set bd_verification_file "../block_designes/${bd_verification_name}.tcl"
set log_dir "../logs"


set src_file_dir "${project_dir}/src"
set sim_file_dir "${project_dir}/sim"
set bd_file_dir "${project_dir}/bd"
set constraints_file_dir "${project_dir}/constraints"

# Create Project and subfolders
if {[file exists $project_dir]} {
    puts "INFO: Project directory already exists. Deleting..."
    file delete -force $project_dir
}

create_project $project_name $project_dir -part $part_name
set_property target_language Verilog [current_project]
set_property simulator_language Mixed [current_project]
puts "INFO: Project $project_name created successfully."

file mkdir $src_file_dir
file mkdir $sim_file_dir
file mkdir $bd_file_dir
file mkdir $log_dir
file mkdir $constraints_file_dir

file copy -force ../src $src_file_dir
file copy -force ../sim $sim_file_dir
file copy -force ../block_designes $bd_file_dir
file copy -force ../constraints/constraints.xdc $constraints_file_dir/


proc get_verilog_files {dir} {
    set files {}

    foreach f [glob -nocomplain -directory $dir *] {
        if {[file isdirectory $f]} {
            set sub_files [get_verilog_files $f]
            set files [concat $files $sub_files]
        } elseif {[string match *.v $f] || [string match *.sv $f] || [string match *.vh $f]} {
            lappend files $f
        }
    }

    return $files
}

set verilog_files [get_verilog_files $src_file_dir]
foreach file $verilog_files {
    puts "INFO: Adding Verilog source: $file"
    add_files -fileset sources_1 -norecurse $file
}

set simulation_files [get_verilog_files $sim_file_dir]
foreach file $simulation_files {
    puts "INFO: Adding Verilog simulation files: $file"
    add_files -fileset sim_1 -norecurse $file
}


update_compile_order -fileset sources_1


# Add IP cores
set ip_repo_path "../ips"
set_property ip_repo_paths [concat [get_property ip_repo_paths [current_project]] $ip_repo_path] [current_project]
update_ip_catalog


# Add constraints file
set constraints_file "${constraints_file_dir}/constraints.xdc"
if {[file exists $constraints_file]} {
    puts "INFO: Adding constraint file: $constraints_file"
    add_files -fileset constrs_1 $constraints_file
} else {
    puts "WARNING: Constraint file not found: $constraints_file"
}

if {[file exists $bd_file]} {
  source $bd_file
}

proc create_hdl_wrapper {block_design_name} {
    global project_dir project_name

    # Path where the wrapper should be copied
    set bd_hdl_wrapper "${project_dir}/src/${block_design_name}_wrapper.v"

    # Path where Vivado generates the wrapper
    set gen_wrapper "${project_dir}/${project_name}.gen/sources_1/bd/${block_design_name}/hdl/${block_design_name}_wrapper.v"

    if {![file exists $bd_hdl_wrapper]} {
        puts "INFO: Creating HDL wrapper for block design: $block_design_name"
        make_wrapper -files [get_files "${project_dir}/${project_name}.srcs/sources_1/bd/${block_design_name}/${block_design_name}.bd"] -top

        # Copy wrapper to src folder
        file copy -force $gen_wrapper $bd_hdl_wrapper
    } else {
        puts "INFO: HDL wrapper already exists: $bd_hdl_wrapper"
    }

    add_files -norecurse $bd_hdl_wrapper
}

create_hdl_wrapper $bd_name


  # Set top module of the project
  if {[file exists $bd_file]} {
  set_property top ${bd_name}_wrapper [current_fileset]
  puts "INFO: Top module set to ${bd_name}_wrapper"
} else {
  puts "WARNING: Block design file not found: $bd_file"
}

puts "INFO: Enable constraints"
set_property is_enabled true [get_files "${project_dir}/constraints/constraints.xdc"]
set_property USED_IN_SYNTHESIS true [get_files "${project_dir}/constraints/constraints.xdc"]
set_property USED_IN_IMPLEMENTATION true [get_files "${project_dir}/constraints/constraints.xdc"]



puts "INFO: Setup Block Design for AXI Verification"


if {[file exists $bd_verification_file]} {
  source $bd_verification_file
}

create_hdl_wrapper $bd_verification_name

set_property top ${tb_top_file} [get_filesets sim_1]
set_property top_lib xil_defaultlib [get_filesets sim_1]
update_compile_order -fileset sim_1