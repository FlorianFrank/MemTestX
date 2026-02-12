"""
Microservice util class contains helper functions, e.g. to list all network interfaces,
or functions to select a listed network interface from command line.
"""

import ipaddress
import platform
import re
import socket
import uuid
from typing import Optional, List, Tuple

import psutil

from db_handler import logger


def print_start_dialog():
    print("*******************************************************************************************")
    print("******************************* Start Test Hub Micro Service*******************************")
    print("*******************************************************************************************")


def list_all_network_cards() -> str:
    """
    Prints a list of available network interfaces currently connected, allowing the user to select one to bind
    this microservice.
    """
    network_card_list = list(psutil.net_if_addrs().keys())

    print("Select a network card to bind the micro-service:")
    for idx, card in enumerate(network_card_list):
        print(f"    {idx}: {card}")

    while True:
        selection = input("Insert selection: ").strip()
        try:
            selected_index = int(selection)
            if 0 <= selected_index < len(network_card_list):
                return network_card_list[selected_index]
            else:
                print(f"Selection out of range! Please enter a number between 0 and {len(network_card_list) - 1}")
        except ValueError:
            print(f"Invalid input! Please insert numbers between 0 and {len(network_card_list) - 1}")


def print_app_config(app_config: dict) -> None:
    print("\n**********************************")
    print("**Load app config**:")
    for key, value in app_config.items():
        print(f"{key}: {value}")
    print("**********************************\n")


def get_network_info(interface_name) -> Tuple[Optional[str], Optional[str], Optional[ipaddress.IPv4Network]]:
    """
    Retrieves the IP address, netmask, and network object for a given interface name.

    Args:
        interface_name (str): The name of the network interface (e.g., 'eth0').

    Returns:
        Tuple: (ip_address, netmask, IPv4Network) or (None, None, None) if no IPv4 address is found.
    """
    try:
        all_interfaces = psutil.net_if_addrs()
        if interface_name in all_interfaces:
            for address in all_interfaces[interface_name]:
                if address.family == socket.AF_INET:
                    ip_address = address.address
                    netmask = address.netmask
                    network = ipaddress.IPv4Network(f"{ip_address}/{netmask}", strict=False)
                    return ip_address, netmask, network
            return None, None, None
        else:
            raise ValueError(f"Interface '{interface_name}' not found.")
    except Exception as e:
        raise RuntimeError(f"Error getting network information: {e}")


def generate_ip_list_from_network(network: ipaddress.IPv4Network) -> Optional[List[str]]:
    """
    Generate a list of IPv4 addresses from the given IPv4 network.

    :param network: IPv4Network object representing the network range.
    :return: List of IPv4 addresses in the network range, or None if an error occurs.
    """
    try:
        # Generate a list of all IPv4 addresses in the network range
        ipv4_list = [str(ip) for ip in network.hosts()]
        return ipv4_list
    except Exception as e:
        logger.error(f"Error generating IPv4 address list: {e}")
        return None


def get_executor_info(device_config: dict):
    """
    Returns general information about the machine on which this executor is running.
    Can be displayed at the device info page in the frontend.
    """
    os_info = platform.uname()
    virtual_memory = str(round(psutil.virtual_memory().total / (1024.0 ** 3))) + " GB"

    return [{'key': 'Hostname', 'value': f'{socket.gethostname()}'},
            {'key': 'Container Physical Address', 'value': ':'.join(re.findall('..', '%012x' % uuid.getnode()))},
            {'key': 'Container System', 'value': f'{os_info.system}'},
            {'key': 'Container Version', 'value': f'{os_info.version}'},
            {'key': 'Container Machine', 'value': f'{os_info.machine}'},
            {'key': 'Container Processor', 'value': f'{os_info.processor}'},
            {'key': 'Container Virtual Memory', 'value': f'{virtual_memory}'},

            {'key': 'FPGA Board', 'value': device_config['fpga_config']['board']},
            {'key': 'FPGA Resolution', 'value': device_config['fpga_config']['timing_resolution']},
            {'key': 'CPUs', 'value': device_config['fpga_config']['cpus']},
            {'key': 'FPGA IP', 'value': device_config['fpga_config']['ip']},
            {'key': 'Ports', 'value': device_config['fpga_config']['port']},
            ]

def generate_ip_list(network):
    """Generate a list of all IP addresses in the network range
    """
    try:
        ip_list = [str(ip) for ip in network.hosts()]
        return ip_list
    except Exception as e:
        print(f"Error generating IP address list: {e}")
        return None