/**
* @file ip_handler.h
* @brief   Implements all IP, TCP, and UDP networking functions for the application.
 *          Handles network stack initialization, board-specific network setup,
 *          client/server connections, data transmission, and PS/PL interface integration.
 * @author Florian Frank
 * @copyright University of Passau - Chair of Computer Engineering
 */

#ifndef _IP_HANDLER_
#define _IP_HANDLER_

#include "lwip/dhcp.h"

struct network_config {
	struct netif *echo_netif;
	ip_addr_t ipaddr, netmask, gw;

} typedef network_config;


int initializeNetworkStack(network_config *config);
void cleanupNetworkStack(const network_config *config);
int initializeBoardSpecificComponents();

int setDefaultIPConfig(network_config *config);
void resetIPConfig(network_config *config);
int startDHCPService(network_config *config);
int startServerMode(struct udp_pcb *pcb);
int connectToClient(char* ipAddress, uint16_t port);
void sendPackageToServer(char *buffer, uint32_t len);
int isClientConnected();
void runRecvSendLoop(const network_config *config);

#endif // _IP_HANDLER_
