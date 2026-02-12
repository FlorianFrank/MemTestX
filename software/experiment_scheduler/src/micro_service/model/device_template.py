from dataclasses import dataclass, field
from typing import List, Any

from micro_service.utils.device_definitions import DeviceType, DeviceProtocol, DeviceStatus, DEVICE_TYPE_MAP


@dataclass
class DeviceTemplate:
    """Template describing a device instance (e.g. an execution container)."""

    name: str
    idn: str
    type: DeviceType
    protocol: DeviceProtocol
    port: str
    status: DeviceStatus
    additional: List[Any] = field(default_factory=list)

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
    if not identifier:
        return DeviceType.OTHER
    return DEVICE_TYPE_MAP.get(identifier.strip().upper(), DeviceType.OTHER)

def input_str_to_protocol(identifier: str) -> DeviceProtocol:
    """Convert a string identifier to a DeviceProtocol enum."""
    try:
        return DeviceProtocol[identifier.strip().upper()]
    except (KeyError, AttributeError):
        raise ValueError(f"Unknown protocol '{identifier}'") from None