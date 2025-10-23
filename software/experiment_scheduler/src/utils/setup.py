from db_handler import DBHandler, logger
from json_parser import JSONParser
from network_handler import NetworkHandler

MEM_CONFIG_FILE_DIR = 'config_files/memory_configs'
MEM_TIMING_FILE_DIR = 'config_files/memory_timings'


class Setup:
    @staticmethod
    def create_initial_db_scheme(db_name: str, clear_db: bool = False) -> DBHandler:
        """
        Creates and initializes the database schema with memory and timing configurations.

        This method reads memory and timing configurations from JSON files,
        initializes the database, and populates the tables accordingly.

        Args:
            db_name (str): The name of the database.
            clear_db (bool): If True, clears all tables before initializing.

        Returns:
            DBHandler: An instance of DBHandler connected to the initialized database.
        """
        db_handler = DBHandler(db_name)
        memory_config_list = JSONParser.grep_all_json_files_in_directory(MEM_CONFIG_FILE_DIR)
        memory_files = []
        for file in memory_config_list:
            memory_files.append(JSONParser.read_json_file(MEM_CONFIG_FILE_DIR, file))

        timing_config_dir = JSONParser.grep_all_json_files_in_directory(MEM_CONFIG_FILE_DIR)
        timing_files = []
        for file in timing_config_dir:
            timing_files.append(JSONParser.read_json_file(MEM_TIMING_FILE_DIR, file))

        try:
            # Initialize the database and create tables
            db_handler.initialize()
            if clear_db:
                db_handler.clear_all_tables()
            db_handler.create_memory_table()
            db_handler.create_timing_parameter_table()
            db_handler.create_memory_instance_table()
            db_handler.create_test_table()

            # Add memory types and timing parameters
            for mem_config in memory_files:
                db_handler.add_memory_type(mem_config)

            for t_config in timing_files:
                db_handler.add_memory_timing_parameter(t_config)
        except Exception as e:
            logger.error(f"An error occurred: {e}")

        finally:
            pass  # Ensure the database connection is closed if necessary

        return db_handler

    @staticmethod
    def setup_network(ip_address: str, port_send: int, port_recv: int) -> NetworkHandler:
        """
        Sets up and initializes the network handler.

        Args:
            ip_address (str): The IP address to bind to.
            port_send (int): The port used for sending data.
            port_recv (int): The port used for receiving data.

        Returns:
            NetworkHandler: An initialized NetworkHandler instance.
        """
        network_handler = NetworkHandler()
        network_handler.initialize(ip_address, port_send, port_recv)
        return network_handler

    def start_test_scheduler(self):
        """
        Placeholder method to start the test scheduler.

        This method is currently not implemented.
        """
        pass
