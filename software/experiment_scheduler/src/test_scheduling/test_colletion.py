import logging
from enum import Enum

from result import Result
from test_scheduling.test import Test, TestStatus


class TestCollectionStatus(Enum):
    TEST_RUNNING = 1
    ITERATION_FINISHED = 2
    COLLECTION_FINISHED = 3
    TEST_IDLE = 4
    TEST_INIT = 5
    TEST_FAILED = 6
    NONE = 7


class TestCollection:

    def __init__(self, identifier: int, test_instance: Test, logger: logging.Logger, iterations: int = 1):
        """
         Initialize TestCollection instance.

         Args:
             identifier (int): Identifier for the test collection.
             test_instance (Test): Instance of the test to be executed.
             logger (logging.Logger): Logger instance for logging messages.
             iterations (int, optional): Number of iterations to run the test. Defaults to 1.
         """
        self._identifier: int = identifier
        self._nr_iterations: int = iterations
        self._current_iteration: int = 0
        self._logger: logging.Logger = logger
        self._test_template: Test = test_instance

    def get_iteration(self) -> int:
        """Returns the current iteration number."""
        return self._current_iteration

    def fetch_result(self) -> Result:
        pass

    def run_next(self):
        """Runs the next iteration of the test."""
        if self._current_iteration < self._nr_iterations:
            self._logger.info(f'Initialize and run test iteration {self._current_iteration}')
            self._test_template.execute(None)
            self._current_iteration += 1
        else:
            self._logger.warning('Maximum number of iterations reached')

    def get_status_of_current_test(self) -> TestStatus:
        return self._test_template.get_test_status()

    def get_collection_status(self) -> TestCollectionStatus:
        """Returns the status of the test collection."""
        if self._test_template.get_test_status().value == TestStatus.STOPPED.value:
            if self._current_iteration == self._nr_iterations:
                return TestCollectionStatus.COLLECTION_FINISHED
            if self._current_iteration < self._nr_iterations:
                return TestCollectionStatus.ITERATION_FINISHED
        elif self._test_template.get_test_status().value == TestStatus.RUNNING.value:
            return TestCollectionStatus.TEST_RUNNING
        elif self._test_template.get_test_status().value == TestStatus.IDLE.value:
            return TestCollectionStatus.TEST_IDLE
        elif self._test_template.get_test_status().value == TestStatus.INIT.value:
            return TestCollectionStatus.TEST_INIT
        elif self._test_template.get_test_status().value == TestStatus.FAILED.value:
            return TestCollectionStatus.TEST_FAILED

    def get_nr_iterations(self) -> int:
        return self._nr_iterations

    def get_current_iteration(self) -> int:
        return self._current_iteration

    def get_current_progress(self) -> int:
        # Currently not implemented
        return 100
        #return self._test_template.get_progress()

    def get_meta_data(self):
        return self._test_template.get_meta_data()

    def get_identifier(self) -> int:
        return self._identifier
