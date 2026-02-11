import socket
import threading
import time
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from model.device_list import DeviceList
from model.device_template import DeviceTemplate
from micro_service.utils.utils import get_network_info, generate_ip_list

DEFAULT_TIMEOUT_IN_S = 2
IDENTIFICATION_MSG = b'*IDN?\n'
RET_BUFFER_SIZE = 256
DISCOVERY_INTERVAL = 20
MAX_DISCOVERY_THREADS = 50  # Limit concurrent discovery threads


class DeviceDiscovery:
    def __init__(self, logger, device_list):
        self._running = False
        self._main_thread = None
        self._logger = logger
        self._device_list = device_list

    def _device_discovery_thread_function(self, interface: str, port: int, device_list: DeviceList):
        while self._running:
            ip_address, netmask, network = get_network_info(interface)

            if ip_address and network:
                self._logger.info(f"Identify NIC {interface} Ip {ip_address} Mask {netmask}")
                ip_list = generate_ip_list(network)
                self._logger.info(f"Start {len(ip_list)} discovery threads")

                with ThreadPoolExecutor(max_workers=MAX_DISCOVERY_THREADS) as executor:
                    futures = {executor.submit(self._device_discovery_thread, ip, port, device_list): ip
                               for ip in ip_list}

                    for future in as_completed(futures):
                        ip = futures[future]
                        try:
                            future.result()
                        except Exception as e:
                            self._logger.error(f"Error discovering device at {ip}: {e}")

                self._logger.info(f"Device discovery round completed")
          #  device_list.validate_all() #TODO
            time.sleep(DISCOVERY_INTERVAL)

    def start_device_discovery(self, interface_name: str, port: int, device_list: DeviceList):
        self._running = True
        self._main_thread = threading.Thread(target=self._device_discovery_thread_function,
                                             args=(interface_name, port, device_list))
        self._main_thread.start()

    def stop_device_discovery(self):
        self._running = False
        self._main_thread.join()

    def is_discovery_running(self):
        return self._running
    def send_discover_msg(self, ip: str, port: int) -> Optional[DeviceTemplate]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(DEFAULT_TIMEOUT_IN_S)
                s.connect((ip, port))
                s.sendall(IDENTIFICATION_MSG)
                recv_msg = s.recv(RET_BUFFER_SIZE)
                if len(recv_msg) > 0:
                    self._logger.info(f'Parse device info {recv_msg} at {ip}:{port}')
                    return self._device_list.device_list.idn_to_device_object(recv_msg=recv_msg.decode('utf-8'), ip=ip, port=port)
        except socket.timeout:
            # logging.info(f'No devices found at IP: {ip}')
            return None
        except Exception as e:
            if 'Connection refused' not in str(e):
                self._logger.error(f'Error occurred {e}')
            return None

        self._logger.info(f'No devices found at IP: {ip}')
        return None

    def _device_discovery_thread(self, ip: str, port: int, device_list: DeviceList):
        device = self.send_discover_msg(ip, port)
        if device is not None:
            if device_list.exists(device):
                self._logger.info(f"Update existing device {device}")
                device_list.update(device)
            else:
                self._logger.info(f"Add new device {device}")
                device_list.add(device)
