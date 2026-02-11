import json
import time

from communication_interfaces.interface_wrapper import InterfaceWrapper
from communication_interfaces.ip_definitions import IPConfig
from db_handler import DBHandler, logger
from message_handling.file_handler import MeasureFileHandler
from model.result import Result
from test_scheduling.microservicetest import MicroserviceTest
from utils.definitions import DB_NAME, Command, DEFAULT_PATH


class MemoryTest(MicroserviceTest):
    """ Test class only executed when performing Microservice Tests"""
    def __init__(self, communication_interface: InterfaceWrapper, server_ip: IPConfig, config: dict, multithread=False) -> None:
        super().__init__(config, multithread)
        self._db_handler = None
        self._progress = 0
        self._communication_interface = communication_interface
        self._server_ip = server_ip
        self._command_dict: dict | None = None

    def init(self) -> None:
        super().init()
        self._db_handler = DBHandler(DB_NAME)
        self._db_handler.initialize()

        cmd = (json.dumps(self._command_dict).replace(', ', ",\n").
               replace('}', '\n}').
               replace('{', '{\n'))
        logger.info(f'Parsed Command {cmd}')

        ts = time.time()
        file_name = f"{self._command_dict['puf_type']}_{self.config['instanceID']}_{ts}.csv"
        self.measure_file = MeasureFileHandler(DEFAULT_PATH, file_name)
        if not self.measure_file.initialize():
            logger.error("Failed to initialize measure file")
        self.measure_file.start_store_data_thread()


    def run(self, repeated=False, stop_condition=None) -> None:
        """Execute the read latency test."""
        super().run(repeated, stop_condition)
        if not self._communication_interface.is_recv_thread_running():
            self._communication_interface.start_recv_thread(self)
        self._communication_interface.send_config(Command.CMD_START_MEASUREMENT, self._server_ip, cfg=self._command_dict)

    def fetch_result(self) -> Result:
        """Fetch the test results."""
        pass

    def get_progress(self) -> int:
        """Fetch the test results."""
        return self._progress

    def update_progress(self, current_address: int) -> None:
        """Update progress based on the current address."""
        if not self._command_dict:
            return

        start = self._command_dict.get('start_addr')
        stop = self._command_dict.get('stop_addr')

        if start is not None and stop is not None and stop > start:
            progress = int(((current_address - start) / (stop - start)) * 100)
            self._progress = max(0, min(100, progress))
            if self._progress_callback:
                self._progress_callback(self.fetch_result())

    @staticmethod
    def get_dict_all_tests(src: dict) -> dict:
        """Map JSON received from GUI/backend to the format acceptable by the FPGA or microcontroller.
        TODO: In a next version the fields must be harmonized.
        """
        return {
            "start_addr": src.get("startAddress"),
            "stop_addr": src.get("stopAddress"),

            "tWaitAfterInit": src.get("tWaitAfterInitTimingDefault"),
            "ce_driven": src.get("ceDrivenWrite"),
            "ceDrivenRead": src.get("ceDrivenRead"),

            "tStartDefault": src.get("tStartWriteTimingDefault"),
            "tNextWriteDefault": src.get("tNextWriteTimingDefault"),
            "tACDefault": src.get("tACWriteTimingDefault"),
            "tASDefault": src.get("tASWriteTimingDefault"),
            "tAHDefault": src.get("tAHWriteTimingDefault"),
            "tPWDDefault": src.get("tPWDWriteTimingDefault"),
            "tDSDefault": src.get("tDSWriteTimingDefault"),
            "tDHDefault": src.get("tDHWriteTimingDefault"),

            "tNextRead": src.get("tNextReadTimingDefault"),
            "tStartReadDefault": src.get("tStartReadTimingDefault"),
            "tASReadDefault": src.get("tASReadTimingDefault"),
            "tAHReadDefault": src.get("tAHReadTimingDefault"),
            "tOEDDefault": src.get("tOEDReadTimingDefault"),
            "tPRCDefault": src.get("tPRCReadTimingDefault"),
            "tCEOEEnableDefault": src.get("tCEOEEnableReadTimingDefault"),
            "tCEOEDisableDefault": src.get("tCEOEDisableReadTimingDefault"),
        }

    @staticmethod
    def get_dict_latency(src: dict) -> dict:
        """Parses the parameters received from the GUI and transforms it "
         to a dict acceptable by the FPGA (TODO should be harmonized in the next version)"""
        return {
            "tStartAdjusted": src.get("tStartWriteTimingAdjusted"),
            "tNextWriteAdjusted": src.get("tNextWriteTimingAdjusted"),
            "tACAdjusted": src.get("tACWriteTimingAdjusted"),
            "tASAdjusted": src.get("tASWriteTimingAdjusted"),
            "tAHAdjusted": src.get("tAHWriteTimingAdjusted"),
            "tPWDAdjusted": src.get("tPWDWriteTimingAdjusted"),
            "tDSAdjusted": src.get("tDSWriteTimingAdjusted"),
            "tDHAdjusted": src.get("tDHWriteTimingAdjusted"),

            "tStartReadAdjusted": src.get("tStartReadTimingAdjusted"),
            "tASReadAdjusted": src.get("tASReadTimingAdjusted"),
            "tAHReadAdjusted": src.get("tAHReadTimingAdjusted"),
            "tOEDAdjusted": src.get("tOEDReadTimingAdjusted"),
            "tPRCAdjusted": src.get("tPRCReadTimingAdjusted"),
            "tCEOEEnableAdjusted": src.get("tCEOEEnableReadTimingAdjusted"),
            "tCEOEDisableAdjusted": src.get("tCEOEDisableReadTimingAdjusted"),
        }