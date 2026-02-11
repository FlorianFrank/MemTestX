"""
Main entry point for the microservice handling networking, device management, and messaging.
"""

import asyncio
import json
import logging

from communication_interfaces.interface_wrapper import InterfaceWrapper
from communication_interfaces.ip_definitions import IPConfig
from micro_service.controller.config_handler import load_microservice_config
from micro_service.utils.device_definitions import DeviceStatus
from controller.device_discovery import DeviceDiscovery
from model.device_list import DeviceList
from model.device_template import DeviceTemplate, input_str_to_device_type, input_str_to_protocol
from controller.heartbeat_monitor import HeartbeatMonitor
from messaging_service.messaging_service_callback_handler import MessagingServiceCallbackHandler
from messaging_service.messaging_service_config import Topic
from messaging_service.nats_micro_service import NATSMessagingService
from micro_service.tests.row_hammering_test import RowHammeringTest
from messaging_service.streaming_service import StreamingService, get_topic_str
from controller.test_parser import TestParser
from test_scheduling.test_queue import TestQueue
from test_scheduling.test_scheduler import TestScheduler
from tests.read_latency_test import ReadLatencyTest
from tests.reliability_test import ReliabilityTest
from tests.write_latency_test import WriteLatencyTest
from utils.definitions import PORT_SEND, PORT_RECV
from utils.setup import Setup
from micro_service.utils.utils import list_all_network_cards, get_network_info, get_executor_info, print_start_dialog

DEV_CONFIG_FOLDER = './config_files/device_specifications'


