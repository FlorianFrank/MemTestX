#!/bin/bash

# Color definitions
RED="\033[1;31m"
YELLOW="\033[1;33m"
BLUE="\033[1;34m"
RESET="\033[0m"

# Helper functions for colored messages
info()    { echo -e "${BLUE}INFO: $1${RESET}"; }
warn()    { echo -e "${YELLOW}WARNING: $1${RESET}"; }
error()   { echo -e "${RED}ERROR: $1${RESET}"; }

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
        "$VIVADO_PATH" -mode batch -source "$TCL_SCRIPT" 2>&1 | \
        sed -E "s/(ERROR.*)/${RED}\1${RESET}/; s/(WARNING.*)/${YELLOW}\1${RESET}/; s/(INFO.*)/${BLUE}\1${RESET}/"
    else
        echo "INFO: Using existing project. Skipping creation."
    fi
else
    echo "INFO: Creating new project..."
    "$VIVADO_PATH" -mode batch -source "$TCL_SCRIPT" 2>&1 | \
        sed -E "s/(ERROR.*)/${RED}\1${RESET}/; s/(WARNING.*)/${YELLOW}\1${RESET}/; s/(INFO.*)/${BLUE}\1${RESET}/"
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
