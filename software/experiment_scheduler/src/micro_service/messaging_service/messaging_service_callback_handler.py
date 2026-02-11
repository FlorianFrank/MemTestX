import json
import logging

from messaging_service.messaging_service_config import get_topic_str, Topic
from messaging_service.streaming_service import StreamingService
from controller.test_parser import TestParser
from model.test_colletion import TestCollection
from test_scheduling.test_scheduler import TestScheduler
from tests.row_hammering_test import RowHammeringTest


class MessagingServiceCallbackHandler:
    """
    This class implements all callbacks to react on the topics.
    GET_DEVICES, SCHEDULE_TEST, GET_TEST_STATUS, RETRIEVE_TEST_RESULTS
    """

    def __init__(self, logger: logging.Logger, endpoint: str, endpoint_name: str, test_scheduler: TestScheduler,
                 test_parser: TestParser, event_loop):
        self._logger = logger
        self._endpoint = endpoint
        self._endpoint_name = endpoint_name
        self._test_scheduler = test_scheduler
        self._messaging_service = None
        self._test_parser = test_parser
        self._event_loop = event_loop
        self.streaming_service = None
        self._init = 0

    def set_messaging_service(self, messaging_service):
        """Attach the messaging service instance used for publishing responses."""
        self._messaging_service = messaging_service

    def register_streaming_service(self, streaming_service: StreamingService):
        """Register the streaming service used for test result streaming."""
        self.streaming_service = streaming_service

    async def init_test_scheduler(self):
        """Start the asynchronous test scheduler loop."""
        self._test_scheduler.run_scheduler_loop()

    async def get_devices_callback(self, msg):
        """Handle incoming device discovery requests."""
        self._logger.info(f"Receive message {msg} on get_devices_callback")

    async def schedule_test_callback(self, msg):
        """Handle requests to schedule a new test on this endpoint."""
        self._logger.info(f"Receive message {msg} on schedule_test_callback")
        parsed_json_list = json.loads(msg.data)

        if (parsed_json_list['deviceData']['name'] == self._endpoint_name and
                parsed_json_list['deviceData']['port'] == self._endpoint):
            test_type = parsed_json_list['testData']['testType']

            test_instance = self._test_parser.get_test_type(test_type)
            if test_instance is None:
                self._logger.error(f"Error test type {test_type} not found")
                await msg.respond(b'ERROR')
            else:
                test_instance = test_instance(communication_interface=self._test_scheduler.get_communication_interface(),
                                              server_ip=self._test_scheduler.get_server_ip(),
                                                 config=json.loads(msg.data.decode()), multithread=False)


                self._logger.info(f"Add new Test of type {test_type} Test to waiting queue")
                iterations = parsed_json_list['testData']['iterations']

                # Parse config from JSON
                test_collection = TestCollection(identifier=parsed_json_list['instanceID'], logger=self._logger,
                                                 iterations=iterations,
                                                 test_instance=test_instance)
                self._test_scheduler.get_test_queue().add_test_collection(test_collection)
                await msg.respond(b'OK')

    async def get_test_status_callback(self, msg):
        """Handle requests for the status of running, waiting, and finished tests."""
        self._logger.info(f"Receive message {msg} on get_test_status_callback")
        parsed_msg = json.loads(msg.data.decode())['payload']

        def filter_instance_ids(test_list: list[dict], instance_ids: list[int]) -> list[dict]:
            """Filter test entries by requested instance IDs."""
            ret_list = []
            for elem in test_list:
                if elem['id'] in instance_ids:
                    ret_list.append(elem)
            return ret_list
        running_tests = filter_instance_ids(self._test_scheduler.get_test_queue().get_running_tests_ids(),
                                            parsed_msg['instance_ids'])
        waiting_tests = filter_instance_ids(self._test_scheduler.get_test_queue().get_waiting_test_ids(),
                                            parsed_msg['instance_ids'])

        finished_tests = filter_instance_ids(self._test_scheduler.get_test_queue().get_finished_test_ids(),
                                             parsed_msg['instance_ids'])

        ret_dict = {'waiting': waiting_tests, 'running': running_tests, 'finished': finished_tests}
        publish_json = {
            'topic': get_topic_str(Topic.TEST_STATUS), 'data': json.dumps(ret_dict)}
        self._logger.info(f'Publish {publish_json}')
        await self._messaging_service.publish_topic(publish_json)

        await msg.respond(b'OK')

    async def retrieve_test_results_callback(self, msg):
        """Handle requests to retrieve completed test results."""
        self._logger.info(f"Receive message {msg} on retrieve_test_results_cb")
