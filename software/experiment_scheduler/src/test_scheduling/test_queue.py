import json
import logging
from typing import Optional

from test_colletion import TestCollection, TestCollectionStatus


class TestQueue:
    def __init__(self, logger):
        """
        Initialize TestQueue instance.

        Parameters:
        - logger: Logger object for logging messages.
        """
        self._running_test: Optional[TestCollection] = None
        self._test_queue_waiting: Optional[list[TestCollection]] = []
        self._test_queue_done: Optional[list[TestCollection]] = []
        self._logger: logging.Logger = logger

    def add_test_collection(self, collection: TestCollection):
        """
        Add tests to the waiting queue.

        Parameters:
        - test: TestCollection object representing the test.
        """
        self._test_queue_waiting.append(collection)

    def schedule_new_test(self) -> bool:
        """
        Schedule a new test if current test is stopped or no running test is set.

        Returns:
        - True if a new test is scheduled, False otherwise.
        """

        if not self._running_test and len(self._test_queue_waiting) == 0:
            return False

        if not self._running_test and len(self._test_queue_waiting) > 0:
            self._logger.info('Schedule first test collection')
            self._running_test = self._test_queue_waiting.pop()
        elif len(self._test_queue_waiting) > 0 and self._running_test:
            self._logger.info('Test collection ')
            self._test_queue_done.append(self._running_test)
            self._running_test = self._test_queue_waiting.pop()
        elif len(self._test_queue_waiting) == 0 and self._running_test:
            self._logger.info('No tests in waiting queue')
            if self._running_test.get_collection_status() == TestCollectionStatus.COLLECTION_FINISHED:
                self._test_queue_done.append(self._running_test)
                self._running_test = None
                return True

        if self._running_test.get_collection_status() == TestCollectionStatus.ITERATION_FINISHED:
            self._logger.info(f'Execute test of iteration {self._running_test.get_current_iteration()}')
            self._running_test.run_next()

        if self._running_test.get_collection_status() == TestCollectionStatus.TEST_IDLE:
            self._logger.info(f'Start new collection with ID {self._running_test.get_identifier()}')
            self._running_test.run_next()

            return True
        else:
            return False

    def get_test_state(self) -> tuple[int, TestCollectionStatus, int]:
        if not self._running_test and len(self._test_queue_waiting) == 0:
            return -1, TestCollectionStatus.NONE, 0
        if self._running_test:
            return self._running_test.get_identifier(), self._running_test.get_collection_status(), \
                self._running_test.get_current_iteration()
        return -1, TestCollectionStatus.TEST_IDLE, 0

    def get_waiting_test_ids(self) -> list[{int, str, int}]:
        """
        Get the list of waiting test identifiers with their status and iteration.

        Returns:
        - List of dictionaries containing test identifiers, status, and iteration.
        """
        return [
            {'id': test_collection_instance.get_identifier(),
             'status': test_collection_instance.get_status_of_current_test().name,
             'queue': 'waiting',
             'iteration': test_collection_instance.get_current_iteration(),
             'progress': test_collection_instance.get_current_progress(),
             'additional': json.dumps({
                 'current_row': f'{test_collection_instance.get_meta_data()[0]}',
                 'current_column': f'{test_collection_instance.get_meta_data()[1]}'
             })
             } for
            test_collection_instance in self._test_queue_waiting]

    def get_running_tests_ids(self) -> list[{int, str, int}]:
        ret = [{'id': self._running_test.get_identifier(),
                'queue': 'running',
                'status': self._running_test.get_status_of_current_test().name,
                'iteration': self._running_test.get_current_iteration(),
                'progress': self._running_test.get_current_progress(),
                'additional': json.dumps({
                    'current_row': f'{self._running_test.get_meta_data()[0]}',
                    'current_column': f'{self._running_test.get_meta_data()[1]}'
                })
                }] if self._running_test else []
        return ret

    def get_finished_test_ids(self) -> list[{int, str, int}]:
        """
        Get the list of finished test identifiers with their status and iteration.

        Returns:
        - List of dictionaries containing test identifiers, status, and iteration.
        """
        return [
            {'id': test_collection_instance.get_identifier(),
             'status': test_collection_instance.get_status_of_current_test().name,
             'queue': 'finished',
             'iteration': test_collection_instance.get_current_iteration(),
             'additional': json.dumps({
                 'current_row': '0',
                 'current_column': '0'
             }),
             'progress': test_collection_instance.get_current_progress()} for
            test_collection_instance in self._test_queue_done]
