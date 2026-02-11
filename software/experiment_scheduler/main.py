import sys
import time
from typing import Optional
from src.micro_service.microservice_entry_point import run_microservice

from communication_interfaces.interface_wrapper import InterfaceWrapper
from communication_interfaces.ip_definitions import IPConfig
from communication_interfaces.network_handler import NetworkHandler
from communication_interfaces.serial_handler import SerialHandler, DEFAULT_BAUDRATE
from db_handler import DBHandler
from src.utils.import_paths import set_import_paths
from test_scheduling.test_config_parser import TestConfigParser
from test_scheduling.test_scheduler import TestScheduler
from utils.definitions import DB_NAME, SCHEDULER_IP, PORT_SEND, NIC_SUFFIX, PORT_RECV, TIME_BETWEEN_TESTS_IN_MS
from utils.logging_handler import initialize_logging
from utils.memory_instance_handler import add_all_memory_instances_to_db
from utils.setup import Setup

# Add directories to python path
set_import_paths()


def select_network_interface_and_setup_scheduler(platform: str, run_microservice: bool):
    """
    Selects the appropriate communication interface based on the test platform
    and initializes a TestScheduler instance with the configured setup.
    For the ZCU102 an Ethernet interface will be selected for the STM32F429 a UART interface.

    Args:
        platform (str): Name of the hardware platform (e.g., "Ultrascale ZCU102" or "STM32F429").

    Returns:
        TestScheduler: Configured scheduler instance ready to handle test execution.
    """
    comm_interface: Optional[InterfaceWrapper] = None
    database_handler = DBHandler(DB_NAME)
    database_handler.initialize()
    zync_ip_configuration = IPConfig(ip=SCHEDULER_IP, port=PORT_SEND)
    if platform == "Ultrascale ZCU102":
        srv_ip_addr = NetworkHandler.detect_network_interface_with_suffix(NIC_SUFFIX)
        logger.info(f"Detected server ip: {srv_ip_addr} -> Setup Network")
        comm_interface = Setup.setup_network(ip_address=srv_ip_addr, port_send=PORT_SEND, port_recv=PORT_RECV)
    elif platform == "STM32F429-DISC1":
        serial_ports = SerialHandler.find_usbmodem_ports()
        logger.info(f"Detected serial ports {serial_ports} -> select first from list")
        if len(serial_ports) == 0:
            logger.error("Error could not detect any serial port! -> Exit program")
            exit(1)
        comm_interface = SerialHandler(serial_ports[0], DEFAULT_BAUDRATE)
    print(zync_ip_configuration.ip)
    return TestScheduler(test_queue=None, time_between_tests_in_ms=TIME_BETWEEN_TESTS_IN_MS, server_ip=zync_ip_configuration,
                         comm_interface=comm_interface, run_microservices=run_microservice)


if __name__ == "__main__":

    print("\n******************************************")
    print("********** Experiment Scheduler **********")
    print("******************************************\n")

    logger = initialize_logging()

    if len(sys.argv) > 1 and sys.argv[1] == '-init_db_scheme':
        db_handler = Setup.create_initial_db_scheme(DB_NAME, clear_db=True)
        db_handler.initialize()
        logger.info(f"Database scheme created")
        add_all_memory_instances_to_db(db_handler, logger)
    elif len(sys.argv) > 1 and sys.argv[1] == '-run_microservice':
        scheduler = select_network_interface_and_setup_scheduler("Ultrascale ZCU102", run_microservice=True)
        run_microservice(logger, scheduler)
    else:
        config_file = None
        refresh_memories = False
        for arg in sys.argv[1:]:
            if '-config_file' in arg:
                config_file = arg.split('=')[1]
            if '-refresh_memories' in arg:
                refresh_memories = True
        if not config_file:
            logger.error("No config file provided (specify with -config_file)")
            exit(1)

        parser = TestConfigParser(config_file)
        parser.parse_config()

        logger.info("Setup database")

        db_handler = DBHandler(DB_NAME)
        db_handler.initialize()
        if refresh_memories:
            add_all_memory_instances_to_db(db_handler, logger)

        # Add tests to scheduler
        scheduler = select_network_interface_and_setup_scheduler(parser.get_platform(),  run_microservice=False)
        parser.initialize_test_scheduler(scheduler)
        scheduler.run_scheduler_loop()

        while True:
            logger.info("Running")
            time.sleep(1)
