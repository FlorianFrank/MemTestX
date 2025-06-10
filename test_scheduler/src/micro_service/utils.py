import ipaddress
import re
import socket
import platform
import uuid
from typing import Optional, List, Tuple

import psutil

from logging_handler import logger


def get_network_info(interface_name) -> Tuple[Optional[str], Optional[str], Optional[ipaddress.IPv4Network]]:
    try:
        # Get all network interfaces
        all_interfaces = psutil.net_if_addrs()
        # Check if the specified interface exists
        if interface_name in all_interfaces:
            # Find the first IPv4 address and netmask associated with the specified interface
            for address in all_interfaces[interface_name]:
                if address.family == socket.AF_INET:
                    ip_address = address.address
                    netmask = address.netmask
                    network = ipaddress.IPv4Network(f"{ip_address}/{netmask}", strict=False)
                    return ip_address, netmask, network
            # If no IPv4 address is found, return None
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


def get_executor_info():
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

            {'key': 'FPGA Board', 'value': 'ZCU102 Evaluation Board'},
            {'key': 'FPGA Resolution', 'value': '2.5 ns'},
            {'key': 'CPUs', 'value': 'Cortex A53/ Cortex R5'},
            {'key': 'FPGA IP', 'value': '132.231.14.92'},
            {'key': 'Ports', 'value': '5023/5024'},
            ]
