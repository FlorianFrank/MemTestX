import nats


from messaging_service.messaging_service_base import MessagingServiceBase
from messaging_service.messaging_service_callback_handler import MessagingServiceCallbackHandler
from messaging_service.messaging_service_config import Topic, get_topic_str
from model.device_list import DeviceList

from micro_service.utils.error_msg import ErrorMsg, ErrorCode


class NATSMessagingService(MessagingServiceBase):

    def __init__(self, device_list: DeviceList, event_loop, logger,
                 callback_handler: MessagingServiceCallbackHandler):
        super().__init__(device_list, event_loop, logger, callback_handler)
        self._nats_handle = None
        self._endpoint_name = ''
        self._endpoint = ''
        self._topic_list = {
            Topic.GET_DEVICES: callback_handler.get_devices_callback,
            Topic.SCHEDULE_TEST: callback_handler.schedule_test_callback,
            Topic.GET_TEST_STATUS: callback_handler.get_test_status_callback,
            Topic.RETRIEVE_TEST_RESULTS: callback_handler.retrieve_test_results_callback
        }
        self.inbox = None

    def __del__(self):
        """
        Destructor closes the NATS connection.
        """
        self._logger.info('Call destructor')
        self.de_initialize()

    async def setup_interface(self, params: dict):
        """
        Set up the interface for the NATS messaging service.

        :param params: Parameters for setting up the interface.
        :return: ErrorMsg instance indicating success or failure.
        """
        await super().setup_interface(params)
        self.inbox = self._nats_handle.new_inbox()
        self._logger.info('New Mailbox registered')
        return ErrorMsg()

    def initialize(self, params: dict) -> ErrorMsg:
        """
         Initialize the NATS messaging service with the given parameters.

         :param params: Parameters for initialization.
         :return: ErrorMsg instance indicating success or failure.
         """
        self._callback_handler.set_messaging_service(self)
        self._logger.info(f'Initialize NATS handler with parameters {params}')
        if 'endpoint' not in params or 'endpoint_name' not in params:
            return ErrorMsg(ErrorCode.INVALID_ARGUMENT, 'endpoint or endpoint_name not defined')
        self._endpoint = params['endpoint']
        self._endpoint_name = params['endpoint_name']
        return ErrorMsg(ErrorCode.NO_ERROR)

    def de_initialize(self) -> ErrorMsg:
        """
        De-initialize the NATS messaging service.

        :return: ErrorMsg instance indicating success or failure.
        """
        self._logger.info('Disconnect NATS connection')
        self._nats_handle.drain()
        return ErrorMsg()

    async def connect(self) -> ErrorMsg:
        """
        Connect to the NATS messaging broker.

        :return: ErrorMsg instance indicating success or failure.
        """
        self._logger.info('Establish connection to NATS broker {}'.format('nats://' + self._endpoint))
        self._nats_handle = await nats.connect('nats://' + self._endpoint, error_cb=self.error_cb,
                                               reconnected_cb=self.reconnect_cb,
                                               disconnected_cb=self.disconnected_cb, closed_cb=self.closed_cb)
        self._logger.info('Connected to NATS broker {}'.format('nats://' + self._endpoint))
        if not self._nats_handle:
            self._logger.error(
                'Connection to NATS broker {} could not be established'.format('nats://' + self._endpoint))
            return ErrorMsg(ErrorCode.CUSTOM_ERROR)
        return ErrorMsg(ErrorCode.NO_ERROR)

    async def subscribe_topics(self) -> ErrorMsg:
        """
        Subscribe to the specified topics.

        :return: ErrorMsg instance indicating success or failure.
        """
        for topic, callback in self._topic_list.items():
            self._logger.info(f'Subscribe to topic {topic.name}')
            await self._nats_handle.subscribe(get_topic_str(topic), cb=callback)

        return ErrorMsg(ErrorCode.NO_ERROR)

    async def publish_topic(self, data: dict) -> ErrorMsg:
        """
        Publish data to a topic.

        :param data: Data to be published. topic can be a string or Enum.
        :return: ErrorMsg instance indicating success or failure.
        """
        try:
            # Handle both string and Enum topic values
            topic_str = data['topic'].value if hasattr(data['topic'], 'value') else str(data['topic'])
            self._logger.info('Publish to topic {}:{}'.format(topic_str, data['data']))
            await self._nats_handle.publish(topic_str, data['data'].encode('utf-8'), reply=self.inbox)
            return ErrorMsg()
        except Exception as e:
            self._logger.error(f'Error publishing message to NATS: {e}')
            return ErrorMsg(ErrorCode.CUSTOM_ERROR)

    async def disconnected_cb(self):
        """
        Callback function for disconnection event.

        :return: None
        """
        self._logger.warning('Receive disconnected callback')

    async def error_cb(self, e):
        """
        Callback function for error event.

        :param e: Error object.
        :return: None
        """
        self._logger.error('Receive error callback ({})'.format(e))

    async def closed_cb(self):
        """
        Callback function for closed event.

        :return: None
        """
        self._logger.warning('Receive closed callback')
        pass

    async def reconnect_cb(self):
        """
        Callback function for reconnection event.

        :return: None
        """
        self._logger.warning('Receive reconnect callback')
        pass
