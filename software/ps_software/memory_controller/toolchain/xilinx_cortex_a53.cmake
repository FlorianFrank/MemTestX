

# xilinx-arm-r5-toolchain.cmake
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR cortex-a53)
set(PLATFORM_DIR ${PROJECT_SOURCE_DIR}/../platform)

set(TOOLCHAIN_PATH /opt/Xilinx/Vitis/2022.1/gnu/aarch64/lin/aarch64-none/bin)

set(CMAKE_C_COMPILER ${TOOLCHAIN_PATH}/aarch64-none-elf-gcc)
set(CMAKE_CXX_COMPILER ${TOOLCHAIN_PATH}/aarch64-none-elf-g++)

set(CMAKE_ASM_COMPILER ${TOOLCHAIN_PATH}/aarch64-none-elf-as)
set(CMAKE_LINKER ${TOOLCHAIN_PATH}/aarch64-none-elf-ld)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Specify the flags for the Cortex-R5 architecture
set(CMAKE_C_FLAGS "-mcpu=cortex-a53 -mtune=cortex-a53 -march=armv8-a" CACHE STRING "" FORCE)
set(CMAKE_CXX_FLAGS "${CMAKE_C_FLAGS}" CACHE STRING "" FORCE)

# Specify linker flags if necessary (e.g., for standalone/baremetal apps)
set(LINKER_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/src/lscript.ld") # Modify this path as needed
set(CMAKE_EXE_LINKER_FLAGS "-Wl,-T ${LINKER_SCRIPT} -L${PLATFORM_DIR}/export/main_block_design_wrapper/sw/main_block_design_wrapper/standalone_psu_cortexa53_0/bsplib/lib -Wl,--start-group,-lxil,-lgcc,-lc,--end-group -Wl,--start-group,-lxil,-llwip4,-lgcc,-lc,--end-group" CACHE STRING "" FORCE)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)