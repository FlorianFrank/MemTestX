/**
 * @file logging.h
 * @brief Implementation of all logging-related functionalities.
 * @author Florian Frank
 * @affiliation University of Passau - Chair of Computer Engineering
 */

#ifndef _LOGGING_
#define _LOGGING_

#include "lwip/dhcp.h"
#include <string.h>
#include "ip_handler.h"

typedef int log_lvl;

/** Definition of logging levels **/
#define LOG_DEBUG 	 0
#define LOG_INFO  	 1
#define LOG_WARNING  2
#define LOG_ERROR 	 3

#define _FILE_NAME_ (strrchr(__FILE__, '/') ? strrchr(__FILE__, '/') + 1 : __FILE__)

int initialize_logging(log_lvl lvl);
void deinitialize_logging();

void log_message(log_lvl lvl, char* fileName, int lineNr, char *msg, ...);

void ip_to_str(const ip_addr_t *ip, char* retStr);
void ip_settings_to_str(network_config *config, char* retStr);

#endif // _LOGGING_
