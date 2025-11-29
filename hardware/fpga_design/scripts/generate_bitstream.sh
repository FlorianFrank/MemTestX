#!/bin/bash

BUILD_DIR="../memory_evaluator"
PROJECT_FILE="memory_evaluator.xpr"
VIVADO_PATH="/opt/Xilinx/Vivado/2022.2/bin/vivado"
TCL_SCRIPT="tcl/generate_bitstream.tcl"

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

if [ ! -x "$VIVADO_PATH" ]; then
    echo "ERROR: Vivado not found at $VIVADO_PATH"
    exit 1
fi

if [ ! -f "$BUILD_DIR/$PROJECT_FILE" ]; then
    echo "ERROR: Project file $BUILD_DIR/$PROJECT_FILE not found"
    exit 1
fi

echo "INFO: Open project: $BUILD_DIR/$PROJECT_FILE"
"$VIVADO_PATH" -mode batch -source "$TCL_SCRIPT" 2>&1 | colorize
