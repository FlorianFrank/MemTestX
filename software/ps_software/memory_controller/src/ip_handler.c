/**
 * @file ip_handler.c
* @brief   Implements all IP, TCP, and UDP networking functions for the application.
 *          Handles network stack initialization, board-specific network setup,
 *          client/server connections, data transmission, and PS/PL interface integration.
 * @author Florian Frank
 * @copyright University of Passau - Chair of Computer Engineering
 */

#include "ip_handler.h"

#include "config/app_config.h" // PORT, SRC_IP

#include "data_parser.h"
#include "logging.h" // log_message

#include "lwip/dhcp.h"
#include "lwip/tcp.h" // tcp_listen, tcb_new_ip_type, tcp_bind, tcp_accept
#include "lwip/udp.h" // udp_sendto, udp_pcb, udp_new_ip_type, udp_bind, udp_recv, udp_new, udp_connect
#include "lwipopts.h"
#include "lwip/ip_addr.h"
#include "lwip/err.h"
#include "lwip/inet.h"

#include "board_support/platform.h" // platform_enable_interrupts
#include "board_support/platform_config.h" // PLATFORM_EMAC_BASEADDR
#include "xparameters.h" // XPAR_XEMACPS_0_BASEADDR
#include "netif/xadapter.h" // netif_input, xemac_add
#include "irq_handler.h"
#include "receive_buffer.h"
#include <assert.h>


#define SEND_BUFFER_SIZE        256

volatile int client_connected = 0;
#define PREAMBLE                "Client Connected\n"

struct pbuf *pbuffer;
const ip_addr_t *addr_recv;


#ifdef XPS_BOARD_ZCU102
int IicPhyReset();
#ifdef XPAR_XIICPS_0_DEVICE_ID
#include "xiicps.h"
#endif
#endif

// defined in platform_zynqmp.c
// We need to call tcp_fasttmr & tcp_slowtmr at intervals specified
// by lwIP. It is not important that the timing is absolutely accurate.
extern volatile int TcpFastTmrFlag;
extern volatile int TcpSlowTmrFlag;
volatile int runRecvSendLoopEnable = 1;

void lwip_init(void);

void tcp_fasttmr(void);

void tcp_slowtmr(void);

void transfer_data();

#if SOCKET_MODE == TCP_MODE
struct tcp_pcb* tpcb_srv;
#else // SOCKET_MODE == UDP_MODE
struct udp_pcb* tpcb_srv;
#endif // SOCKET_MODE == TCP_MODE

/**
 * This function initializes the LWIP stack, allocates memory for the network
 * interface structure, adds the interface to the netif list, and sets it as the default.
 * Additionally, it enables platform interrupts and activates the network interface.
 * @param config network configuration to be returned.
 * @return 0 on success, else return -1.
 */
int initializeNetworkStack(network_config *config) {
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Initialize Network stack");
    if (!config) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "network config is null!");
        return -1;
    }


    config->echo_netif = malloc(sizeof(struct netif));
    if (!config->echo_netif) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error allocating memory for netif");
        return -1;
    }

    lwip_init();
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "LWIP stack initialized");

    /* Add network interface to the netif_list, and set it as default */
    unsigned char mac_ethernet_address[] = PHYSICAL_ADDR;
    if (!xemac_add(config->echo_netif, &config->ipaddr, &config->netmask,
                   &config->gw, mac_ethernet_address,
                   PLATFORM_EMAC_BASEADDR)) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error adding N/W interface\n\r");
        cleanupNetworkStack(config);
        return -1;
    }
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Set N/W interface");

    netif_set_default(config->echo_netif);

    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Enable Platform Interrupts");
    platform_enable_interrupts();

    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Active netif interface");
    netif_set_up(config->echo_netif);

    return 0;
}

/**
 * Sets down the network interface. Cleanup the netif interface.
 * @param config configuration to cleanup.
 */
void cleanupNetworkStack(const network_config *config) {
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Cleanup Network Stack");
    netif_set_down(config->echo_netif);
    free(config->echo_netif);
}

