/**
* @file    axi_protocol.h
 * @brief   Implements the interface between the PS and PL using AXI Lite.
 *          Provides the protocol to configure PUF-based tests and
 *          receives and decodes measured data from the interface.
 *
 * @author  Florian Frank
 * @affiliation University of Passau
 * @date    2025
 */

#pragma once

#include "json_parser.h"

void printVerilogTBConfig(int idx, uint32_t value);
void createAXISegments(const PUFConfiguration *pufConfig);
void read_data_frame(uint32_t *values, int size);