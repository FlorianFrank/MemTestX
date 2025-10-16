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
set bd_file "../block_designes/${bd_name}.tcl"

set src_file_dir "${project_dir}/src"
set sim_file_dir "${project_dir}/sim"
set bd_file_dir "${project_dir}/bd"

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

# Copy all source, sim files and block designes (TODO use files directly)
file copy -force ../src $src_file_dir
file copy -force ../sim $sim_file_dir
file copy -force ../block_designes $bd_file_dir

set verilog_files [get_verilog_files $src_file_dir]

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

foreach file $verilog_files {
    puts "INFO: Adding Verilog source: $file"
    add_files -norecurse $file
}

update_compile_order -fileset sources_1


# Add IP cores
set ip_repo_path "../ips"
set_property ip_repo_paths [concat [get_property ip_repo_paths [current_project]] $ip_repo_path] [current_project]
update_ip_catalog


# Load block design
if {[file exists $bd_file]} {
  source $bd_file
}