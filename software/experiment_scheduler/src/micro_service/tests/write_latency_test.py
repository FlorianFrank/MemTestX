"""
Module contains state machine to execute write latency tests.
"""
import time

from communication_interfaces.interface_wrapper import InterfaceWrapper
from communication_interfaces.ip_definitions import IPConfig
from model.result import Result
from test_scheduling.memory_test import MemoryTest


class WriteLatencyTest(MemoryTest):
    def __init__(self, communication_interface: InterfaceWrapper, server_ip: IPConfig, config: dict, multithread=False) -> None:
        """Initialize WriteLatencyTest with config and optional multithread/log_level settings."""
        super().__init__(communication_interface, server_ip, config, multithread)

    def init(self) -> None:
        """Initialize the write latency test."""
        src = self.config['testData']
        dict_write_latency = {
            "init_value": src.get("initializationValue"),
            "puf_value": src.get("writeValue"),
        }
        self._command_dict = {
            "puf_type": "writeLatency",
            **MemoryTest.get_dict_all_tests(src),
            **MemoryTest.get_dict_latency(src),
            **dict_write_latency
        }

        super().init()

    def run(self, repeated=False, stop_condition=None) -> None:
        """Execute the row hammering test."""
        super().run(repeated, stop_condition)

    def fetch_result(self) -> Result:
        """Fetch the test results."""
        pass

    def get_progress(self) -> int:
        """Fetch the test results."""
        return  self._progress
