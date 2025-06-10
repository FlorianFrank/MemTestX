from abc import ABC, abstractmethod
from device_list import DeviceList
from error_msg import ErrorMsg
from messaging_service_callback_handler import MessagingServiceCallbackHandler
from test_scheduler import TestScheduler


class MessagingServiceBase(ABC):
    """
    Base class for messaging service, establishing the connection between the different microservices and the
    backend. Allows the implementation of a custom messaging services, e.g. NATS or MQTT.
    """

    def __init__(self, device_list: DeviceList, event_loop, logger, callback_handler: MessagingServiceCallbackHandler):
        """
        Initialize MessagingServiceBase instance.

        Args:
            device_list (DeviceList): Device list instance.
            event_loop: Event loop.
            logger: Logger instance.
        """
        self._device_list = device_list
        self._event_loop = event_loop
        self._logger = logger
        self._callback_handler = callback_handler

    async def setup_interface(self, params: dict) -> ErrorMsg:
        """
        Setup interface.

        Args:
            params (dict): Parameters for setup.

        Returns:
            ErrorMsg: Error message if setup fails.
        """
        ret = self.initialize(params)
        if ret.is_error():
            return ret

        ret = await self.connect()
        if ret.is_error():
            return ret

        ret = await self.subscribe_topics()
        if ret.is_error():
            return ret

    @abstractmethod
    def initialize(self, params: dict) -> ErrorMsg:
        """
        Initialize messaging service.

        Args:
            params (dict): Initialization parameters.

        Returns:
            ErrorMsg: Error message if initialization fails.
        """
        pass

    @abstractmethod
    def de_initialize(self) -> ErrorMsg:
        """
        De-initialize messaging service.

        Returns:
            ErrorMsg: Error message if de-initialization fails.
        """
        pass

    @abstractmethod
    async def connect(self) -> ErrorMsg:
        """
        Connect to messaging service.

        Returns:
            ErrorMsg: Error message if connection fails.
        """
        pass

    @abstractmethod
    async def subscribe_topics(self) -> ErrorMsg:
        """
        Subscribe to topics.

        Returns:
            ErrorMsg: Error message if subscription fails.
        """
        pass

    @abstractmethod
    async def publish_topic(self, data: dict) -> ErrorMsg:
        """
        Publish topic data.

        Args:
            data (dict): Data to be published.

        Returns:
            ErrorMsg: Error message if publishing fails.
        """
        pass
