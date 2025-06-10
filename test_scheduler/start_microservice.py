import asyncio
import json
from ipaddress import IPv4Network

from definitions import PORT_SEND, PORT_RECV, DB_NAME
from micro_service import test_parser
from micro_service.command_line_handler import print_start_dialog, print_app_config, print_network_card_selection
from micro_service.config_handler import load_app_config, add_all_devices
from micro_service.device_definitions import DeviceStatus
from micro_service.device_list import DeviceList
from micro_service.device_template import DeviceTemplate, input_str_to_device_type, input_str_to_protocol
from micro_service.heartbeat_monitor import HeartbeatMonitor
from micro_service.logging_handler import logger
from micro_service.messaging_service_callback_handler import MessagingServiceCallbackHandler
from micro_service.messaging_service_config import Topic, get_topic_str
from micro_service.nats_micro_service import NATSMessagingService
from micro_service.streaming_service import StreamingService
from micro_service.utils import get_network_info, get_executor_info
from network_handler import IPConfig
from setup import Setup
from test_parser import TestParser
from test_queue import TestQueue
from test_scheduler import TestScheduler

DEV_CONFIG_FOLDER = './config_files/device_specifications'

def register_test_types() -> TestParser:
    """
    Registers the different test types, which can be used to parse and execute certain tests.
    """
    test_parser = TestParser(logger=logger)
    test_parser.register_test_type('Sample Test')
    test_parser.register_test_type('Transfer Characteristic')
    return test_parser

def setup_heartbeat_service(device_list: DeviceList, app_config: dict, messaging_interface: NATSMessagingService):
    """
    Starts the heartbeat service in a separate thread, which sends an identification message every
    heartbeat_interval seconds, to all devices registered in the DeviceList.
    """
    heartbeat_monitor = HeartbeatMonitor(logger, device_list=device_list, port=app_config['discovery_port'],
                                         heartbeat_interval=app_config['heartbeat_interval'],
                                         messaging_service=messaging_interface,
                                         event_loop=event_loop,
                                         send_continuously=True if app_config[
                                                                       'heartbeat_publish_continuously'].lower() == 'true' else False)
    heartbeat_monitor.start()

def setup_device_discovery(app_config: dict, messaging_interface: NATSMessagingService, ip: str,
                           network: IPv4Network,
                           device_list: DeviceList):
    """
    Initiates a discovery service in a separate thread, designed to operate exclusively within a
    local network environment.
    """
   # if app_config['enable_device_discovery'] == 'true':
        #device_discovery = DeviceDiscovery(logger, app_config['discovery_interval'], messaging_interface,
  #                                         event_loop)
#        device_discovery.start_device_discovery(network_config=(ip, network),
 #                                               port=app_config['discovery_port'], device_list=device_list)

def create_device_template(app_config: dict, ip_address: str) -> DeviceList:
    """
    Generates a device to represent the currently running executor service.
    Additionally, this device is appended to a newly created DeviceList, which is then returned.
    """
    d = DeviceTemplate(name=app_config['executor_name'],
                       idn=app_config['executor_type'],
                       type=input_str_to_device_type(app_config['executor_type']),
                       protocol=input_str_to_protocol(app_config['protocol']),
                       port=f'{ip_address}:{app_config["discovery_port"]}',
                       status=DeviceStatus.ONLINE,
                       additional=get_executor_info())

    device_list = DeviceList()
    device_list.add(d)
    return device_list


async def setup_messaging_interface(device_list: DeviceList, container_device: DeviceTemplate, test_parser,
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


async def main(event_loop):
    # Load configuration json
    app_config = load_app_config()

    print_start_dialog()
    print_app_config(app_config)
    network_card = print_network_card_selection()

    # Get network properties of selected network card
    ip, netmask, network = get_network_info(network_card)

    # Initiate test queue and scheduler operating on this list
    test_queue = TestQueue(logger)

    # OLD

    network_handler = Setup.setup_network(ip_address=ip, port_send=PORT_SEND, port_recv=PORT_RECV)
    db_handler = Setup.create_initial_db_scheme(DB_NAME, True)
    memory_inst_dict = {'test_ctr': 0, 'label': 'FRAM_ROHM1', 'comment': 'Nix',
                        'memory_type_label': 'FRAM_Rohm_MR48V256C'}
    db_handler.add_memory_instance(memory_inst_dict)
    memory_inst_dict = {'test_ctr': 0, 'label': 'FRAM_ROHM2', 'comment': 'Nix',
                        'memory_type_label': 'FRAM_Rohm_MR48V256C'}
    db_handler.add_memory_instance(memory_inst_dict)

    zync_ip_config = IPConfig(ip="132.231.14.92", port=PORT_SEND)
    scheduler = TestScheduler(test_queue=test_queue, time_between_tests_in_ms=app_config['scheduler_time_interval'], network_handler=network_handler,
                              server_ip=zync_ip_config)

    # OLD


    test_parser = register_test_types()


    device_list = create_device_template(app_config, ip)
    add_all_devices(device_list=device_list, folder=DEV_CONFIG_FOLDER)

    container_device = device_list.get_first_element()

    # Setup callback handler and generic test interface. Register current service at the backend
    messaging_interface = await setup_messaging_interface(device_list, container_device, test_parser,
                                                          scheduler, app_config['nats_broker_ip'],
                                                          int(app_config['nats_broker_port']))

    # Start heartbeat service continuously requesting the availability of the device in the device list.
    setup_heartbeat_service(app_config=app_config, device_list=device_list, messaging_interface=messaging_interface)

    # Start device discovery in the local network
    setup_device_discovery(app_config, messaging_interface, ip, network, device_list)


if __name__ == '__main__':
    event_loop = asyncio.new_event_loop()
    event_loop.run_until_complete(main(event_loop))
    event_loop.run_forever()
