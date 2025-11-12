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
