from enum import IntEnum


class CustomEnum(IntEnum):
    def __str__(self):
        return self.name.lower()


class DeviceStatus(CustomEnum):
    """Enumeration for device status."""
    ONLINE = 1
    OFFLINE = 2


class DeviceType(CustomEnum):
    """Enumeration for device types."""
    SMU = 1
    OSCILLOSCOPE = 2
    DC_POWER_SUPPLY = 3
    SIGNAL_GENERATOR = 4
    SWITCH_MATRIX = 5
    CLIMATE_CHAMBER = 6
    NANOSEC_CONTAINER = 7
    GENERAL_CONTAINER = 8
    FPGA = 9
    MEMORY_CONTROLLER = 10
    OTHER = 11


# Dictionary mapping string identifiers to DeviceType enum values
DEVICE_TYPE_MAP = {
    'SMU': DeviceType.SMU,
    'OSCILLOSCOPE': DeviceType.OSCILLOSCOPE,
    'DC_POWERSUPPLY': DeviceType.DC_POWER_SUPPLY,
    'SIGNAL_GENERATOR': DeviceType.SIGNAL_GENERATOR,
    'SWITCH_MATRIX': DeviceType.SWITCH_MATRIX,
    'CLIMATE_CHAMBER': DeviceType.CLIMATE_CHAMBER,
    'NANOSEC_CONTAINER': DeviceType.NANOSEC_CONTAINER,
    'GENERAL_CONTAINER': DeviceType.GENERAL_CONTAINER,
    'FPGA': DeviceType.FPGA,
    'MEMORY_CONTROLLER': DeviceType.MEMORY_CONTROLLER,
}


class DeviceProtocol(CustomEnum):
    """Enumeration for device protocols."""
    TCP_IP = 0
    UART = 1
    SPI = 2
