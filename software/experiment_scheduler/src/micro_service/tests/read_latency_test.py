"""
Module contains state machine to execute read latency tests.
"""
from communication_interfaces.interface_wrapper import InterfaceWrapper
from communication_interfaces.ip_definitions import IPConfig
from db_handler import logger
from model.result import Result
from test_scheduling.memory_test import MemoryTest


class ReadLatencyTest(MemoryTest):
    def __init__(self, communication_interface: InterfaceWrapper, server_ip: IPConfig, config: dict, multithread=False) -> None:
        """Initialize RowHammeringTest with config and optional multithread/log_level settings."""
        super().__init__(communication_interface, server_ip, config, multithread)


    def init(self) -> None:
        """Initialize the latency variation test."""
        logger.info("Initializing latency variation test.")
        src = self.config['testData']
        dict_read_latency = {
            "init_value": src.get("writeValue"),
            "puf_value": src.get("writeValue"),
        }

        self._command_dict =   {
            "puf_type": "readLatency",
            **MemoryTest.get_dict_all_tests(src),
            **MemoryTest.get_dict_latency(src),
            **dict_read_latency }
        super().init()


    def run(self, repeated=False, stop_condition=None) -> None:
        """Execute the read latency test."""
        logger.info("Run read latency violation test.")
        super().run(repeated, stop_condition)

    def fetch_result(self) -> Result:
        """Fetch the test results."""
        pass