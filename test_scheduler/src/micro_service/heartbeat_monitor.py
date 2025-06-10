import asyncio
import json
import threading

import logging_handler
import time

from device_list import DeviceList
from messaging_service_base import MessagingServiceBase
from messaging_service_config import get_topic_str, Topic


class HeartbeatMonitor:
    """
    This class sends periodic heartbeat messages to discovered devices.
    The heartbeat interval can be adjusted by the "heartbeat_interval" parameter in the configuration file.
    """

    def __init__(self, logger: logging.Logger, device_list: DeviceList, messaging_service: MessagingServiceBase,
                 event_loop, port: int, heartbeat_interval: int, send_continuously: bool = True):
        self._thread = None
        self._device_list = device_list
        self._logger = logger
        self._port = port
        self._heartbeat_interval = heartbeat_interval
        self._messaging_service = messaging_service
        self._event_loop = event_loop
        self._send_continuously = send_continuously
        self._stop_event = threading.Event()

    def _heartbeat_task(self):
        """
        The thread function continuously sends an 'IDN?' instruction to each device in the device list and publishes
        the device status when the state of a device changes, such as transitioning from offline to online or vice versa
        """
        while not self._stop_event.is_set():
            nr_updates = 0
            for dev in self._device_list.return_device_dicts():
                if dev['protocol'] == 'tcp_ip':
                    self._logger.info(f"Send heartbeat to device {dev}")
                    ip = dev['port'].split(':')[0]
                    #new_device = DeviceDiscovery.send_discover_msg(logger=self._logger, ip=ip, port=self._port,
                      #                                             device_list=self._device_list)

                    #if new_device is not None:
                     #   nr_updates += 1 if (self._device_list.update(new_device)) else 0

            time.sleep(self._heartbeat_interval)
            self._device_list.validate_all_devices()

            if self._send_continuously or (self._device_list.has_changed() or nr_updates > 0):
                asyncio.run_coroutine_threadsafe(
                    self._messaging_service.publish_topic(
                        {'topic': get_topic_str(Topic.GET_DEVICES),
                         'data': json.dumps(self._device_list.return_device_dicts())}),
                    self._event_loop
                ).result()

        self._logger.info("Heartbeat thread stopped.")

    def start(self):
        """
        Starts the heartbeat thread function, which monitors all devices.
        """
        self._logger.info("Starting heartbeat thread")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._heartbeat_task)
        self._thread.start()

    def stop(self):
        """
        Stops the monitor thread function.
        """
        self._logger.info("Stopping heartbeat thread")
        self._stop_event.set()
        if self._thread:
            self._thread.join()