/**
 * @brief Initializes board-specific components required for networking.
 *
 * This function initializes components that are specific to the target board and necessary for
 * networking functionality. Depending on the architecture and presence of specific cores,
 * it may program certain PHYs (Physical Layer Devices) and perform a PHY reset if required.
 *
 * The initialization steps include:
 * - Programming Si5324 and SFP PHY if certain Gigabit Ethernet cores are present.
 * - Performing a PHY reset on the ZCU102 board if the corresponding macro is defined.
 *
 * @return 0 on successful initialization, -1 on failure.
 */

int initializeBoardSpecificComponents() {
#if defined(__arm__) && !defined(ARMR5)
#if XPAR_GIGE_PCS_PMA_SGMII_CORE_PRESENT == 1 || XPAR_GIGE_PCS_PMA_1000BASEX_CORE_PRESENT == 1
    ProgramSi5324();
    ProgramSfpPhy();
#endif
#endif
    // Define this board specific macro to perform PHY reset on ZCU102
#ifdef XPS_BOARD_ZCU102
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Perform PHY reset");
    if (IicPhyReset() != 0) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error performing PHY reset");
        return -1;
    }
#endif // XPS_BOARD_ZCU102

    return 0;
}

/**
 * Set all parameters of the Ip configuration to 0.
 * @param config configuration to be reseted.
 */
void resetIPConfig(network_config *config) {
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Reset IP config");
    config->ipaddr.addr = 0;
    config->gw.addr = 0;
    config->netmask.addr = 0;
}

/**
 * Set default network configuration, configured in app_config.h.
 * @param config handle on which the configuration is applied.
 * @return 0 on success else return -1;
 */
int setDefaultIPConfig(network_config *config) {
    if (!config) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "network config is null!");
        return -1;
    }

    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Setting default IP config");

    // Check array sizes to prevent buffer overflow
    //assert (sizeof(SRC_IP_V4) >= 4 && sizeof(NET_MASK_V4) >= 4 && sizeof(DEFAULT_GW_V4) >= 4)
    IP4_ADDR(&config->ipaddr, SRC_IP_V4[0], SRC_IP_V4[1], SRC_IP_V4[2], SRC_IP_V4[3]);
    IP4_ADDR(&config->netmask, NET_MASK_V4[0], NET_MASK_V4[1], NET_MASK_V4[2], NET_MASK_V4[3]);
    IP4_ADDR(&config->gw, DEFAULT_GW_V4[0], DEFAULT_GW_V4[1], DEFAULT_GW_V4[2], DEFAULT_GW_V4[3]);

    return 0;
}

/**
 * @brief  Callback for handling incoming UDP packets from a client.
 *         Parses the received payload, generates a response, and sends it back to the sender.
 * @param  pcb  UDP control block associated with the connection.
 * @param  p    Packet buffer containing the received data.
 * @param  addr IP address of the sender.
 * @param  port Port number of the sender.
 */
void udp_client_recv(void *, struct udp_pcb *pcb, struct pbuf *p, const ip_addr_t *addr, u16_t port) {
    client_connected = 1;
    tpcb_srv = pcb;
    addr_recv = addr;
    if (p != NULL) {
        Response *response = malloc(sizeof(Response));
        if (!response) {
            log_message(LOG_ERROR, __FILE__, __LINE__, "Error allocating memory for response");
            pbuf_free(p);
            return;  // Stop further execution
        }

        parseInputCommands(p->payload, response);

        struct pbuf *buf = pbuf_alloc(PBUF_TRANSPORT, strlen(response->responseMsg) + 1, PBUF_RAM);
        if (!buf) {
            log_message(LOG_ERROR, __FILE__, __LINE__, "Error allocating pbuf");
            free(response);
            pbuf_free(p);
            return;  // Stop further execution
        }
        memset(buf->payload, 0, strlen(response->responseMsg) + 1);
        printf("Send Response msg: %s\n", response->responseMsg);
        strncpy(buf->payload, response->responseMsg, strlen(response->responseMsg) + 1);

        err_t err = udp_sendto(pcb, buf, addr, SERVER_PORT);
        if (err != ERR_OK) {
            log_message(LOG_ERROR, __FILE__, __LINE__, "Error while udp_send %d", err);
        } else {
            // Log successful response with IP and port
            log_message(LOG_INFO, __FILE__, __LINE__,
                        "Response sent successfully to IP: %s, Port: %u",
                        ipaddr_ntoa(addr), port);
        }

        pbuf_free(buf);
        free(response);
        pbuf_free(p);
    }
}

