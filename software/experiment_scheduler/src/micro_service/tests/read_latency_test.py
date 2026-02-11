"""
Module contains state machine to execute read latency tests.
"""
import time

from communication_interfaces.interface_wrapper import InterfaceWrapper
from communication_interfaces.ip_definitions import IPConfig
from model.result import Result
from test_scheduling.memory_test import MemoryTest


class ReadLatencyTest(MemoryTest):
    def __init__(self, communication_interface: InterfaceWrapper, server_ip: IPConfig, config: dict, multithread=False) -> None:
        """Initialize RowHammeringTest with config and optional multithread/log_level settings."""
        super().__init__(communication_interface, server_ip, config, multithread)


    def init(self) -> None:
        """Initialize the row hammering test."""
        super().init()
        #self._cmd_

    def run(self, repeated=False, stop_condition=None) -> None:
        """Execute the read latency test."""
        super().run(repeated, stop_condition)

    def fetch_result(self) -> Result:
        """Fetch the test results."""
        pass

    def get_progress(self) -> int:
        """Fetch the test results."""
        return  self._progress
