import sys
import time

from src.utils.import_paths import set_import_paths

# Add directories to python path
set_import_paths()

from db_handler import DBHandler
from utils.logging_handler import initialize_logging
from memory_instance_handler import add_all_memory_instances_to_db
from definitions import IP_SUFFIX, PORT_SEND, PORT_RECV, DB_NAME
from network_handler import NetworkHandler, IPConfig
from setup import Setup
from tests import SampleTests

if __name__ == "__main__":

    print("\n******************************************")
    print("********** Experiment Scheduler **********")
    print("******************************************\n")

    logger = initialize_logging()

    if len(sys.argv) > 1 and sys.argv[1] == '-init_db_scheme':
        db_handler = Setup.create_initial_db_scheme(DB_NAME, clear_db=True)
        logger.info(f"Database scheme created")
    else:

        srv_ip = NetworkHandler.detect_network_interface_with_suffix(IP_SUFFIX)
        logger.info(f"Detected server ip: {srv_ip} -> Setup Network")

        network_handler = Setup.setup_network(ip_address=srv_ip, port_send=PORT_SEND, port_recv=PORT_RECV)

        logger.info("Setup database")

        db_handler = DBHandler(DB_NAME)
        db_handler.initialize()

        add_all_memory_instances_to_db(db_handler, logger)

        zync_ip_config = IPConfig(ip=IP_SUFFIX, port=PORT_SEND)
        time.sleep(4)

        SampleTests.sample_test_execution_zync()

        # Start infinite loop to let the scheduler start different experiments.
        while True:
            logger.info("Running")
            time.sleep(1)
