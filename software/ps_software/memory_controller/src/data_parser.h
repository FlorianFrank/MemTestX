/**
 * @file data_parser.h
 * @brief Implementation of all functions to identify commands in data received from the network adapter, received the scheduler,
 * parse the payload and execute the corresponding actions.
 * @author Florian Frank
 * @affiliation University of Passau
 */

#ifndef _TCP_DATA_PARSER_
#define _TCP_DATA_PARSER_
#include "json_parser.h"

void parseInputCommands(const char* command, Response* response);
#endif // _TCP_DATA_PARSER_
