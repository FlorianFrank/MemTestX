/**
 * @file irq_handler.c
 * @brief Implementation of an interrupt handler to react on notifications of incoming data from the PL.
 * @author Florian Frank
 * @copyright University of Passau - Chair of Computer Engineering
 */

#include "irq_handler.h"
#include "xil_types.h"
#include <xparameters.h>

#include "axi_protocol.h"

#include "logging.h" // log_message
#include "receive_buffer.h"
#include "config/app_config.h"
#include "lwip/udp.h" // udp_pcb

static XScuGic_Config *intr_cfg;

XScuGic *intr_ctrl;

#define INTC_DEVICE_ID        XPAR_SCUGIC_0_DEVICE_ID


s32 User_XScuGic_CfgInitialize(XScuGic *InstancePtr,
                               XScuGic_Config *ConfigPtr,
                               u32 EffectiveAddr) {
    u32 Int_Id;
    (void) EffectiveAddr;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(ConfigPtr != NULL);

    if (InstancePtr->IsReady != XIL_COMPONENT_IS_READY) {
        InstancePtr->IsReady = 0U;
        InstancePtr->Config = ConfigPtr;

        InstancePtr->IsReady = XIL_COMPONENT_IS_READY;
    }

    return XST_SUCCESS;
}


//There are 32 priority levels supported with a step of 8. Hence the supported priorities are 0, 8, 16, 32, 40 ..., 248.
// 0 is the highest priory
#define PRIORITY_LVL    0x0A

// . Each bit pair describes the configuration for an INT_ID. SFI Read Only b10 always PPI Read Only depending on
// how the PPIs are configured. b01 Active HIGH level sensitive b11 Rising edge sensitive SPI LSB is read only. b01 Active HIGH level sensitive
// b11 Rising edge sensitive
// Our interrupt is rising edge sensitive
#define TRIGGER_TYPE    0x03

char *buffer[128];
struct udp_pcb *pcb_buf;
uint32_t maxAddr = 0;


int initializeIRQHandler(struct udp_pcb *pcb) {
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Start initialize IRQ Handler");
    pcb_buf = udp_new();
    // TODO free in the end
    intr_ctrl = malloc(sizeof(XScuGic));

    intr_cfg = XScuGic_LookupConfig(INTC_DEVICE_ID);
    if (NULL == intr_cfg) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "XScuGic_LookupConfig returned null -> return XST_FAILURE");
        return XST_FAILURE;
    }

    s32 status = User_XScuGic_CfgInitialize(intr_ctrl, intr_cfg, intr_cfg->CpuBaseAddress);
    if (status != XST_SUCCESS) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__,
                    "XScuGic_CfgInitialize returned with error code %x -> return XST_FAILURE", status);
        return XST_FAILURE;
    }

    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Set interrupt with priority ");
    XScuGic_SetPriorityTriggerType(intr_ctrl, INTC_INTERRUPT_ID, PRIORITY_LVL, TRIGGER_TYPE);

    // This handler is being called when the processor encounters the specified exception.
    Xil_ExceptionRegisterHandler(INTC_INTERRUPT_ID, (Xil_ExceptionHandler) XScuGic_InterruptHandler, intr_ctrl);

    status = XScuGic_Connect(intr_ctrl, INTC_INTERRUPT_ID, (Xil_InterruptHandler) plMessageReceiveInterruptHandler,
                             pcb);
    if (status != XST_SUCCESS) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__,
                    "XScuGic_Connect returned with error code %x -> return XST_FAILURE", status);
        return XST_FAILURE;
    }

    XScuGic_Enable(intr_ctrl, INTC_INTERRUPT_ID);
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Interrupt with ID %x enabled", INTC_INTERRUPT_ID);

    return XST_SUCCESS;
}


void deInitializeIRQHandler() {
    // TODO to be implemented
}

/**
 * Interrupt handler is fired when a rising edge from the axi_light_master_txn_done signal on the PL is received.
 * It disables the interrupt while storing the data within the receive buffer.
 * @param CallbackRef Currently not used.
 */
void disableInterrupt() {
    XScuGic_Disable(intr_ctrl, INTC_INTERRUPT_ID);
}

void enableInterrupt() {
    XScuGic_Enable(intr_ctrl, INTC_INTERRUPT_ID);
}

bool getDestinationIP(ip_addr_t *dest_ip) {
    if (!ipaddr_aton("132.231.14.93", dest_ip)) { // TODO save IP from which request was received
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "ERROR WHILE CALLING IPADDR_ATON");
        return false;
    }
    return true;
}

void sendUDPMessage(const char *message, ip_addr_t *dest_ip) {
    struct pbuf *p = pbuf_alloc(PBUF_TRANSPORT, strlen(message), PBUF_RAM);
    if (p == NULL) {
        printf("Error: Could not allocate pbuf\n");
        return;
    }

    memcpy(p->payload, message, strlen(message));
    //printf("Sending UDP message: %s -> dest\n", message);
    err_t err = udp_sendto(pcb_buf, p, dest_ip, SERVER_PORT);

    if (err != ERR_OK) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error while calling sendto %d", err);
    } else {
        //log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Successfully sent to server");
    }

    pbuf_free(p);
}

void processReceivedData(uint32_t *buf) {
    char buffer[128];
    ip_addr_t dest_ip;

    if (!getDestinationIP(&dest_ip)) return;

    snprintf(buffer, sizeof(buffer),
             "{\"msg_type\": \"m\", \"d\": [[%d,%d,%d]]}", buf[1], buf[2], buf[1] + buf[2]);
    sendUDPMessage(buffer, &dest_ip);

    if (buf[1] >= maxAddr) {
        snprintf(buffer, sizeof(buffer),
                 "{\"msg_type\": \"response\", \"cmd\": \"start_measurement\", \"cmd_status\": \"ready\"}");
        sendUDPMessage(buffer, &dest_ip);
        log_message(LOG_WARNING, _FILE_NAME_, __LINE__, "Maximum address 0x%x is reached", maxAddr);
    }
}

void plMessageReceiveInterruptHandler(void *CallbackRef) {
    //disableInterrupt();

    uint32_t buf[4];
    read_data_frame(buf, 4);
    processReceivedData(buf);

    //enableInterrupt();
}

