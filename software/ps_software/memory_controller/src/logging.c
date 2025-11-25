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
#include "xil_io.h"    // For Xil_In32 etc if needed


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
    return 0;
}

#define CNTFRQ 100000000 // Use a 100 MHz clk


/**
 * @brief Reads the system timer and returns elapsed time in seconds.
 *
 * This function reads the CNTVCT_EL0 register (64-bit counter) and converts
 * ticks to seconds using the counter frequency CNTFRQ.
 *
 * @return Elapsed time in seconds since system reset.
 */
static inline double get_system_time_seconds() {
    uint64_t cntpct;
    asm volatile("mrs %0, cntpct_el0" : "=r"(cntpct));
    return ((double)cntpct) / CNTFRQ;
}

/**
 * @brief Returns the current timestamp as a string in hh:mm:ss format.
 *
 * @return Pointer to a static buffer containing the formatted timestamp.
 */
char* getCurrentTimeStamp() {
    static char buffer[16];  // hh:mm:ss
    double t = get_system_time_seconds();

    uint32_t hours   = ((uint32_t)t / 3600) % 24;
    uint32_t minutes = ((uint32_t)t / 60) % 60;
    uint32_t seconds = ((uint32_t)t) % 60;

    snprintf(buffer, sizeof(buffer), "%02u:%02u:%02u", hours, minutes, seconds);
    return buffer;
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

    xil_printf("%s [%s:%d] %s: %s\r\n", getCurrentTimeStamp(), fileName, lineNr, getLogStr(lvl), tmp_buffer);
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
void ip_settings_to_str(network_config *config, char* retStr, size_t retStrSize) {
    char tmpBuffIP[18];       // max length for IPv4
    char tmpBuffNetMask[18];
    char tmpBuffGw[18];

    ip_to_str(&config->ipaddr, tmpBuffIP);
    ip_to_str(&config->netmask, tmpBuffNetMask);
    ip_to_str(&config->gw, tmpBuffGw);

snprintf(retStr, retStrSize, "IP: %-15s Netmask: %-15s Gateway: %-15s",
         tmpBuffIP, tmpBuffNetMask, tmpBuffGw);
}