/**
 * Callback is fired when receiving incoming TCP packages. It parses the incoming data, generates a Response objects,
 * sends the command to the PL and returns a TCP response to the sender.
 * @param arg not used!
 * @param tcp_pcb TCP handle to respond to the sender.
 * @param pbuf Buffer containing the parsed payload.
 * @param err Error in case an error occurred
 * @return
 */
err_t recv_callback(void *arg, struct tcp_pcb *tcp_pcb,
                    struct pbuf *pbuf, err_t err) {

    if(err != ERR_OK){
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Receive Callback caused an error!");
        return err;
    }

    log_message(LOG_DEBUG, _FILE_NAME_, __LINE__, "Calling receive callback function");

    /* Do not read the packet if we are not in ESTABLISHED state */
    if (!pbuf) {
        tcp_close(tcp_pcb);
        tcp_recv(tcp_pcb, NULL);
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Pbuf is zero, returning with error code");
        return ERR_OK;  // Use ERR_OK to indicate the callback was handled, but an error occurred
    }

    // Allocate memory for the response structure
    Response *response = malloc(sizeof(Response));
    if (!response) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error allocating memory for response");
        pbuf_free(pbuf);
        return ERR_MEM;  // Use ERR_MEM to indicate a memory allocation failure
    }

    /* Indicate that the packet has been received */
    tcp_recved(tcp_pcb, pbuf->len);


    if (tcp_sndbuf(tcp_pcb) > pbuf->len) {
        log_message(LOG_DEBUG, _FILE_NAME_, __LINE__, "Returning data: %s", response->responseMsg);
        err = tcp_write(tcp_pcb, response->responseMsg, strlen(response->responseMsg), 1);
    } else {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "No space in tcp_sndbuf");
        err = ERR_OK;  // Use ERR_OK to indicate the callback was handled, but an error occurred
    }

    /* Free the received pbuf */
    pbuf_free(pbuf);
    free(response);

    return err;
}

/**
 * Callback function which gets fired in case of a connection being accepted, when acting in server mode.
 * @param arg not used!
 * @param new_pcb handle of the accepted connection.
 * @param err error code.
 * @return ERR_OK when a connection is successfully accepted, otherwise return an error code.
 */
err_t accept_callback(void *arg, struct tcp_pcb *new_pcb, err_t err) {

    if(err != ERR_OK){
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Accept Callback caused an error!");
        return err;
    }

    log_message(LOG_DEBUG, _FILE_NAME_, __LINE__, "Calling accept callback function");

    static const int initial_connection = 1;
    static int connection = initial_connection;

    /* Set the receive-callback for this connection */
    tcp_recv(new_pcb, recv_callback);

    /* Use an integer number indicating the connection id as the callback argument */
    tcp_arg(new_pcb, (void *) (UINTPTR) connection);

    /* Increment for subsequent accepted connections */
    connection++;

    return ERR_OK;
}

/**
 * @brief  Initializes and starts a TCP server listening on the configured port.
 *         Sets up PCB, binds, listens, and registers the accept callback.
 * @return 0 on success, -1 on failure.
 */
int startTCPServer(){
    const unsigned port = PORT;

    /* create new TCP PCB structure */
    struct tcp_pcb *pcb = tcp_new_ip_type(IPADDR_TYPE_ANY);
    if (!pcb) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error creating PCB. Out of Memory");
        return -1;
    }

    /* bind to specified @port */
    log_message(LOG_DEBUG, _FILE_NAME_, __LINE__, "Call tcp_bind");
    err_t err = tcp_bind(pcb, IP_ANY_TYPE, port);
    if (err != ERR_OK) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Unable to bind to port %d: err = %d", port, err);
        return -1;
    }

    /* we do not need any arguments to callback functions */
    tcp_arg(pcb, NULL);

    /* listen for connections */
    log_message(LOG_DEBUG, _FILE_NAME_, __LINE__, "Call tcp_listen");
    pcb = tcp_listen(pcb);
    if (!pcb) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Out of memory while tcp_listen");
        return -1;
    }

    /* specify callback to use for incoming connections */
    tcp_accept(pcb, accept_callback);
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "TCP echo server started @ port %d\n\r", port);

    return 0;
}

