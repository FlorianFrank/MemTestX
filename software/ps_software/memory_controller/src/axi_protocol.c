/**
 * @file    axi_protocol.c
 * @brief   Implements the interface between the PS and PL using AXI Lite.
 *          Provides the protocol to configure PUF-based tests and
 *          receives and decodes measured data from the interface.
 *
 * @author  Florian Frank
 * @affiliation University of Passau
 * @date    2025
 */

#include "axi_protocol.h"

#include "xil_cache.h" // Xil_DCacheFlush
#include <stdio.h> // printf, only for debugging purposes
#include <xil_io.h> // Xil_Out32, Xil_In32

#define TestBENCH 0
#define ADDRESS_OFFSET 0x40000000

/**
 * @brief Prints the Verilog testbench AXI write commands for a given value.
 * Prints out the lines which can be copied to the axi_full_simulator found in the hardware/fpga_design folder.
 *
 * @param idx    Index/address offset of the AXI write.
 * @param value  32-bit value to copy to the testbench.
 */
void printVerilogTBConfig( int idx, uint32_t value) {
#if TESTBENCH
    printf(" master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h%x, 0, 32'h%02X_%02X_%02X_%02X, resp);\n", idx, (value >> 24) & 0xFF,
           (value >> 16) & 0xFF,
           (value >> 8) & 0xFF,
           value & 0xFF);
#else
    printf("master_agent.AXI4LITE_WRITE_BURST(base_addr + addr + 32'h%x, 0, 32'h%02X_%02X_%02X_%02X, resp);\n", idx, value >> 24 & 0xFF,
       value >> 16 & 0xFF,
       value >> 8 & 0xFF,
       value & 0xFF);
#endif
}

/**
 * @brief Creates AXI segments based on the provided PUF configuration and writes
 *        them to the PS-PL interface.
 *
 * @param pufConfig  Pointer to the PUF configuration structure containing general,
 *                   write, and read timing parameters.
 */
