/**
 * @file data_parser.c
 * @brief Implementation of all functions to identify commands in data received from the network adapter, received the scheduler,
 * parse the payload and execute the corresponding actions.
 * @author Florian Frank
 * @affiliation University of Passau
 */

#include "data_parser.h"
#include "logging.h"
#include "json_parser.h"
#include "axi_protocol.h"

#include <string.h>

// Identification string in order to identify and detect the board in the network
#define IDN_STR "Zync Ultrascale+ MPSoC ZCU102 Evaluation Kit"

/**
 * @brief Finds the next occurrence of a target substring in a string.
 *
 * @param str     Input string to search.
 * @param target  Substring to find.
 * @return Pointer to the character immediately after the found substring,
 *         or NULL if not found.
 */
const char *find_next(const char *str, const char *target) {
    const char *result = strstr(str, target);
    return result ? result + strlen(target) : NULL;
}

/**
 * @brief Parses input commands received over the network in JSON format,
 *        executes the corresponding actions, and fills the response structure.
 *
 * @param input_command  JSON string containing the command and parameters.
 * @param response       Pointer to the Response structure to populate.
 */
void parseInputCommands(const char *input_command, Response *response) {
    PUFConfiguration config;
    parse_json(input_command, &config);
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Send response");
    // Clear response message buffer
    memset(response->responseMsg, 0, MAX_RESPONSE_SIZE);

    createAXISegments(&config);
    // Set the response command and status
    response->command = config.generalConfig.command;
    if (response->command == CMD_START_MEASUREMENT)
        response->status = PROCESSING;

    // Log the command
    log_message(LOG_INFO, __FILE__, __LINE__, "Command is %s", cmdToStr(response->command));

    // Begin building the common response JSON structure
    int offset = snprintf(response->responseMsg, MAX_RESPONSE_SIZE,
                          "{\"msg_type\": \"response\", \"cmd\": \"%s\", \"cmd_status\": \"%s\"",
                          cmdToStr(response->command), statusToString(response->status));

    if (offset < 0 || offset >= MAX_RESPONSE_SIZE) {
        log_message(LOG_ERROR, __FILE__, __LINE__, "Error formatting response");
        return;
    }

    // Add command-specific fields
    switch (response->command) {
        case CMD_IDN:
            snprintf(response->responseMsg + offset, MAX_RESPONSE_SIZE - offset, ", \"idn\": \"%s\"}", IDN_STR);
            break;

        case CMD_START_MEASUREMENT:
        case CMD_STOP_MEASUREMENT:
            snprintf(response->responseMsg + offset, MAX_RESPONSE_SIZE - offset, "}");
            break;

        case CMD_RETRIEVE_STATUS:
            snprintf(response->responseMsg + offset, MAX_RESPONSE_SIZE - offset, ", \"status\": \"%s\"}", cmdToStr(response->status));
            break;

        case CMD_RESET:
            snprintf(response->responseMsg + offset, MAX_RESPONSE_SIZE - offset, "}");
            break;

        default:
            log_message(LOG_ERROR, __FILE__, __LINE__, "Unknown command");
            snprintf(response->responseMsg + offset, MAX_RESPONSE_SIZE - offset, ", \"error\": \"Unknown command\"}");
            break;
    }
    log_message(LOG_DEBUG, __FILE__, __LINE__, "Response: %s", response->responseMsg);
}