/**
 * @brief  Initializes and starts a UDP server on the configured port.
 *         Allocates a PCB, binds it, and registers the reception callback.
 * @param  pcb  Pointer to the UDP PCB structure (will be initialized).
 * @return 0 on success, -1 on failure.
 */
int startUDPServer(struct udp_pcb *pcb){
    unsigned port = PORT;

    /* create new UDP PCB structure */
    pcb = udp_new_ip_type(IPADDR_TYPE_ANY);
    if (!pcb) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error creating PCB. Out of Memory");
        return -1;
    }

    /* bind to specified @port */
    log_message(LOG_DEBUG, _FILE_NAME_, __LINE__, "Call udp_bind Port %d", port);
    err_t err = udp_bind(pcb, IP_ANY_TYPE, port);
    if (err != ERR_OK) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Unable to bind to port %d: err = %d", port, err);
        return -1;
    }

    // TODO directly call receive or send
    /* Set the receive-callback for this connection */
    log_message(LOG_DEBUG, _FILE_NAME_, __LINE__, "Wait for messages to receive");
    udp_recv(pcb, udp_client_recv, NULL);
    return 0;
}


/**
 * Start the application in server mode. providing a TCP endpoint.
 * @return 0 if successful, otherwise, return -1.
 */
int startServerMode(struct udp_pcb *pcb) {
#if SOCKET_MODE == TCP_MODE
    return startTCPServer();
#else // SOCKET_MODE == UDP_MODE
    return startUDPServer(pcb);
#endif // SOCKET_MODE == TCP_MODE
}

/**
 * Close a tcp session
 * @param pcb handle corresponding to the connection to close.
 */
#if SOCKET_MODE == TCP_MODE
static void tcp_client_close(struct tcp_pcb *pcb) {
    err_t err;

    if (pcb != NULL) {
        tcp_sent(pcb, NULL);
        tcp_err(pcb, NULL);
        err = tcp_close(pcb);
        if (err != ERR_OK) {
            /* Free memory with abort */
            tcp_abort(pcb);
        }
    }
}
#endif // SOCKET_MODE == TCP_MODE


err_t tcp_sent_callback(void *arg, struct tcp_pcb *tpcb,
                             u16_t len){
    log_message(LOG_DEBUG, _FILE_NAME_, __LINE__, "tcp_sent_fn got fired");
    return ERR_OK;
}

/**
 * Callback function when application is acting in client mode. Called when a connection is established.
 * In case of a successful connection start IRQ handler, and start PS/PL interface. TODO separate concerns.
 * @param arg not used!
 * @param new_pcb handle of the connection.
 * @param err error code.
 * @return ERR_OK when a connection is successfully accepted, otherwise return an error code.
 */
#if SOCKET_MODE == TCP_MODE
static err_t tcp_client_connected(void *arg, struct tcp_pcb *tpcb, err_t err) {

    if (err != ERR_OK) {
        tcp_client_close(tpcb);
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "tcp_client_connected caused an error %x", err);
        return err;
    }

    client_connected = 1;
    log_message(LOG_DEBUG, _FILE_NAME_, __LINE__, "TCPClientConnectedCallbackFunction got fired");
    tpcb_srv = tpcb;

    tcp_sent(tpcb, tcp_sent_callback);

    char initData[SEND_BUFFER_SIZE];
    strcpy(initData, PREAMBLE);
    log_message(LOG_DEBUG, _FILE_NAME_, __LINE__, "Transmit preamble \"%s\"", initData);
    err_t ret = tcp_write(tpcb, initData, strlen(initData), 1);
    if (ret == ERR_OK) {
        // Send the data
        ret = tcp_output(tpcb);
        if(ret != ERR_OK)
            log_message(LOG_DEBUG, _FILE_NAME_, __LINE__, "Transmit TCP data", initData);

    }
    int psPlRet = initializePSPLInterconnection();
    if(psPlRet != 0){
    	log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Could not initialize PS/PL interconnection");
    	return ERR_ABRT;
    }

    log_message(LOG_DEBUG, _FILE_NAME_, __LINE__, "tcp_client_connected returned successful", err);
    return ERR_OK;
}
#endif // SERVER_MODE == TCP_MODE

