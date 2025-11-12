/**
* @file    json_parser.h
 * @brief   Provides JSON parsing utilities for PUF configurations.
 *          Implements parsing of commands, PUF types, timing parameters, and row
 *          hammering configurations from JSON input strings into structured
 *          PUFConfiguration objects. Also provides helper functions for string
 *          manipulation and configuration printing for debugging purposes.
 *
 *          This file especially contains all the definitions required for parsing the configurations.
 *
 * @author  Florian Frank
 * @affiliation University of Passau
 * @date    2025
 */


#pragma once
#include <stdbool.h> // bool
#include <stdint.h> // uint32_t

#define MAX_RESPONSE_SIZE 128

/**
 * @enum Status
 * @brief Represents the current status of a PUF measurement or command execution.
 */
typedef enum Status {
    STATUS_OK = 0x00,
    PROCESSING = 0x01,
    READY = 0x02,
    ERROR = 0x03,
} Status;

/**
 * @enum DataType
 * @brief Defines the type of data associated with a JSON token.
 */
typedef enum DataType {
    INTEGER,
    BOOLEAN,
    STRING
} DataType;


/**
 * @enum PUFType
 * @brief Enumerates supported PUF test types.
 */
typedef enum PUFType {
    RELIABLE = 0,
    WRITE_LATENCY = 1,
    READ_LATENCY = 2,
    ROW_HAMMERING = 3,
    UNKNOWN_PUF_TEST = 4
} PUFType;

/**
 * @enum Cmd
 * @brief Lists supported commands for the PUF controller.
 */
typedef enum Cmd {
    CMD_IDN = 0x00,
    CMD_START_MEASUREMENT = 0x01,
    CMD_STOP_MEASUREMENT = 0x02,
    CMD_RETRIEVE_STATUS = 0x03,
    CMD_RESET = 0x04,
    CMD_UNDEFINED = 0x05
} Cmd;

/**
 * @struct Response
 * @brief Structure to store responses from the PUF controller.
 */
typedef struct Response {
    Cmd command;
    Status status;
    char responseMsg[MAX_RESPONSE_SIZE];
} Response;

/**
 * @struct GeneralConfig
 * @brief Contains general configuration parameters for a PUF test.
 */
typedef struct GeneralConfig {
    Cmd command;
    PUFType pufType;
    uint32_t initValue;
    uint32_t pufValue;
    uint32_t startAddress;
    uint32_t endAddress;
    uint16_t tWaitAfterInit;
    uint16_t tNextRead;
    bool ceDrivenWrite;
    bool ceDrivenRead;
} GeneralConfig;

/**
 * @struct WriteTimingConfig
 * @brief Stores write timing parameters for PUF memory operations.
 */
typedef struct WriteTimingConfig {
    uint16_t tStart;
    uint16_t tNext;
    uint16_t tAC;
    uint16_t tAS;
    uint16_t tAH;
    uint16_t tPWD;
    uint16_t tDS;
    uint16_t tDH;
} WriteTimingConfig;

/**
 * @struct ReadTimingConfig
 * @brief Stores read timing parameters for PUF memory operations.
 */
typedef struct ReadTimingConfig {
    uint16_t tStart;
    uint16_t tAS;
    uint16_t tAH;
    uint16_t tEOD;
    uint16_t tPRC;
    uint16_t tCEOEEnable;
    uint16_t tCEOEDisable;
} ReadTimingConfig;

/**
 * @struct RowHammeringConfig
 * @brief Configuration parameters for row hammering tests.
 */
typedef struct RowHammeringConfig {
    uint16_t tWaitBetweenHammering;
    uint16_t hammeringIterations;
    uint16_t hammeringDistance;
}RowHammeringConfig;


typedef enum TokenType {
    COMMAND,
    PUF_TYPE,
    INIT_VALUE,
    PUF_VALUE,
    START_ADDR,
    STOP_ADDR,
    CE_DRIVEN,

    T_WAIT_AFTER_INIT,
    T_NEXT_READ,
    T_START_DEFAULT,
    T_NEXT_WRITE_DEFAULT,
    T_AC_DEFAULT,
    T_AS_DEFAULT,
    T_AH_DEFAULT,
    T_PWD_DEFAULT,
    T_DS_DEFAULT,
    T_DH_DEFAULT,

    T_START_ADJUSTED,
    T_NEXT_WRITE_ADJUSTED,
    T_AC_ADJUSTED,
    T_AS_ADJUSTED,
    T_AH_ADJUSTED,
    T_PWD_ADJUSTED,
    T_DS_ADJUSTED,
    T_DH_ADJUSTED,

    CE_DRIVEN_READ,
    T_START_READ_DEFAULT,
    T_AS_READ_DEFAULT,
    T_AH_READ_DEFAULT,
    T_OED_DEFAULT,
    T_PRC_DEFAULT,
    T_CE_OE_ENABLE_DEFAULT,
    T_CE_OE_DISABLE_DEFAULT,

    T_START_READ_ADJUSTED,
    T_AS_READ_ADJUSTED,
    T_AH_READ_ADJUSTED,
    T_OED_ADJUSTED,
    T_PRC_ADJUSTED,
    T_CE_OE_ENABLE_ADJUSTED,
    T_CE_OE_DISABLE_ADJUSTED,

    T_WAIT_BETWEEN_HAMMERING,
    HAMMERING_ITERATIONS,
    HAMMERING_DISTANCE,
} TokenType;


/*
 * @struct Token
 * @brief Represents a JSON token with its type and expected data type.
 */
typedef struct Token {
    TokenType tokenIDN;
    const char *token;
    DataType dataType;
} Token;

/**
 * @struct PUFConfiguration
 * @brief Complete configuration structure for a PUF test.
 */
typedef struct PUFConfiguration {
    GeneralConfig generalConfig;
    WriteTimingConfig writeTimingConfigDefault;
    WriteTimingConfig writeTimingConfigAdjusted;
    ReadTimingConfig readTimingConfigDefault;
    ReadTimingConfig readTimingConfigAdjusted;
    RowHammeringConfig rowHammeringConfig;
} PUFConfiguration;

char* statusToString(Status status);
char* cmdToStr(Cmd cmd);
Cmd parseCmd(char *str);
void parse_json(const char *inputBuffer, PUFConfiguration* config);