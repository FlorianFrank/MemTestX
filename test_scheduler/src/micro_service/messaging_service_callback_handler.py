import json
import logging_handler

from messaging_service_config import get_topic_str, Topic
from micro_service.streaming_service import StreamingService
from micro_service.test_parser import TestParser
from test_colletion import TestCollection
from test_scheduler import TestScheduler


#from generic_config import GenericConfig
#from messaging_service_config import get_topic_str, Topic
#from model.tests.test_collection import TestCollection
#from streaming_service import StreamingService
#from test_parser import TestParser
#from test_scheduler import TestScheduler


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
        self._messaging_service = messaging_service

    def register_streaming_service(self, streaming_service: StreamingService):
        self.streaming_service = streaming_service

    async def init_test_scheduler(self):
        #self._test_scheduler.run_test_scheduler()
        print("TODO run scheduler!")

    async def get_devices_callback(self, msg):
        self._logger.info(f"Receive message {msg} on get_devices_callback")

    async def schedule_test_callback(self, msg):
        self._logger.info(f"Receive message {msg} on schedule_test_callback")
        parsed_json_list = json.loads(msg.data)

        if (parsed_json_list['deviceData']['name'] == self._endpoint_name and
                parsed_json_list['deviceData']['port'] == self._endpoint):
            test_type = parsed_json_list['testData']['testType']

            test_instance = self._test_parser.get_test_type(test_type)
            if test_instance is None:
                self._logger.error(f"Error test type {test_type} not found")
                await msg.respond(b'ERROR')
                return None

            #generic_config = GenericConfig(config=parsed_json_list)
            test_instance = test_instance(config=None, streaming_service=s)

            self._logger.info(f"Add new Test of type {test_type} Test to waiting queue")
            iterations = parsed_json_list['testData']['iterations']

            # Parse config from json
            test_collection = TestCollection(identifier=parsed_json_list['instanceID'], logger=self._logger,
                                             iterations=iterations,
                                             test_instance=test_instance)
            self._test_scheduler.get_test_queue().add_test_collection(test_collection)

        await msg.respond(b'OK')

    async def get_test_status_callback(self, msg):
        self._logger.info(f"Receive message {msg} on get_test_status_callback")
        parsed_msg = json.loads(msg.data.decode())['payload']

        def filter_instance_ids(test_list: list[dict], instance_ids: list[int]) -> list[dict]:
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

        self._init = (self._init + 2) % 100
        # TODO test
        runner = [{'id': 160,
                   'status': 'RUNNING',
                   'queue': 'running',
                   'iteration': self._init % 10,
                   'progress': self._init,
                   'additional': json.dumps({
                       'current_row': f'{1}',
                       'current_column': f'{5}'
                   })
                   }]

        ret_dict = {'waiting': waiting_tests, 'running': runner, 'finished': finished_tests}
        publish_json = {
            'topic': get_topic_str(Topic.TEST_STATUS), 'data': json.dumps(ret_dict)}
        self._logger.info(f'Publish {publish_json}')
        await self._messaging_service.publish_topic(publish_json)

        await msg.respond(b'OK')

    async def retrieve_test_results_callback(self, msg):
        self._logger.info(f"Receive message {msg} on retrieve_test_results_cb")
