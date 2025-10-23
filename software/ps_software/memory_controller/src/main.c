/**
 * @file main.c
 * @brief Application entry point
 * @author Florian Frank
 * @affiliation University of Passau - Chair of Computer Engineering
 */
 

	


#include "config/app_config.h"
#include "irq_handler.h" // deInitializeIRQHandler
#include "receive_buffer.h"
#include "logging.h"
#include "ip_handler.h"

#include "board_support/platform.h" // init_platform, cleanup_platform
#include "sleep.h"

extern void sleep(uint32_t seconds) {
    sleep_A53(seconds);
}


/** Handle holding the network configuration. */
network_config net_config;

int initialize();
void cleanup();
int logAndExitProgram();
int startNetworkConfig();

void print(const char *msg) {
    xil_printf("%s", msg); // Redirects to standard output
}


int main() {

    struct udp_pcb *pcb = NULL;
    if (initialize() != 0)
        return logAndExitProgram();

    initializeIRQHandler(pcb);

    if (startNetworkConfig() != 0)
        return logAndExitProgram();

    if (initializeBuffer() != 0)
        return logAndExitProgram();

#if SERVER_MODE
    if (startServerMode(pcb) != 0)
        return logAndExitProgram();
#endif // SERVER_MODE

#if CLIENT_MODE
    if (connectToClient(SERVER_IP_ADDRESS, SERVER_PORT) != 0)
        return logAndExitProgram();
#endif // CLIENT MODE

    runRecvSendLoop(&net_config);

    cleanup();

    return 0;
}

/**
 * This function initializes the logging, board specific components, like the ethernet PHY and
 * initializes the lwip network stack
 * @return 0 if no error occurred, else return -1.
 */
int initialize() {
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Call initialize");


    if (initialize_logging(LOG_DEBUG) != 0) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error while calling initialize_logging()");
        return -1;
    }

    resetIPConfig(&net_config);

    if (initializeBoardSpecificComponents() != 0) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error while calling initializeBoardSpecificComponents()");
        return -1;
    }

    init_platform();

    if (initializeNetworkStack(&net_config) != 0) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error while calling initializeNetworkStack()");
        return -1;
    }

    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Initialization finished");
    return 0;
}

/**
 * Cleanup the platform, e.g. free all logging buffers, de-initializes the network stack, clears all buffers
 * and de-registers the interrupt handler.
 */
void cleanup() {
    deinitialize_logging();
    cleanupNetworkStack(&net_config);
    cleanup_platform();
    deInitializeBuffer();
    deInitializeIRQHandler();
}

/**
 * Helper function logs the program exit, cleanup the platform.
 * @return always return with 0.
 */
int logAndExitProgram() {
    log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Exit Program");
    cleanup();
    return 0;
}

/**
 * Helper function starts the network config. Either set a local ip if LWIP_DHCP is not defined.
 * Otherwise start the DHCP cleint.
 * @return 0 if no error occurred, else return -1.
 */
int startNetworkConfig() {
#if (LWIP_DHCP == 1)
    if(startDHCPService(&net_config) != 0){
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Start DHCP client caused an error!");
        return -1;
    }
#else
    setDefaultIPConfig(&net_config);
#endif
    return 0;
}
