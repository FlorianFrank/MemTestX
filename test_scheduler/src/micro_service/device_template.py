from dataclasses import dataclass
from device_definitions import DeviceType, DeviceProtocol, DeviceStatus, DEVICE_TYPE_MAP


@dataclass
class DeviceTemplate:
    name: str
    idn: str
    type: DeviceType
    protocol: DeviceProtocol
    port: str
    status: DeviceStatus
    additional: []

    def as_dict(self) -> dict:
        return {
            **self.__dict__,
            'type': str(self.type),
            'protocol': str(self.protocol),
            'status': str(self.status),
            'idn': str(self.idn),
            'additional': self.additional
        }


def input_str_to_device_type(identifier: str) -> DeviceType:
    """Converts a string identifier to DeviceType enum."""
    return DEVICE_TYPE_MAP.get(identifier.upper(), DeviceType.OTHER)


def input_str_to_protocol(identifier: str) -> DeviceProtocol:
    if identifier.upper() == 'TCP_IP':
        return DeviceProtocol.TCP_IP
    if identifier.upper() == 'UART':
        return DeviceProtocol.UART
    if identifier.upper() == 'SPI':
        return DeviceProtocol.SPI