/**
 * Transmits a TCP package to the connected server.
 * @param buffer string buffer to send.
 * @param len length of the message to transmit.
 */
void sendPackageToServer(char *buffer, uint32_t len) {
    if (tpcb_srv != NULL) {
        err_t err = ERR_OK;
#if SOCKET_MODE == TCP_MODE
    	err = tcp_write(tpcb_srv, buffer, len, TCP_WRITE_FLAG_COPY);
        if (err == ERR_OK) {
            // Send the data
            err_t err = tcp_output(tpcb_srv);
            if(err != ERR_OK)
                log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error while calling tcp_output %d", err);

        }else
            log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error while tcp_write %d", err);
#else // SOCKET_MODE == UDP_MODE
		pbuffer = pbuf_alloc(PBUF_TRANSPORT, len*sizeof(u8), PBUF_REF);
        pbuffer->payload = buffer;
        //err_t err = udp_sendto(tpcb_srv, p, addr, SERVER_PORT);
        if (err != ERR_OK)
            log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error while udp_write %d", err);
        pbuf_free(pbuffer);
#endif // SOCKET_MODE == TCP_MODE
	}
}

/**
 * Error handler got fired in case of a TCP error from the LWIP stack.
 * Logs the error on the console.
 * @param arg not used!
 * @param err Error code to pritn
 */
void socket_error_handler(void *arg, err_t err) {
    log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "socket_error_handler called with error code %d", err);
}


int isClientConnected() {
    return client_connected;
}

/**
 * @brief  Establishes a TCP connection to a remote client.
 *         Creates a TCP PCB, resolves the IP address, connects, and registers the error handler.
 * @param  ipAddress  IP address of the remote client as a string.
 * @param  port       Port number of the remote client.
 * @return 0 on success, -1 on failure.
 */
int connectToTCPClient(char *ipAddress, uint16_t port){
#if SOCKET_MODE == TCP_MODE
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Establish connection to client %s:%d",  ipAddress, port);
    err_t err;
    struct tcp_pcb *pcb;
    ip_addr_t remote_addr;

#if LWIP_IPV6 == 1
    remote_addr.type= IPADDR_TYPE_V6;
    err = inet6_aton(TCP_SERVER_IPV6_ADDRESS, &remote_addr);
#else
    err = inet_aton(ipAddress, &remote_addr);
#endif /* LWIP_IPV6 */
    if (err == 0) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Failed to convert IP address: %s", ipAddress);
        return -1;
    }

    /* Create Client PCB */
    pcb = tcp_new_ip_type(IPADDR_TYPE_ANY);
    if (!pcb) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error while calling tcp_new_ip_type");
        return -1;
    }


    err = tcp_connect(pcb, &remote_addr, port,
                      tcp_client_connected);
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Register TCP error handler");
    tcp_err(pcb, socket_error_handler);

    if (err) {
        log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Error %d on TCP connect. -> Close connection", err);
        tcp_client_close(pcb);
        return -1;
    }
#endif // SERVER_MODE == TCP_MODE
    return 0;
}

/**
 * @brief  Establishes a UDP connection to a remote client.
 *         Creates a UDP PCB, resolves the IP address, binds, connects, and initializes the IRQ handler.
 * @param  ipAddress  IP address of the remote client as a string.
 * @param  port       Port number of the remote client.
 * @return 0 on success, -1 on failure.
 */
