#!/bin/bash


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BUILD_DIR="../memory_evaluator"
PROJECT_FILE="memory_evaluator.xpr"
VITIS_PATH="/opt/Xilinx/Vitis/2022.1/bin/xsct"
TCL_SCRIPT="tcl/export_platform.tcl"
PLATFORM_DIR="${BUILD_DIR}/export/platform/memory_evaluator/*"
PS_SOFTWARE_DIR="${SCRIPT_DIR}/../../../software/ps_software/platform"


RED="\e[1;31m"
YELLOW="\e[1;33m"
ORANGE="\e[1;33m" 
BLUE="\e[1;34m"
RESET="\e[0m"

# Function to colorize output
colorize() {
    while IFS= read -r line; do
        if [[ "$line" == *"ERROR:"* ]]; then
            echo -e "${RED}${line}${RESET}"
        elif [[ "$line" == *"CRITICAL:"* ]]; then
            echo -e "${ORANGE}${line}${RESET}"
        elif [[ "$line" == *"WARNING:"* ]]; then
            echo -e "${YELLOW}${line}${RESET}"
        elif [[ "$line" == *"INFO:"* ]]; then
            echo -e "${BLUE}${line}${RESET}"
        else
            echo "$line"
        fi
    done
}

if [ ! -x "$VITIS_PATH" ]; then
    echo "ERROR: Vitis not found at $VITIS_PATH"
    exit 1
fi

if [ ! -f "$BUILD_DIR/$PROJECT_FILE" ]; then
    echo "ERROR: Project file $BUILD_DIR/$PROJECT_FILE not found"
    exit 1
fi

echo "INFO: Export platform: $BUILD_DIR/$PROJECT_FILE"
"$VITIS_PATH" "$TCL_SCRIPT" 2>&1 | colorize



read -p "Copy Platform to PS Software project? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
echo "cp -r ${PLATFORM_DIR} ${PS_SOFTWARE_DIR}"
  cp -r ${PLATFORM_DIR} ${PS_SOFTWARE_DIR}
fi
