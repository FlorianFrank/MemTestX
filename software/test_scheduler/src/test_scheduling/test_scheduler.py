import datetime
import json
import threading
import time
from typing import Optional

from definitions import DB_NAME, Command, DEFAULT_PATH, SCHEDULER_THREAD_TIMEOUT_IN_S
from file_handler import MeasureFileHandler
from interface_wrapper import InterfaceWrapper
from measure_device_wrapper import PowerSupplyWrapper
from network_handler import IPConfig
from src.db_handler import DBHandler, logger
from test_defines import TestRange, Test, TestState, test_type_to_str, TestType, TestInternalState
from test_queue import TestQueue


class TestScheduler:
    """
    Manages the scheduling and execution of memory tests.
    Handles test initialization, communication with devices,
    measurement data collection, voltage/current adjustments,
    and updates to the database. Can run in a dedicated thread
    for continuous scheduling.
    """
    def __init__(self, test_queue: Optional[TestQueue], time_between_tests_in_ms: int, server_ip: IPConfig,
                 comm_interface: InterfaceWrapper):
        self._test_range: TestRange = TestRange([], time_between_tests_in_ms)
        self._test_thread: Optional[threading.Thread] = None
        self._stop_test_thread: bool = False
        self._current_test_idx: int = 0
        self._current_test: Optional[Test] = None
        self._db_handler: Optional[DBHandler] = None
        self._server_ip: IPConfig = server_ip
        self._test_queue: TestQueue = test_queue
        self.communication_interface: InterfaceWrapper = comm_interface
        self.db_updated = False
        self._measure_device = None

    def add_test(self, test: Test):
        self._test_range.lists.append(test)

    def start_test(self):
        """
        Prepares and starts the current test by initializing the database entry,
        configuring measurement devices, setting timing parameters, and sending
        the start command via the communication interface.
        """
        command_dict = dict()

        self._db_handler = DBHandler(DB_NAME)
        self._db_handler.initialize()
        timing_parameters = self._db_handler.get_timing_parameter(
            self._test_range.lists[self._current_test_idx].test_template.memory_type_name)
        memory_config = self._db_handler.get_memory_config(
            self._test_range.lists[self._current_test_idx].test_template.memory_type_name)

        command_dict['puf_type'] = test_type_to_str(self._test_range.lists[self._current_test_idx].test_template.type)
        command_dict['start_addr'] = memory_config['min_addr']
        command_dict['stop_addr'] = memory_config['max_addr']
        command_dict['tWaitAfterInit'] = timing_parameters['tWaitAfterInit']

        if self._test_range.lists[self._current_test_idx].test_template.type == TestType.VOLTAGE_READ or \
                self._test_range.lists[self._current_test_idx].test_template.type == TestType.VOLTAGE_WRITE:
            if self._measure_device is None:
                logger.info(f"Initialize power supply")
                self._measure_device = PowerSupplyWrapper()
                self._measure_device.initialize()
                time.sleep(0.2)

            self._measure_device.power_supply_default_settings(default_current=memory_config['current'],
                                                               default_voltage=memory_config['voltage'])

        # Default Write Parameters
        command_dict['ce_driven'] = bool(timing_parameters['ceDrivenWrite'])
        command_dict['tStartDefault'] = timing_parameters['tStartWrite']
        command_dict['tNextWriteDefault'] = timing_parameters['tNextWrite']
        command_dict['tACDefault'] = timing_parameters['tACWrite']
        command_dict['tASDefault'] = timing_parameters['tASWrite']
        command_dict['tAHDefault'] = timing_parameters['tAHWrite']
        command_dict['tPWDDefault'] = timing_parameters['tPWDWrite']
        command_dict['tDSDefault'] = timing_parameters['tDSWrite']
        command_dict['tDHDefault'] = timing_parameters['tDHWrite']

        # Default Read Parameters
        command_dict['tNextRead'] = timing_parameters['tNextRead']
        command_dict['ceDrivenRead'] = bool(timing_parameters['ceDrivenRead'])
        command_dict['tStartReadDefault'] = timing_parameters['tStartRead']
        command_dict['tASReadDefault'] = timing_parameters['tASRead']
        command_dict['tAHReadDefault'] = timing_parameters['tAHRead']
        command_dict['tOEDDefault'] = timing_parameters['tOEDRead']
        command_dict['tPRCDefault'] = timing_parameters['tPRCRead']
        command_dict['tCEOEEnableDefault'] = timing_parameters['tCEOEEnableRead']
        command_dict['tCEOEDisableDefault'] = timing_parameters['tCEOEDisableRead']

        # Adjusted Write Parameters
        command_dict['tStartAdjusted'] = timing_parameters['tStartWrite']
        command_dict["tNextWriteAdjusted"] = timing_parameters['tNextWrite']
        command_dict["tACAdjusted"] = timing_parameters['tACWrite']
        command_dict["tASAdjusted"] = timing_parameters['tASWrite']
        command_dict["tAHAdjusted"] = timing_parameters['tAHWrite']
        command_dict["tPWDAdjusted"] = timing_parameters['tPWDWrite']
        command_dict["tDSAdjusted"] = timing_parameters['tDSWrite']
        command_dict["tDHAdjusted"] = timing_parameters['tDHWrite']

        # Adjusted Read Parameters
        command_dict['tStartReadAdjusted'] = timing_parameters['tStartRead']
        command_dict['tASReadAdjusted'] = timing_parameters['tASRead']
        command_dict['tAHReadAdjusted'] = timing_parameters['tAHRead']
        command_dict['tOEDAdjusted'] = timing_parameters['tOEDRead']
        command_dict['tPRCAdjusted'] = timing_parameters['tPRCRead']
        command_dict['tCEOEEnableAdjusted'] = timing_parameters['tCEOEEnableRead']
        command_dict['tCEOEDisableAdjusted'] = timing_parameters['tCEOEDisableRead']

        for key, value in self._test_range.lists[self._current_test_idx].test_template.parameters.items():
            if key == 'init_value':
                command_dict['init_value'] = value
            elif key == 'puf_value':
                command_dict['puf_value'] = value
            elif key == 'tStartWrite':
                command_dict['tStartAdjusted'] += value
            elif key == 'tNextWrite':
                command_dict['tNextWriteAdjusted'] += value
            elif key == 'tACWrite':
                command_dict['tACAdjusted'] += value
            elif key == 'tASWrite':
                command_dict['tASAdjusted'] += value
            elif key == 'tAHWrite':
                command_dict['tAHAdjusted'] += value
            elif key == 'tPWDWrite':
                command_dict['tPWDAdjusted'] += value
            elif key == 'tDSWrite':
                command_dict['tDSAdjusted'] += value
            elif key == 'tDHWrite':
                command_dict['tDHAdjusted'] += value

            elif key == 'tStartRead':
                command_dict['tStartReadAdjusted'] += value
            elif key == 'tASRead':
                command_dict['tASReadAdjusted'] += value
            elif key == 'tAHRead':
                command_dict['tAHReadAdjusted'] += value
            elif key == 'tOED':
                command_dict['tOEDAdjusted'] += value
            elif key == 'tPRC':
                command_dict['tPRCAdjusted'] += value
            elif key == 'tCEOEEnable':
                command_dict['tCEOEEnableAdjusted'] += value
            elif key == 'tCEOEDisable':
                command_dict['tCEOEDisableAdjusted'] += value
            else:
                if key == 'tWaitBetweenHammering' or key == 'hammeringIterations' or key == 'hammeringDistance':
                    command_dict[key] = value
                else:
                    logger.error(f"Unknown PUF key parameter {key}")

        cmd = (json.dumps(command_dict).replace(', ', ",\n").
               replace('}', '\n}').
               replace('{', '{\n'))
        logger.info(f'Send command {cmd}')

        self._test_range.lists[self._current_test_idx].state = TestState.WAITING_FOR_RESPONSE
        self._test_range.lists[self._current_test_idx].measure_file.initialize()
        self._test_range.lists[self._current_test_idx].measure_file.start_store_data_thread()
        self._db_handler.add_test_entry(self._test_range.lists[self._current_test_idx])
        time.sleep(0.1)
        if self._measure_device:
            self._measure_device.turn_on()
        self.communication_interface.send_config(Command.CMD_START_MEASUREMENT, self._server_ip, cfg=command_dict)

    @staticmethod
    def create_file_name(test: Test):
        """
        Generates a unique filename for storing measurement data using the current timestamp and some experiment parameters.
        """
        ts = time.time()
        return test_type_to_str(test.test_template.type) + '_' + test.memory_label.replace('.', '').strip().replace(' ',
                                                                                                                    '') + '_' + str(
            ts) + ".csv"

    def adjust_electrical_params(self, voltage_offset, current_offset):
        """
        Adjusts the voltage and current parameters of a connected measurement device, controlled by our
        instrument control lib. Required when performing measurement under voltage and current variations.
        """
        # REDUCE VOLTAGE to new value
        memory_config = self._db_handler.get_memory_config(
            self._test_range.lists[self._current_test_idx].test_template.memory_type_name)
        voltage = memory_config['voltage'] + voltage_offset
        current = memory_config['current'] + current_offset
        if not self._measure_device.change_voltage(voltage):
            logger.info(f"Hardware protection -> Shutdown power supply, disconnect "
                        f"from device and end scheduler")
            self._measure_device.disconnect()
            self._measure_device = None
            return False
        else:
            time.sleep(0.3)
            if not self._measure_device.change_current(current):
                logger.info(f"Hardware protection -> Shutdown power supply, disconnect "
                            f"from device and end scheduler")
                self._measure_device.disconnect()
                self._measure_device = None
                return False
            logger.info(f"Voltage set to {voltage} while current limit set to {current}")
            self.communication_interface.send_continue(self._server_ip)
        self._test_range.lists[self._current_test_idx].internal_state = TestInternalState.INACTIVE

    def test_scheduling_function(self):
        """
        Starts the scheduler loop in a dedicated thread.
        """
        while not self._stop_test_thread:
            if len(self._test_range.lists) > self._current_test_idx:
                if self._test_range.lists[self._current_test_idx].state == TestState.WAITING_FOR_RESPONSE:
                    logger.info(f"Waiting for response ...")
                if self._test_range.lists[self._current_test_idx].state == TestState.PROCESSING:
                    if not self.db_updated:
                        self._db_handler.update_start_ts(
                            datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                            self._test_range.lists[self._current_test_idx])
                        self.db_updated = True

                    # APPLY VOLTAGE VARIATION TESTS
                    if self._test_range.lists[self._current_test_idx].test_template.type == TestType.VOLTAGE_WRITE or \
                            self._test_range.lists[self._current_test_idx].test_template.type == TestType.VOLTAGE_READ:
                        if self._test_range.lists[self._current_test_idx].internal_state == TestInternalState.INIT:
                            logger.info(f"Memory initialization finished")
                            if 'voltage_change' in self._test_range.lists[
                                self._current_test_idx].test_template.parameters or 'current_change' in \
                                    self._test_range.lists[self._current_test_idx].test_template.parameters:
                                voltage_offset = 0
                                current_offset = 0
                                if self._test_range.lists[
                                    self._current_test_idx].test_template.type == TestType.VOLTAGE_WRITE:
                                    voltage_offset = \
                                    self._test_range.lists[self._current_test_idx].test_template.parameters[
                                        'voltage_change'] if 'voltage_change' in self._test_range.lists[
                                        self._current_test_idx].test_template.parameters else 0
                                    current_offset = \
                                        self._test_range.lists[self._current_test_idx].test_template.parameters[
                                            'current_change'] if 'current_change' in self._test_range.lists[
                                            self._current_test_idx].test_template.parameters else 0

                                self.adjust_electrical_params(voltage_offset, current_offset)

                        elif self._test_range.lists[self._current_test_idx].internal_state == TestInternalState.RUN:
                            logger.info(f"Memory run finished")
                            if 'voltage_change' in self._test_range.lists[
                                self._current_test_idx].test_template.parameters or 'current_change' in \
                                    self._test_range.lists[self._current_test_idx].test_template.parameters:
                                voltage_offset = 0
                                current_offset = 0
                                if self._test_range.lists[
                                    self._current_test_idx].test_template.type == TestType.VOLTAGE_READ:
                                    voltage_offset = \
                                        self._test_range.lists[self._current_test_idx].test_template.parameters[
                                            'voltage_change'] if 'voltage_change' in self._test_range.lists[
                                            self._current_test_idx].test_template.parameters else 0
                                    current_offset = \
                                        self._test_range.lists[self._current_test_idx].test_template.parameters[
                                            'current_change'] if 'current_change' in self._test_range.lists[
                                            self._current_test_idx].test_template.parameters else 0

                                self.adjust_electrical_params(voltage_offset, current_offset)

                        elif self._test_range.lists[self._current_test_idx].internal_state == TestInternalState.DONE:
                            logger.info(f"Memory done received")
                            self._measure_device.turn_off()

                    logger.info(f"Test is processing wait till finished ...")
                elif self._test_range.lists[self._current_test_idx].state == TestState.INACTIVE:
                    file_name = self.create_file_name(self._test_range.lists[self._current_test_idx])
                    self._test_range.lists[self._current_test_idx].measure_file = MeasureFileHandler(DEFAULT_PATH,
                                                                                                     file_name)
                    logger.info(f"Start new test and store data in {file_name}")
                    if not self.communication_interface.is_recv_thread_running():
                        self.communication_interface.start_recv_thread(self._test_range.lists[self._current_test_idx])
                    self.start_test()
                elif self._test_range.lists[self._current_test_idx].state == TestState.FINISHED:
                    if self._measure_device:
                        logger.info(f"Turn off power supply.")
                        self._measure_device.turn_off()
                    if not self.db_updated:
                        self._db_handler.update_stop_ts(
                            datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                            self._test_range.lists[self._current_test_idx])
                        self.db_updated = False
                    logger.info(f"Test Finish -> Stop network thread")
                    self.communication_interface.stop_thread()
                    self._current_test_idx += 1
                elif self._test_range.lists[self._current_test_idx].state == TestState.ERROR:
                    logger.error(f"An error occurred while executing test with index {self._current_test_idx}")
            time.sleep(self._test_range.wait_between_tests_in_ms / 1000)

    def run_scheduler_loop(self, start_in_dedicated_threads: bool = True):
        """
          Starts the scheduler loop either in a dedicated thread or the main thread.
          Currently only threaded execution is supported!!
          """
        if start_in_dedicated_threads:
            logger.info("Start Scheduling thread")
            self._stop_test_thread = False
            self._test_thread = threading.Thread(target=self.test_scheduling_function)
            self._test_thread.start()

    def stop_scheduler_loop(self):
        """
        Stops the scheduler loop and waits for the dedicated thread to finish.
        """
        logger.info("Stop Scheduler Loop")
        self._stop_test_thread = True
        self._test_thread.join(SCHEDULER_THREAD_TIMEOUT_IN_S)

    def get_test_queue(self):
        return self._test_queue
