#!/bin/bash


echo "***************************************"
echo "********** Memory Evaluator ***********"
echo "******** University of Passau**********"
echo "***************************************"

pushd ../hardware/fpga_design/scripts
echo "Create FPGA Project"

read -p "Would you like to setup the FPGA Project? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    source create_project.sh

    read -p "Generate bitstream? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Generate Bitstream"
        source generate_bitstream.sh

        echo "Generate Bitstream"
        source export_platform.sh
    fi
fi
popd

read -p "Would you like to build the PS Firmware? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
pushd ../software/ps_software/scripts
    source build.sh
popd
fi

read -p "Would you like to flash the bitstream? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
pushd ../hardware/fpga_design/scripts
    source flash_board.sh
popd
fi

read -p "Would you like to flash bit PS Firmware? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
pushd ../software/ps_software/scripts
    source flash_ps.sh
popd
fi