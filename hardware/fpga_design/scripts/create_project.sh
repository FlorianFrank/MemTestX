#!/bin/bash

# Color definitions
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

echo "**************************************"
echo "********** Memory Evaluator **********"
echo "**************************************"
echo ""
echo "Start Creating Project ..."

BUILD_DIR="../memory_evaluator"
PROJECT_FILE="memory_evaluator.xpr"
VIVADO_PATH="/opt/Xilinx/Vivado/2022.1/bin/vivado"
TCL_SCRIPT="tcl/create_project.tcl"

if [ ! -x "$VIVADO_PATH" ]; then
    echo "ERROR: Vivado not found at $VIVADO_PATH"
    exit 1
fi

if [ -d "$BUILD_DIR" ]; then
    echo "INFO: $BUILD_DIR already exists."
    read -p "Would you like to recreate the project? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "INFO: Creating new project..."
        "$VIVADO_PATH" -mode batch -source "$TCL_SCRIPT" 2>&1 | colorize
    else
        echo "INFO: Using existing project. Skipping creation."
    fi
else
    echo "INFO: Creating new project..."
    "$VIVADO_PATH" -mode batch -source "$TCL_SCRIPT" 2>&1 | colorize
fi

read -p "Open Project in Vivado GUI? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "$BUILD_DIR/$PROJECT_FILE" ]; then
        "$VIVADO_PATH" "$BUILD_DIR/$PROJECT_FILE"
    else
        echo "ERROR: Project file $BUILD_DIR/$PROJECT_FILE not found."
        exit 1
    fi
fi
