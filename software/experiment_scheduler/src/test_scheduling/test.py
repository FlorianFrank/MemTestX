from __future__ import annotations

import logging
import threading
import time
from abc import ABC, abstractmethod
from enum import Enum

from config import Config
from result import Result


class TestStatus(Enum):
    """
    The various possible statuses of the test execution.
    """

    IDLE = 0
    INIT = 1
    RUNNING = 2
    STOPPED = 3
    FAILED = 4


class Test(ABC):
    """
    The base class of all tests. It defines an interface to work with tests and provides a fixed test procedure.
    Always use this class as a superclass for your own tests and implement all abstract methods.
    If you want to override a non-abstract method be sure to call the corresponding super method and do not change what
    the method does already.
    """

    def __init__(self, config: Config, multithread=False, log_level=logging.DEBUG) -> None:
        """
        Constructs a new test object. Declare all used attributes here, even if they are uninitialized for now.
        Always call super().__init__() in your base classes!

        :param multithread: Whether this test should use multithreading.
        :param log_level: The level of logs to be shown.
        """
        self.config: Config = config
        self.repeated: bool = False
        self.stop_condition: bool = False
        self.status: TestStatus = TestStatus.IDLE
        self.timestamp: dict = {"start": 0.0, "stop": 0.0}
        self.progress_counter = 0
        self.__climate_chamber: None #ClimateChamberControl | None = None
        self._progess_callback = None

        #logging.set_log_level(log_level)

        self.thread: threading.Thread | None = None
        if multithread:
            self.thread = threading.Thread(target=self.execute, args=(1,))

    def start_test(self) -> None:
        """
        Starts the test by logging the start time. If multithreading is enabled it starts the thread.

        :return: None
        """
        self.timestamp['start'] = time.time()
        logging.info("Start: " + str(self.timestamp['start']))

        if self.thread:
            self.thread.start()
        else:
            self.execute(None)

    def execute(self, thread_param) -> None:
        """
        Executes the test by first initializing it, then running the test and after a successful execution stopping and
        deinitializing. If there is an error while executing the test, the status gets set to FAILED and the error
        propagates.

        :param thread_param: TODO: What is this for?
        :return: None
        """
        self.init()
        #   try:
        if self.repeated:
            while self.stop_condition:
                self.run()
        else:
            self.run()
        self.done()

    #     except Exception as e:
    #        self.status = TestStatus.FAILED
    #       raise e

    @abstractmethod
    def init(self) -> None:
        """
        Initializes the test. Each concrete test needs to override this method and implement its own init procedure.

        :return: None
        """
        logging.info('state=initialize')
        self.status = TestStatus.INIT

    @abstractmethod
    def run(self, repeated=False, stop_condition=None) -> None:
        """
        Executes the actual test.

        :param repeated: Whether or not this test is repeated.
        :param stop_condition: The loop condition if this test is repeated. Is checked before every run.
        :return: None
        """
        logging.info('state=run')
        self.status = TestStatus.RUNNING

    def done(self) -> None:
        """
        Cleans up after a successful test execution. Stops the timer and exits the test.

        :return: None
        """
        self.timestamp['stop'] = time.time()
        logging.info("Stop: " + str(self.timestamp['stop']) + " Difference: " + str(
            self.timestamp['stop'] - self.timestamp['start']) + " seconds")

        self._finish_progress()

        logging.info('state=done')
        self.status = TestStatus.STOPPED

    def is_active(self) -> bool:
        """
        Returns whether or not this test is active, e.g. is initialized or running.

        :return: True if and only if the test is currently running.
        """
        return self.status in [TestStatus.INIT, TestStatus.RUNNING]

    @abstractmethod
    def fetch_result(self) -> Result:
        """
        Returns the result after a successful test execution. Change the type hint in the base class to the specific
        result type of your test.

        :return: The Result object which contains the measured data.
        """
        pass

    def set_climate_chamber_values(self, temperature: float, humidity: float) -> None:
        """
        Sets the temperature and humidity of the climate chamber. Can be only executed after a successful setup of the
        climate chamber. If one of the values does not need to be changed, set it to None for it to be ignored.

        :param temperature: The temperature to be set.
        :param humidity: The humidity to be set.
        :return: None
        """
        if temperature is not None:
            pass
          #  self.__climate_chamber.set_target_temperature(temperature)
        if humidity is not None:
            pass
         #   self.__climate_chamber.set_target_humidity(humidity)
        #self.__climate_chamber.start_execution()

        #self.__wait_for_climate_chamber(temperature, humidity)

    def __wait_for_climate_chamber(self, temperature: float, humidity: float) -> None:
        """
        Waits for the climate chamber to reach the given values.
        TODO: Change to optimized version

        :param temperature: The temperature to be reached.
        :param humidity: The humidity to be reached.
        :return: None
        """

        def temperature_reached():
            pass

        #     return math.isclose(self.__climate_chamber.get_current_temperature(), temperature, abs_tol=0.5) \
        #        or temperature is None

        def humidity_reached():
            pass
            # return math.isclose(self.__climate_chamber.get_current_humidity(), humidity, abs_tol=0.5) \
            #   or humidity is None

        while not temperature_reached() or not humidity_reached():
            print(f'Waiting for climate chamber to get to the target values')
            time.sleep(10)

    def _init_progress(self, length: int) -> None:
        """
        Initis the progress indicator as the test just started. Must be called right before starting the test execution.

        :param length: The number of steps in the next test execution.
        :return: None
        """
        self.test_length = length
        self.progress_counter = 0

    def register_progress_callback(self, callback_func) -> None:
        """
        Registers a function that is called every time there is progress in the test execution. This function should
        expect exactly one argument, which is the result object of the current test, filled with the values so far.
        """
        self._progess_callback = callback_func

    def _progress(self) -> None:
        """
        If progress is made in the test, i.e. a step of the self.test_length steps is done, this method advances the
        progress indicator. Always call this after the execution of a test step.

        :return: None
        """
        self.progress_counter += 1
        logging.info(f'{round((self.progress_counter / self.test_length) * 100, 1)} %')
        if self._progess_callback is not None:
            self._progess_callback(self.fetch_result())

    def _finish_progress(self) -> None:
        """
        If the test finished, this clears up the progress indicator.

        :return: None
        """
        pass

    def __del__(self) -> None:
        """
        Deinitializes the test.

        :return: None
        """
        # if self.__climate_chamber:
        #     self.__climate_chamber.stop_execution()
        #     self.__climate_chamber.deinitialize()

    def get_test_status(self):
        return self.status

    def get_meta_data(self):
        pass
