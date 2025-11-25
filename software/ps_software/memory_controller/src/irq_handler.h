/**
* @file    json_parser.c
 * @brief   Provides JSON parsing utilities for PUF configurations.
 *          Implements parsing of commands, PUF types, timing parameters, and row
 *          hammering configurations from JSON input strings into structured
 *          PUFConfiguration objects. Also provides helper functions for string
 *          manipulation and configuration printing for debugging purposes.
 *
 * @author  Florian Frank
 * @affiliation University of Passau
 * @date    2025
 */

#ifndef _IRQ_HANDLER_H_
#define _IRQ_HANDLER_H_

#include "xscugic.h"
struct udp_pcb;

#define INTC_INTERRUPT_ID    XPS_FPGA0_INT_ID

extern XScuGic *intr_ctrl;
extern uint32_t maxAddr;

int initializeIRQHandler(struct udp_pcb *pcb);
void deInitializeIRQHandler();
void plMessageReceiveInterruptHandler (void *CallbackRef);

#endif // _IRQ_HANDLER_H_