class Microservice:
    """Provides configuration and setup logic for microservice orchestration."""

    @staticmethod
    def set_network_config():
        """ Show list of all available network cards and select one from the list."""
        network_card = list_all_network_cards()
        logging.info("Select network card %s", network_card)
        ip, netmask, network = get_network_info(network_card)
        logging.info("Retrieved network settings from %s: "
                     "(IP: %s, Netmask: %s, Network: %s)", network_card, ip, netmask, network)
        network_handler = Setup.setup_network(ip_address=ip, port_send=PORT_SEND, port_recv=PORT_RECV)
        return network_handler, network_card, ip, netmask, network

    @staticmethod
    def setup_heartbeat_service(event_lp, logger, device_list: DeviceList, app_config: dict, messaging_interface: NATSMessagingService):
        """
        Starts the heartbeat service in a separate thread, which sends an identification message every
        heartbeat_interval seconds, to all devices registered in the DeviceList.
        """
        heartbeat_monitor = HeartbeatMonitor(logger, device_list=device_list, port=app_config['discovery_port'],
                                             heartbeat_interval=app_config['heartbeat_interval'],
                                             messaging_service=messaging_interface,
                                             event_loop=event_lp,
                                             send_continuously=True if app_config[
                                                                           'heartbeat_publish_continuously'].lower() == 'true' else False)
        heartbeat_monitor.start()

    @staticmethod
    async def setup_messaging_interface(event_loop, logger, device_list: DeviceList, container_device: DeviceTemplate, test_parser,
                                        scheduler, broker_ip: str, broker_port: int) -> NATSMessagingService:
        """
        Set up the MessagingService and its required callback function. It further starts the test scheduler and
        registers the executor service at the test hub backend.
        """

        callback_handler = MessagingServiceCallbackHandler(logger, endpoint=container_device.port,
                                                           endpoint_name=container_device.name, test_scheduler=scheduler,
                                                           test_parser=test_parser, event_loop=event_loop)
        await callback_handler.init_test_scheduler()

        messaging_interface = NATSMessagingService(device_list, event_loop, logger, callback_handler)

        streaming_service = StreamingService(logger=logger, nats_interface=messaging_interface,
                                             event_loop=event_loop)
        streaming_service.start_streaming_thread()

        callback_handler.register_streaming_service(streaming_service=streaming_service)

        await messaging_interface.setup_interface(
            params={'endpoint': broker_ip + f':{broker_port}', 'endpoint_name': container_device.name})
        await messaging_interface.publish_topic(
            {'topic': get_topic_str(Topic.GET_DEVICES), 'data': json.dumps(device_list.return_device_dicts())})
        return messaging_interface

    @staticmethod
    def create_device_template(app_config: dict, ip_address: str) -> DeviceList:
        """
        Generates a device to represent the currently running executor service.
        Additionally, this device is appended to a newly created DeviceList, which is then returned.
        """
        d = DeviceTemplate(name=app_config['general_config']['executor_name'],
                           idn=app_config['general_config']['executor_type'],
                           type=input_str_to_device_type(app_config['general_config']['executor_type']),
                           protocol=input_str_to_protocol(app_config['general_config']['protocol']),
                           port=f'{ip_address}:{app_config['general_config']["discovery_port"]}',
                           status=DeviceStatus.ONLINE,
                           additional=get_executor_info(app_config))

        device_list = DeviceList()
        device_list.add(d)
        return device_list


    @staticmethod
    def set_supported_tests(logger):
        """
        Registers the different test types, which can be used to parse and execute certain tests.
        """
        test_parser = TestParser(logger=logger)
        logger.info('Registering test types: RowHammering, WriteLatency and ReadLatency.')
        test_parser.register_test_type('Row Hammering Tests', RowHammeringTest)
        test_parser.register_test_type('Write Latency Tests', WriteLatencyTest)
        test_parser.register_test_type('Read Latency Tests', ReadLatencyTest)
        test_parser.register_test_type('Reliability Tests', ReliabilityTest)
        return test_parser


    @staticmethod
    def setup_device_discovery(logger, app_config: dict, interface_name, device_list: DeviceList):
         """
         Initiates a discovery service in a separate thread, designed to operate exclusively within a
         local network environment.
         """
         if app_config['enable_device_discovery'] == 'true':
            device_discovery = DeviceDiscovery(logger, device_list)
            logger.info('Start device Discovery')
            device_discovery.start_device_discovery(interface_name=interface_name,port=app_config['discovery_port'], device_list=device_list)


    @staticmethod
    async def entry_point(event_lp, logger, scheduler: TestScheduler):
        """
        Entrypoint of the microservice. This function starts the NATS endpoint, the heartbeat
        service and the device discovery. Furthermore, it initializes the test scheduler.
        """
        app_config = load_microservice_config()

        print_start_dialog()
        network_handler, network_card, ip, netmask, network = Microservice.set_network_config()

        device_list = Microservice.create_device_template(app_config, ip)
        container_device = device_list.get_first_element()
        test_parser = Microservice.set_supported_tests(logger)
        tq   = TestQueue(logger)
        #scheduler = TestScheduler(test_queue=tq, time_between_tests_in_ms=app_config['general_config']['scheduler_time_interval'],
                           #       comm_interface=comm_interface, server_ip=IPConfig(ip="localhost", port=PORT_SEND),
                            #      run_microservices=True)

        scheduler.set_test_queue(tq)
        scheduler.set_time_between_tests_in_ms(app_config['general_config']['scheduler_time_interval'])

        messaging_interface = await Microservice.setup_messaging_interface(event_lp, logger, device_list, container_device, test_parser,
                                                              scheduler, app_config['nats_config']['nats_broker_ip'],
                                                              int(app_config['nats_config']['nats_broker_port']))

        # Start heartbeat service continuously requesting the availability of the device in the device list.
        Microservice.setup_heartbeat_service(event_lp=event_lp, logger=logger,
                                             device_list=device_list,
                                             app_config=app_config['general_config'],
                                             messaging_interface=messaging_interface)

        # Start device discovery in the local network
        Microservice.setup_device_discovery(logger, app_config['general_config'], network_card, device_list)

def run_microservice(logger, scheduler: TestScheduler):
    """Initializes and runs the microservice event loop."""

    logger.info("Running microservice")
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    try:
        event_loop.run_until_complete(Microservice.entry_point(event_loop, logger, scheduler))
        event_loop.run_forever()
    finally:
        event_loop.close()
