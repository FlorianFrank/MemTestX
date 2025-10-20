cmake_minimum_required(VERSION 3.3)
set(CMAKE_TOOLCHAIN_FILE "toolchain/xilinx_cortex_a53.cmake" CACHE FILEPATH "Toolchain file")

project(memory_evaluator C)
set(CMAKE_CXX_STANDARD 14)
set(EXEC_NAME memory_evaluator.elf)

file(GLOB SRC_FILES src/*.c src/*.cpp src/config/*.c)
file(GLOB BOARD_SUPPORT_FILES src/board_support/*.c)
file(GLOB GCC_FILES
        ${PLATFORM_DIR}/zynqmp_fsbl/zynqmp_fsbl_bsp/psu_cortexa53_0/libsrc/standalone_v7_7/src/arm/common/gcc/*.c
        ${PLATFORM_DIR}/psu_cortexa53_0/standalone_psu_cortexa53_0/bsp/psu_cortexa53_0/libsrc/lwip211_v1_7/src/lwip-2.1.1/src/include)


file(GLOB ETH_FILES
        ${PLATFORM_DIR}/psu_cortexa53_0/standalone_psu_cortexa53_0/bsp/psu_cortexa53_0/libsrc/emacps_v3_16/src/*.c
        ${PLATFORM_DIR}/zynqmp_fsbl/zynqmp_fsbl_bsp/psu_cortexa53_0/libsrc/standalone_v7_7/src/xil_mmu.c)

add_executable(${EXEC_NAME} ${SRC_FILES} ${BOARD_SUPPORT_FILES} ${GCC_FILES} ${ETH_FILES})

target_include_directories(${EXEC_NAME} PUBLIC
        include/board_support
        ${PLATFORM_DIR}/export/main_block_design_wrapper/sw/main_block_design_wrapper/standalone_psu_cortexa53_0/bspinclude/include
        ${PLATFORM_DIR}/zynqmp_fsbl/zynqmp_fsbl_bsp/psu_cortexa53_0/include
        ${PLATFORM_DIR}/psu_cortexa53_0/standalone_psu_cortexa53_0/bsp/psu_cortexa53_0/libsrc/lwip211_v1_7/src/contrib/ports/xilinx/include
        ${PLATFORM_DIR}/psu_cortexa53_0/standalone_psu_cortexa53_0/bsp/psu_cortexa53_0/libsrc/lwip211_v1_7/src/lwip-2.1.1/src/include)

target_link_directories(${EXEC_NAME} PUBLIC
        ${PLATFORM_DIR}/sw/zcu_102_sgmii_sfp/standalone_psu_cortexa53_0/bsplib/lib
        ${PLATFORM_DIR}/zynqmp_fsbl/zynqmp_fsbl_bsp/psu_cortexa53_0/lib
        ${PLATFORM_DIR}/export/main_block_design_wrapper/sw/main_block_design_wrapper/standalone_psu_cortexa53_0/bsplib/lib)

target_link_libraries(${EXEC_NAME} PUBLIC xil lwip4 gcc c)
