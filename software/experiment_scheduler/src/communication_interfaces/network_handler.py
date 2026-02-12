import json
import socket
import threading
from typing import Dict, List
from typing import Optional

import netifaces
from typing_extensions import override

from communication_interfaces.interface_wrapper import InterfaceWrapper
from communication_interfaces.ip_definitions import IPConfig
from db_handler import logger
from test_scheduling.memory_test import MemoryTest

from test_scheduling.test_defines import TestState, StandaloneTest
from utils.definitions import Command, cmd_to_str, NETWORK_TIMEOUT_RESPONSE, NETWORK_MAX_RECV_BUF_LEN, InterfaceEnum


class NetworkHandler(InterfaceWrapper):
    def __init__(self):
        super().__init__()
        self._response = None
        self._send_socket = None
        self._recv_socket = None
        self._ip = None
        self._send_port = None
        self._recv_port = None
        self._recv_thread = None
        self._received_response = {}
        self._is_response_received = False

    def is_response_received(self):
        return self._is_response_received

    def get_response(self):
        self._is_response_received = False
        return self._response

    @staticmethod
    def create_udp_socket():
        logger.debug("Creating UDP socket.")
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def initialize(self, ip_address: str, send_port: int, recv_port: int):
        logger.info("Initializing NetworkHandler with IP: %s, send_port: %d, recv_port: %d", ip_address, send_port,
                    recv_port)
        try:
            self._send_socket = self.create_udp_socket()
            self._ip = ip_address
            self._send_port = send_port
            self._recv_port = recv_port
            logger.info("NetworkHandler initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize NetworkHandler: %s", e)
            raise

    @override
    def send_config(self, cmd: Command, ip_config: IPConfig, cfg: dict = None):
        self._is_response_received = False
        try:
            config_full = cfg or {}
            config_full["cmd"] = cmd_to_str(cmd)
            response = json.dumps(config_full)
            response = response.replace('{', '{\n')
            response = response.replace('}', '\n}')
            response = response.replace(", ", ",\n")
            logger.debug("Send command {}".format(response))
            self._send_socket.sendto(response.encode(), (ip_config.ip, ip_config.port))
            logger.info("Sent command '%s' to IP: %s, Port: %d", cmd_to_str(cmd), ip_config.ip, ip_config.port)
        except Exception as e:
            logger.error("Failed to send config: %s", e)
            raise

    @override
    def parse_msg(self, response: bytes, test: MemoryTest | StandaloneTest): # TODO to not forget
        try:
            decoded_str = response.decode('utf-8')
            if decoded_str[-1] != '}':
                response_json = json.loads(response.decode('utf-8')[:-1])  # ERROR incorrect data at the end?
            else:
                response_json = json.loads(response.decode('utf-8'))  # ERROR incorrect data at the end?
            if response_json['msg_type'] == 'response':
                if response_json['cmd'] == 'start_measurement':
                    if response_json['cmd_status'] == 'processing':
                        logger.debug("Transition state to processing")
                        test.set_processing()
                    if response_json['cmd_status'] == 'ready':
                        InterfaceWrapper.wait_until_writer_finishes(test)
                    if response_json['cmd_status'] == 'error':
                        test.set_error()
                        logger.error(f"Error returned {response_json}")

                if response_json['cmd'] == 'idn':
                    logger.info("Receive Response from command `idn` with status `%s`", response_json['cmd_status'])
                    self._is_response_received = True
                    self._response = response_json
                if response_json['cmd'] == 'reset':
                    logger.info("Receive Response from command `reset` with status `%s`", response_json['cmd_status'])
                    self._is_response_received = True
                    self._response = response_json
                if response_json['cmd'] == 'status':
                    logger.info("Receive Response from command `status` with status `%s`", response_json['cmd_status'])
                    self._is_response_received = True
                    self._response = response_json

            if response_json['msg_type'] == 'm':
                data = response_json['d']
                if isinstance(test, MemoryTest):
                    if len(data) > 0 and len(data[-1]) > 0:
                        test.update_progress(data[-1][0])

                if test and test.measure_file:
                    test.measure_file.add_to_buffer(data)
                else:
                    # TODO may remove in the future
                    logger.warning("Received measurement data but no measure_file is initialized for the current test.")

        except Exception as e:
            logger.error(f"Failed to decode response ({response.decode()}): {e}")

    @override
    def recv_thread_func(self, test: StandaloneTest | MemoryTest):
        self._recv_socket = self.create_udp_socket()
        logger.info(f"Starting Receive Thread bind to: {self._ip}:{self._recv_port}")
        self._recv_socket.bind((self._ip, self._recv_port))
        try:
            while not self._stop_thread:
                logger.info("Wait for incoming data...")
                self._recv_socket.settimeout(NETWORK_TIMEOUT_RESPONSE)
                try:
                    response, server = self._recv_socket.recvfrom(NETWORK_MAX_RECV_BUF_LEN)  # Buffer size of 4096 bytes
                    logger.info("Received data from %s: %s", server, response.decode())
                    self.parse_msg(response, test)
                except TimeoutError:
                    if test.get_state() == TestState.WAITING_FOR_RESPONSE:
                        logger.error(f"Timed out waiting {NETWORK_TIMEOUT_RESPONSE} seconds for response")
                        test.set_error()
                    if self._stop_thread:
                        logger.info(f"Stopping recv_thread function")

        except Exception as e:
            logger.error("Error in Receive Thread: %s", e)

    @override
    def start_recv_thread(self, test: StandaloneTest | MemoryTest):
        self._stop_thread = False
        self._recv_thread = threading.Thread(target=self.recv_thread_func, args=(test,))
        self._recv_thread.start()
        logger.info("Network handler Receive thread started.")

    @override
    def stop_thread(self):
        logger.info("Stopping receive thread.")
        self._stop_thread = True
        if self._recv_thread and self._recv_thread.is_alive():
            self._recv_thread.join()
            logger.info("Receive thread stopped successfully.")
        else:
            logger.warning("Receive thread was not running.")

    @staticmethod
    def get_network_interfaces() -> Dict[str, Dict[str, List[IPConfig]]]:
        """
        Retrieve network interfaces and their configurations (IP and netmask).

        Returns:
            A dictionary mapping each network interface to its configuration.
        """
        logger.info("Retrieving network interfaces...")
        interfaces = netifaces.interfaces()
        interface_config = {}

        for iface in interfaces:
            if iface == "lo":
                logger.debug(f"Skipping loopback interface: {iface}")
                continue

            logger.debug(f"Processing interface: {iface}")
            # Get address families for the current interface
            try:
                addresses = netifaces.ifaddresses(iface)
            except Exception as e:
                logger.error(f"Failed to retrieve addresses for interface {iface}: {e}")
                continue

            # Extract configurations for this interface
            cfg_list = [
                IPConfig(ip=addr_info.get("addr"), netmask=addr_info.get("netmask"))
                for family in addresses.values()
                for addr_info in family
                if "addr" in addr_info and "netmask" in addr_info
            ]

            # Store the configuration if any valid entries are found
            if cfg_list:
                interface_config[iface] = {"cfg": cfg_list}
                logger.debug(f"Found configuration for interface {iface}: {cfg_list}")
            else:
                logger.debug(f"No valid IP configuration found for interface {iface}.")

        logger.info("Completed retrieving network interfaces.")
        return interface_config

    @staticmethod
    def detect_network_interface_with_suffix(suffix: str) -> Optional[str]:
        """
        Detect a network interface with an IP address containing the specified suffix.

        Args:
            suffix: A substring to search for in IP addresses.

        Returns:
            The IP address of the first matching interface or None if not found.
        """
        logger.info(f"Detecting network interface with IP suffix: {suffix}")
        network_interfaces_dict = NetworkHandler.get_network_interfaces()
        for iface, value in network_interfaces_dict.items():
            for cfg in value["cfg"]:
                if suffix in cfg.ip:
                    logger.info(f"Found matching interface: {iface} with IP: {cfg.ip}")
                    return cfg.ip  # TODO: Only one IP is possible
        logger.warning(f"No interface found with IP suffix: {suffix}")
        return None

    @override
    def get_if_type(self) -> InterfaceEnum:
        return InterfaceEnum.ETH_IF

    @override
    def send_continue(self, ip_config: IPConfig):
        try:
            self._send_socket.sendto("Continue".encode(), (ip_config.ip, ip_config.port))
            logger.info("Sent continue to IP: %s, Port: %d", ip_config.ip, ip_config.port)
        except Exception as e:
            logger.error("Failed to send config: %s", e)
            raise
