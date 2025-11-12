/**
 * @file    app_config.h
* @brief   Global configurations of this application, including network settings,
 *          modes of operation, and additional flags.
 * @author  Florian Frank
 * @affiliation University of Passau
 * @date    2025
 */

#ifndef _APP_CONFIG_
#define _APP_CONFIG_

#define ENABLE              1
#define TCP_MODE            1
#define UDP_MODE            2

#define LOG_BUFFER_LEN 		   512
#define LOG_BUFFER_LEN_ADD	 256

// Network Configurations
extern int SRC_IP_V4[4];
extern int NET_MASK_V4[4];
extern int DEFAULT_GW_V4[4];
#define PORT 			             5024
#define PHYSICAL_ADDR        { 0x00, 0x0a, 0x35, 0x00, 0x01, 0x02 }

#define DHCP_TIMEOUT_CTR     24

#define SOCKET_MODE          UDP_MODE
#define SERVER_MODE		        ENABLE
#define CLIENT_MODE 	        DISABLE

#define SERVER_IP_ADDRESS    "132.231.14.108"
#define SERVER_PORT          5023

#endif // _APP_CONFIG_
