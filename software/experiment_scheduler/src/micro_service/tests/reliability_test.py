"""
Module contains state machine to execute reliability tests.
"""
import time

from communication_interfaces.interface_wrapper import InterfaceWrapper
from communication_interfaces.ip_definitions import IPConfig
from db_handler import logger
from model.result import Result
from test_scheduling.memory_test import MemoryTest


class ReliabilityTest(MemoryTest):
    def __init__(self, communication_interface: InterfaceWrapper, server_ip: IPConfig, config: dict, multithread=False) -> None:
        """Initialize RowHammeringTest with config and optional multithread/log_level settings."""
        super().__init__(communication_interface, server_ip, config, multithread)

    def init(self) -> None:
        """Initialize the row hammering test."""
        logger.info("Init reliability test.")
        src = self.config['testData']
        self._command_dict = {
            "puf_type": "reliable",
            **MemoryTest.get_dict_all_tests(src),
            **ReliabilityTest.get_dict_tests_reliable(src),
        }
        super().init()


    def run(self, repeated=False, stop_condition=None) -> None:
        """Execute the row hammering test."""
        logger.info("Run reliability test.")
        super().run(repeated, stop_condition)

    def fetch_result(self) -> Result:
        """Fetch the test results."""
        pass


    @staticmethod
    def get_dict_tests_reliable(src):
        return {
            "tStartAdjusted": src.get("tStartWriteTimingDefault"),
            "tNextWriteAdjusted": src.get("tNextWriteTimingDefault"),
            "tACAdjusted": src.get("tACWriteTimingDefault"),
            "tASAdjusted": src.get("tASWriteTimingDefault"),
            "tAHAdjusted": src.get("tAHWriteTimingDefault"),
            "tPWDAdjusted": src.get("tPWDWriteTimingDefault"),
            "tDSAdjusted": src.get("tDSWriteTimingDefault"),
            "tDHAdjusted": src.get("tDHWriteTimingDefault"),

            "tStartReadAdjusted": src.get("tStartReadTimingDefault"),
            "tASReadAdjusted": src.get("tASReadTimingDefault"),
            "tAHReadAdjusted": src.get("tAHReadTimingDefault"),
            "tOEDAdjusted": src.get("tOEDReadTimingDefault"),
            "tPRCAdjusted": src.get("tPRCReadTimingDefault"),
            "tCEOEEnableAdjusted": src.get("tCEOEEnableReadTimingDefault"),
            "tCEOEDisableAdjusted": src.get("tCEOEDisableReadTimingDefault"),
            "init_value": src.get("initializationValue"),
            "puf_value": (
                src.get("initializationValue") * 2
                if src.get("initializationValue") is not None
                else None
            )
        }