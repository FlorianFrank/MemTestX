import threading
import time

from test_colletion import TestCollectionStatus
from test_queue import TestQueue


class Scheduler:
    def __init__(self, test_queue: TestQueue, logger, scheduler_time_interval: int):
        """
        Initializes TestScheduler with the provided TestQueue.

        :param test_queue: Instance of TestQueue.
        :param logger: Logger instance for logging messages.
        :param scheduler_time_interval: Time interval (in seconds) for the scheduler.
        """
        self._test_queue = test_queue
        self._scheduler_thread = None
        self._running = False
        self._logger = logger
        self._scheduler_time_interval = scheduler_time_interval

    def get_test_queue(self) -> TestQueue:
        """
        Get the associated TestQueue.

        :return: TestQueue instance.
        """
        return self._test_queue

    def _scheduler_thread_function(self):
        """
        Function to be executed by the scheduler thread.
        """
        while self._running:
            identifier, state, iteration = self._test_queue.get_test_state()
            self._logger.info(
                f"Retrieving state of the running test (ID: {identifier}, State: {state}, Iteration: {iteration})")
            if state == TestCollectionStatus.ITERATION_FINISHED or state == TestCollectionStatus.TEST_IDLE \
                    or state == TestCollectionStatus.COLLECTION_FINISHED:
                self._logger.info('Schedule new test')
                self._test_queue.schedule_new_test()
            time.sleep(self._scheduler_time_interval)

    def run_test_scheduler(self):
        """
        Start the scheduler thread.
        return
        """
        if not self._running:
            self._running = True
            self._logger.info('Starting Scheduler thread')
            self._scheduler_thread = threading.Thread(target=self._scheduler_thread_function)
            self._scheduler_thread.start()
        else:
            self._logger.warning("Scheduler is already running")

    def stop_scheduler(self):
        """
        Stop the scheduler thread.
        """
        if self._running:
            self._running = False
            self._scheduler_thread.join()
            self._logger.info('Scheduler thread stopped')
        else:
            self._logger.warning("Scheduler is not running")
