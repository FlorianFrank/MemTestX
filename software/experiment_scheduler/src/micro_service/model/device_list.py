import threading
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple

from micro_service.utils.device_definitions import DeviceType, DeviceStatus, DeviceProtocol
from model.device_template import DeviceTemplate


class DeviceAvailability(Enum):
    # Indicates that the device was added and never asked by the heartbeat service
    ADDED = 1
    # Device state was updated by the heartbeat service
    UPDATED = 2
    # Device cannot be reached by the heartbeat service
    UNAVAILABLE = 3


class DeviceList:
    def __init__(self):
        self._devices: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._has_changed = True
        self._device_template_list: List[Tuple[str, str, DeviceType, List[dict]]] = []

    def get_first_element(self) -> DeviceTemplate:
        """
        Returns the first element in the device list as dictionary otherwise return IndexError.
        e.g. Device dict, e.g. {"name": "NANOSEC MicroService", "idn": "NANOSEC_CONTAINER", "type": "nanosec_container",
        "protocol": "tcp_ip", "port": "192.168.178.77", "status": "online"}

        Returns:
            DeviceTemplate: The first device in the list.
        Raises:
            IndexError: If the list is empty.

        """
        if not self._devices or len(self._devices) == 0:
            raise IndexError("Device list is empty")
        return self._devices[0]['dev']

    def add(self, device: DeviceTemplate) -> None:
        """
        Adds a new device to the list.

        Args:
            device (DeviceTemplate): The device to add.
        """
        with self._lock:
            self._devices.append({'dev': device, 'updated': DeviceAvailability.ADDED})
            self._has_changed = True

    def update(self, updated_device: DeviceTemplate) -> bool:
        """
        Update an existing device, for example, change its state from online to offline or vice versa.
        This method should only be called by the heartbeat service.

        Args:
            updated_device (DeviceTemplate): The updated device.

        Returns:
            bool: True if the device was updated, False otherwise.
        """
        with self._lock:
            for index, device_info in enumerate(self._devices):
                if device_info['dev'].idn.strip() == updated_device.idn.strip() and \
                        device_info['dev'].port.strip() == updated_device.port.strip():
                    if self._devices[index]['dev'].status != updated_device.status:
                        device_info['dev'] = updated_device
                        device_info['updated'] = DeviceAvailability.UPDATED
                        return True
            return False

    def device_exists(self, device: DeviceTemplate):
        """
        Checks if a device exists in the list.

        Args:
            device (DeviceTemplate): The device to check.

        Returns:
            bool: True if the device exists, False otherwise.
        """
        return any(d['dev'].idn.strip() == device.idn.strip() or d['dev'].port.strip() == device.port.strip()
                   for d in self._devices)

    def validate_all_devices(self) -> None:
        """
        Iterates over the device list and checks the updated devices.
        If a device is unavailable it is declared as offline.
        It does not check the current container device.
        """
        with self._lock:
            for d in self._devices:
                if d['updated'] == DeviceAvailability.UNAVAILABLE and not (
                        d['dev'].type == DeviceType.NANOSEC_CONTAINER or d['dev'].type == DeviceType.GENERAL_CONTAINER):
                    if d['dev'].status != DeviceStatus.OFFLINE:
                        d['dev'].status = DeviceStatus.OFFLINE
                        self._has_changed = True
                d['updated'] = DeviceAvailability.UNAVAILABLE

    def return_device_dicts(self) -> list[Dict[str, Any]]:
        """
        Returns the list of devices as dictionary.

        Returns:
            List[Dict[str, Any]]: A list of device dictionaries.
        """
        with self._lock:
            self._has_changed = False
            return [x['dev'].as_dict() for x in self._devices]

    def remove_device(self, idn: str, port: str) -> Optional[DeviceTemplate]:
        """
        Removes a device from the list.

        Args:
            idn (str): The identifier of the device to remove.
            port (str): The port of the device to remove.

        Returns:
            Optional[DeviceTemplate]: The removed device, or None if not found.
        """
        with self._lock:
            filtered_devices = filter(lambda d: d['dev'].idn == idn and d['dev'].port == port, self._devices)
            removed_device = next(filtered_devices, None)
            if removed_device:
                self._devices.remove(removed_device)
                self._has_changed = True
            return removed_device

    def has_changed(self) -> bool:
        """
        Checks if the device list has changed.

        Returns:
            bool: True if the device list has changed, False otherwise.
        """
        return self._has_changed

    def register_device_template(self, identifier: str, name: str, device_type: DeviceType, additional: Optional[List[dict]]) -> None:
        self._device_template_list.append((identifier, name, device_type, additional))

    def idn_to_device_object(self, recv_msg: str, ip: str, port: int) -> Optional[DeviceTemplate]:
        filtered_iter = iter(filter(lambda dev_tuple: dev_tuple[0] in recv_msg, self._device_template_list))
        detected_device_tuple = next(filtered_iter, None)
        if detected_device_tuple:
            return DeviceTemplate(name=detected_device_tuple[1], idn=recv_msg.replace('\n', ''),
                                  port=f'{ip}:{port}', type=detected_device_tuple[2], protocol=DeviceProtocol.TCP_IP,
                                  status=DeviceStatus.ONLINE, additional=detected_device_tuple[4])
        return None

    def exists(self, device_template: DeviceTemplate) -> bool:
        """
        Return if a device exists in the device list, identified by its idn and port.
        """
        return any(device_template.idn == d['dev'].idn and device_template.port == d['dev'].port for d in self._devices)