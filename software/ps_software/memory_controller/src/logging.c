/**
 * @file logging.c
 * @brief Implementation of all logging-related functionalities.
 * @author Florian Frank
 * @affiliation University of Passau - Chair of Computer Engineering
 */

#include "logging.h"
#include <stdarg.h>
#include "config/app_config.h"
#include "malloc.h"
#include <xil_printf.h>
#include "ip_handler.h"

#include <time.h>

char *log_buffer;

volatile int global_log_lvl;

/**
 * @brief Initializes the logging system.
 * @param lvl The global logging level.
 * @return 0 on success, -1 if memory allocation fails.
 */
int initialize_logging(log_lvl lvl) {
    global_log_lvl = lvl;

    log_buffer = malloc(LOG_BUFFER_LEN * LOG_BUFFER_LEN_ADD * sizeof(char));
    if (log_buffer == NULL) {
        log_message(LOG_ERROR, __FILE__, __LINE__, "malloc returned NULL!");
        return -1;
    }

    return 0;
}

char* getCurrentTimeStamp(){
    // TODO
    return "00:00:00";
}

/*
 * @brief Deinitializes the logging system and frees allocated resources.
 */
void deinitialize_logging() {
    free(log_buffer);
}

/**
 * @brief Returns a string representation of the log level.
 * @param lvl The log level.
 * @return A string corresponding to the log level.
 */
const char *getLogStr(log_lvl lvl) {
    if (lvl == LOG_DEBUG) return "Debug";
    if (lvl == LOG_INFO) return "Info";
    if (lvl == LOG_WARNING) return "Warning";
    if (lvl == LOG_ERROR) return "Error";
    return "Undefined";
}

/**
 * @brief Logs a formatted message with file and line information.
 * @param lvl The log level of the message.
 * @param fileName The name of the source file.
 * @param lineNr The line number in the source file.
 * @param msg The message format string.
 */
void log_message(log_lvl lvl, char* fileName, int lineNr, char *msg, ...) {
    if (lvl < global_log_lvl)
        return;

    va_list args;
    va_start(args, msg);
    char tmp_buffer[LOG_BUFFER_LEN];
    vsprintf(tmp_buffer, msg, args);
    va_end(args);

    xil_printf("%d [%s:%d] %s: %s \r\n", getCurrentTimeStamp(), fileName, lineNr, getLogStr(lvl), tmp_buffer);
}

/**
 * @brief Converts an IP address to a human-readable string.
 * @param ip Pointer to the IP address structure.
 * @param retStr Buffer to store the resulting string.
 */
void ip_to_str(const ip_addr_t *ip, char* retStr) {
    if(retStr && ip)
        sprintf(retStr, "%d.%d.%d.%d\n\r", ip4_addr1(ip), ip4_addr2(ip),
                   ip4_addr3(ip), ip4_addr4(ip));
    else
        log_message(LOG_ERROR, _FILE_NAME_, __LINE__, "Error IP or strBuf is null!");
}

/**
 * @brief Converts network configuration (IP, netmask, gateway) to a string.
 * @param config Pointer to the network configuration structure.
 * @param retStr Buffer to store the resulting string.
 */
void ip_settings_to_str(network_config *config, char* retStr) {
    char tmpBuffIP[18]; // max length of an IPV4 address or mask e.g. 192.168.178.125
    char tmpBuffNetMask[18];
    char tmpBuffGw[18];

    ip_to_str(&config->ipaddr, tmpBuffIP);
    ip_to_str(&config->netmask, tmpBuffNetMask);
    ip_to_str(&config->gw, tmpBuffGw);

    sprintf(retStr, "\nIP: %s Netmask: %s Gateway: %s\n", tmpBuffIP, tmpBuffNetMask, tmpBuffGw);
}