void createAXISegments(const PUFConfiguration *pufConfig) {
    uint32_t segmentList[128];
    int maxBursts = 0;
    const Cmd cmd = pufConfig->generalConfig.command;
    if (cmd == CMD_RESET || cmd == CMD_IDN) {
        segmentList[0] = (uint8_t)cmd;
        maxBursts = 1;
    } else if (cmd == CMD_START_MEASUREMENT) {

        // First 32 bit CMD (8 bit) || puf type (8 bit) // ce_driven // tWaitAfterInit || CHECKED: TRUE
        segmentList[0] = (uint8_t)cmd | (uint32_t)pufConfig->generalConfig.pufType << 8 |
                         ((uint32_t)pufConfig->generalConfig.ceDrivenWrite ? 0xff : 0x00) << 16 |
                             (uint32_t)(pufConfig->generalConfig.tWaitAfterInit & 0xff) << 24;

        // Second half of TWaitAfterInit, TNextRead == 0x02, 8 bit of tStartDefault || CHECKED: TRUE
        segmentList[1] = (uint32_t)pufConfig->generalConfig.tWaitAfterInit >> 8 & 0xff |
                         (uint32_t)pufConfig->generalConfig.tNextRead << 8
                         | ((uint32_t)pufConfig->writeTimingConfigDefault.tStart & 0xff) << 24;

        // second half of tStartDefault, tNextWriteDefault = 0x05, 8-bits of tACDefault || CHECKED: TRUE
        segmentList[2] = (uint32_t)pufConfig->writeTimingConfigDefault.tStart >> 8 & 0xff |
                         (uint32_t)pufConfig->writeTimingConfigDefault.tNext << 8
                         | ((uint32_t)pufConfig->writeTimingConfigDefault.tAC & 0xff) << 24;

        // second half of tACDefault, tASDefault = 0x06, 8-bits of tAHDefault = 0x07 || CHECKED: TRUE
        segmentList[3] = (uint32_t)pufConfig->writeTimingConfigDefault.tAC >> 8 & 0xff |
                         (uint32_t)pufConfig->writeTimingConfigDefault.tAS << 8
                         | ((uint32_t)pufConfig->writeTimingConfigDefault.tAH & 0xff) << 24;

        // second half of tAHDefault, tPWDDefault = 0x08, 8-bits of tDSDefault = 0x09 || CHECKED: TRUE
        segmentList[4] = (uint32_t)pufConfig->writeTimingConfigDefault.tAH >> 8 & 0xff |
                         (uint32_t)pufConfig->writeTimingConfigDefault.tPWD << 8
                         | ((uint32_t)pufConfig->writeTimingConfigDefault.tDS & 0xff) << 24;

        // second half of tDSDefault, tDHDefault = 0x0a, 8-bits of initValue = 0xaaaa || CHECKED: TRUE
        segmentList[5] = (uint32_t)pufConfig->writeTimingConfigDefault.tDS >> 8 & 0xff |
                         (uint32_t)pufConfig->writeTimingConfigDefault.tDH << 8
                         | ((uint32_t)pufConfig->generalConfig.initValue & 0xff) << 24;

        // second half of initValue, pufValue = 0x5555, 8-bits of startAddress = 0x1234 || CHECKED: TRUE
        segmentList[6] = (uint32_t)pufConfig->generalConfig.initValue >> 8 & 0xff |
                         (uint32_t)pufConfig->generalConfig.pufValue << 8
                         | ((uint32_t)pufConfig->generalConfig.startAddress & 0xff) << 24;

        // second half of startAddress 8-bits of end address = 0x7fff || CHECKED: TRUE
        // second half of startAddress 8-bits of end address = 0x7fff || CHECKED: TRUE
        segmentList[7] = (uint32_t)pufConfig->generalConfig.startAddress >> 8 & 0xffffff |
                         ((uint32_t)pufConfig->generalConfig.endAddress & 0xff) << 24;

        segmentList[8] = (uint32_t)pufConfig->generalConfig.endAddress >> 8 & 0xffffff |
                         ((uint32_t)pufConfig->generalConfig.ceDrivenWrite ? 0xff : 0x00) << 24;


        segmentList[9] = (uint32_t)pufConfig->readTimingConfigDefault.tStart |
                         (uint32_t)pufConfig->readTimingConfigDefault.tAS << 16;

        segmentList[10] = (uint32_t)pufConfig->readTimingConfigDefault.tAH |
                          (uint32_t)pufConfig->readTimingConfigDefault.tEOD << 16;

        segmentList[11] = (uint32_t)pufConfig->readTimingConfigDefault.tPRC |
                          (uint32_t)pufConfig->readTimingConfigDefault.tCEOEEnable << 16;
        segmentList[12] = 0 | (uint32_t)pufConfig->readTimingConfigDefault.tCEOEDisable;


        switch (pufConfig->generalConfig.pufType) {

            case RELIABLE:
                maxBursts = 13;
                break;
            case WRITE_LATENCY:
                segmentList[13] = (uint32_t)pufConfig->writeTimingConfigAdjusted.tNext |
                                  (uint32_t)pufConfig->writeTimingConfigAdjusted.tStart << 16;
                segmentList[14] = (uint32_t)pufConfig->writeTimingConfigAdjusted.tAC |
                                  (uint32_t)pufConfig->writeTimingConfigAdjusted.tAS << 16;
                segmentList[15] = (uint32_t)pufConfig->writeTimingConfigAdjusted.tAH |
                                  (uint32_t)pufConfig->writeTimingConfigAdjusted.tDS << 16;
                segmentList[16] = (uint32_t)pufConfig->writeTimingConfigAdjusted.tDH |
                                  (uint32_t)pufConfig->writeTimingConfigAdjusted.tPWD << 16;
                maxBursts = 17;
                break;
            case READ_LATENCY:
                segmentList[13] = (uint32_t)pufConfig->readTimingConfigAdjusted.tStart |
                                  (uint32_t)pufConfig->readTimingConfigAdjusted.tAS << 16;
                segmentList[14] = (uint32_t)pufConfig->readTimingConfigAdjusted.tEOD |
                                  (uint32_t)pufConfig->readTimingConfigAdjusted.tPRC << 16;
                segmentList[15] = (uint32_t)pufConfig->readTimingConfigAdjusted.tCEOEEnable |
                                  (uint32_t)pufConfig->readTimingConfigAdjusted.tCEOEDisable << 16;
                maxBursts = 16;
                break;
            case ROW_HAMMERING:
                segmentList[13] = (uint32_t)pufConfig->rowHammeringConfig.hammeringIterations |
                                  (uint32_t)pufConfig->rowHammeringConfig.hammeringDistance << 16;
                segmentList[14] = 0 | (uint32_t)pufConfig->rowHammeringConfig.tWaitBetweenHammering;
                maxBursts = 15;
                break;
            case UNKNOWN_PUF_TEST:
                break;
        }


        if (pufConfig->generalConfig.pufType == ROW_HAMMERING) {

        }
    }

    for (int i = 0; i < maxBursts; i++) {
        Xil_Out32(XPAR_PS_PL_INTERFACE_AXI_LIGHT_SLAVE_BASEADDR + i * 0x04, segmentList[i]);
        printVerilogTBConfig(i*0x04, segmentList[i]);
    }
}

/**
 * @brief Reads a frame of 32-bit values from the PS-PL interface into the provided array.
 * Typically, measurement data consisting of [address, value, checksum].
 *
 * @param values  Pointer to the array where the read values will be stored.
 * @param size    Number of 32-bit words to read.
 */
void read_data_frame(uint32_t *values, const int size) {
    for (int i = 0; i < size; i++) {
        values[i] = Xil_In32(XPAR_PSU_DDR_0_S_AXI_BASEADDR + ADDRESS_OFFSET + i * 0x04);
    }
    Xil_DCacheFlush();
}