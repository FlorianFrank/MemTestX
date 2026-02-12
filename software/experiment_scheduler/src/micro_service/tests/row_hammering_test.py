"""
Module contains state machine to execute write row hammering tests.
"""
import time

from communication_interfaces.interface_wrapper import InterfaceWrapper
from communication_interfaces.ip_definitions import IPConfig
from db_handler import logger
from model.result import Result
from test_scheduling.memory_test import MemoryTest
from tests.reliability_test import ReliabilityTest


class RowHammeringTest(MemoryTest):
    def __init__(self, communication_interface: InterfaceWrapper, server_ip: IPConfig, config: dict, multithread=False) -> None:
        """Initialize RowHammeringTest with config and optional multithread/log_level settings."""
        super().__init__(communication_interface, server_ip, config, multithread)


    def init(self) -> None:
        """Initialize the row hammering test."""
        logger.info("Init row hammering test.")
        src = self.config['testData']
        dict_row_hammering = {
            "hammeringIterations": src.get("hammerIterations"),
            "hammeringDistance": src.get("addressOffset"),
            "tWaitBetweenHammering": src.get("waitBetweenHammering")
        }

        self._command_dict =   {
            "puf_type": "rowHammering",
            **MemoryTest.get_dict_all_tests(src),
            **dict_row_hammering,
            **ReliabilityTest.get_dict_tests_reliable(src), # Use default timing
        }
        super().init()

    def run(self, repeated=False, stop_condition=None) -> None:
        """Execute the row hammering test."""
        super().run(repeated, stop_condition)
        logger.info("Run row hammering test.")

    def fetch_result(self) -> Result:
        """Fetch the test results."""
        pass

    def get_progress(self) -> int:
        """Fetch the test results."""
        return  self._progress
