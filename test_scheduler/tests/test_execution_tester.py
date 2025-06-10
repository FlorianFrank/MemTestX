import json
import socket
import threading
import time
from typing import Optional

import coloredlogs

from src.definitions import IP_SUFFIX
from src.network_handler import NetworkHandler

RECV_PORT = 5024
SEND_PORT = 5023
srv_ip = 'localhost'

thread: Optional[threading.Thread] = None
thread_running: bool = False
recv_sock: Optional[socket.socket]


def handle_start_test(socket: socket.socket, stop_address: int):
    response = {'cmd': 'start_measurement', 'msg_type': 'response', 'cmd_status': 'processing'}
    socket.sendto(str(json.dumps(response) + ' ').encode(), ('localhost', SEND_PORT))
    buff = []
    for i in range(stop_address):
        time.sleep(0.0001)
        buff.append([i, 0x55, 0xf1])
        if i % 10 or i == stop_address - 1:
            response = {'msg_type': 'm', 'd': buff}
            socket.sendto(str(json.dumps(response) + ' ').encode(), ('localhost', SEND_PORT))
            buff.clear()
    response = {'cmd': 'start_measurement', 'msg_type': 'response', 'cmd_status': 'ready'}
    socket.sendto(str(json.dumps(response) + ' ').encode(), ('localhost', SEND_PORT))


def parse_test_json(input_str: bytes):
    parsed = json.loads(input_str.decode())
    logger.info(f'Received test data: {parsed}')
    response = {}

    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if parsed['cmd'] == 'start_measurement':
        handle_start_test(send_sock, parsed['stop_addr'])

    logger.info(f'Send back response {response}')


def recv_thread_func():
    logger.info("Start Recv Thread")
    while thread_running:
        data, address = recv_sock.recvfrom(1024)
        parse_test_json(data)


def start_recv_thread():
    global thread, thread_running
    thread_running = True
    thread = threading.Thread(target=recv_thread_func)
    thread.start()


def stop_recv_thread():
    global thread, thread_running
    thread_running = False
    thread.join()


def start_test_simulator():
    global recv_sock, srv_ip
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    srv_ip = NetworkHandler.detect_network_interface_with_suffix(IP_SUFFIX)
    logger.info(f"Detected server ip: {srv_ip} -> Start Tester")
    recv_sock.bind(('', RECV_PORT))
    start_recv_thread()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    coloredlogs.install(level='DEBUG')
    coloredlogs.install(level='DEBUG', logger=logger)

    logger.info(f'Start Test simulator. Waiting for incoming data...')
    start_test_simulator()

    while True:
        time.sleep(1)
