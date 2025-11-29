#!/bin/bash

VITIS_PATH="/opt/Xilinx/Vitis/2022.2/bin/xsdb"
TCL_SCRIPT="tcl/flash_ps.tcl"

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

echo "INFO: Export platform: $BUILD_DIR/$PROJECT_FILE"
"$VITIS_PATH" "$TCL_SCRIPT" 2>&1 | colorize
