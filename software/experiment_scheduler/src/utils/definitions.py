from enum import Enum


class InterfaceEnum(Enum):
    """
    Enumeration for supported communication interfaces.
    """
    SERIAL_IF = 1
    ETH_IF = 2


class Command(Enum):
    """
    Enumeration for supported device commands.
    """
    CMD_IDN = 0x00
    CMD_START_MEASUREMENT = 0x01
    CMD_STOP_MEASUREMENT = 0x02
    CMD_RETRIEVE_STATUS = 0x03
    CMD_RESET = 0x04
    CMD_UNDEFINED = 0x05


# ============================
# Command Helper
# ============================
def cmd_to_str(cmd: Command) -> str:
    """
    Convert a Command enum to its corresponding string representation.

    Args:
        cmd (Command): The command to be converted.

    Returns:
        str: The string representation of the command.
    """
    command_map = {
        Command.CMD_IDN: "idn",
        Command.CMD_START_MEASUREMENT: "start_measurement",
        Command.CMD_STOP_MEASUREMENT: "stop_measurement",
        Command.CMD_RETRIEVE_STATUS: "status",
        Command.CMD_RESET: "reset",
    }
    return command_map.get(cmd, "undefined")


DB_NAME = "memories.db"

# Network Configuration (e.g. to the ZCU102)
PORT_SEND = 5024
PORT_RECV = 5023
NIC_SUFFIX = "132.231.14"
SCHEDULER_IP = "132.231.14.106"

NETWORK_MAX_RECV_BUF_LEN = 4096  # Maximum length for received buffers (ethernet)
NETWORK_TIMEOUT_RESPONSE = 500.0  # Timeout for receiving a response (in seconds)
NETWORK_TIMEOUT_WRITE_FINISH = 10  # Timeout for write completion (in seconds)

# Measurement File Parsing Configuration
MEASURE_FILE_DELIMITER = ';'  # Delimiter used in measurement files
MEASURE_FILE_QUOTE_CHAR = '"'  # Quote character for measurement files

SCHEDULER_THREAD_TIMEOUT_IN_S = 10
TIME_BETWEEN_TESTS_IN_MS = 200
DEFAULT_PATH = 'output_results'