int connectToUDPClient(char *ipAddress, uint16_t port){
#if SOCKET_MODE == UDP_MODE
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Establish connection to client %s:%d",  ipAddress, port);
    err_t err;
    struct udp_pcb *pcb;
    ip_addr_t remote_addr;

#if LWIP_IPV6 == 1
    remote_addr.type= IPADDR_TYPE_V6;
    err = inet6_aton(TCP_SERVER_IPV6_ADDRESS, &remote_addr);
#else
    err = inet_aton(ipAddress, &remote_addr);
#endif /* LWIP_IPV6 */

    if (!err) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "inet_aton caused an error %d wile transforming the IP%s",  err, ipAddress);
        return -1;
    }

    /* Create Client PCB */
    pcb = udp_new();
    if (!pcb) {
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error while calling udp_new_ip_type");
        return -1;
    }

	err = udp_bind(pcb, IP_ADDR_ANY, port);
    if(err != ERR_OK){
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "udp_bind returned with error code %d", err);
        return -1;
    }

    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Call udp_connect");
    err = udp_connect(pcb, &remote_addr, port);
    if(err != ERR_OK){
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error while calling udp_connect %d", err);
    	return -1;
    }
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Connection established");
    tpcb_srv = pcb;
    client_connected = 1;
    initializeIRQHandler(pcb);

    char initData[SEND_BUFFER_SIZE];
    strcpy(initData, PREAMBLE);
    pbuf_free(pbuffer);
    sendPackageToServer(initData, strlen(initData));
#endif // SERVER_MODE == UDP_MODE
    return 0;
}

/**
 * Establish a TCP connection to a server, identified by its IP and port.
 * @param ipAddress address of the server.
 * @param port port of the connection.
 * @return 0 if no error occurred, otherwise return -1.
 */
int connectToClient(char *ipAddress, uint16_t port) {
#if SOCKET_MODE == TCP_MODE
    return connectToTCPClient(ipAddress, port);
#else // SOCKET_MODE == UDP_MODE
    return connectToUDPClient(ipAddress, port);
#endif // SOCKET_MODE == TCP_MODE
}

/* Create a new DHCP client for this interface.
 * Note: you must call dhcp_fine_tmr() and dhcp_coarse_tmr() at
 * the predefined regular intervals after starting the client.
 */
int startDHCPService(network_config *config) {
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Start DHCP Service with timeout ctr %d", DHCP_TIMEOUT_CTR);
    dhcp_start(config->echo_netif);

    while (((config->echo_netif->ip_addr.addr) == 0) != 0)
        xemacif_input(config->echo_netif);

    config->ipaddr.addr = config->echo_netif->ip_addr.addr;
    config->gw.addr = config->echo_netif->gw.addr;
    config->netmask.addr = config->echo_netif->netmask.addr;

    char ipSettingsBuf[512];
    ip_settings_to_str(config, ipSettingsBuf, sizeof(ipSettingsBuf));
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Set IP settings \n%s", ipSettingsBuf);
    return 0;
}

/**
 * Pops elements from the PS/PL receive buffer and sends them to the connected server.
 * @note Multiple messages should be combined to avoid I/O overhead. Currently not implemented!
 */
int ctr = 0;
void readAXIAndSendResponse() {
    BufferElement bufferElement = {0,ctr,2,3};
    if (isClientConnected() == 0) {
      //  log_message(LOG_WARNING, _FILE_NAME_, __LINE__, "Wait for client connection");
    } else {
    	ctr ++;
       if (popElementFromRecvBuffer(&bufferElement) == 1) {

            char buffer[SEND_BUFFER_SIZE];
            // read multiple buffer elements and transform them into a single TCP message
            // This decreases the overhead by I/O operations.
            int len = sprintf(buffer, "{\"msg_type\": \"m\", \"data\": [%d, %d, %d, %d]}", bufferElement.preamble,
                              bufferElement.address,
                              bufferElement.value, bufferElement.checksum);
            sendPackageToServer(buffer, len);
        }
    }
}

/**
 * TCP receive and transmit loop. Reacts on incoming connections, and send data to the client in case of data available in the
 * PS/PL recv buffer.
 * @param config configuration of the network stack to handle.
 */
void runRecvSendLoop(const network_config *config) {
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Ready to receive and send messages...");
    /* receive and process packets */
    while (runRecvSendLoopEnable) {
        if (TcpFastTmrFlag) {
            tcp_fasttmr();
            TcpFastTmrFlag = 0;
        }
        if (TcpSlowTmrFlag) {
            tcp_slowtmr();
            TcpSlowTmrFlag = 0;
        }
        xemacif_input(config->echo_netif);
        readAXIAndSendResponse();

    }
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Run exit send/receive loop");
}
