import asyncio
import json
import logging_handler
import threading
import time


class StreamingService:

    def __init__(self, logger: logging.Logger, nats_interface, event_loop):  # MessagingServiceBase
        self._thread: threading.Thread = threading.Thread(target=self.streaming_thread_function)
        self._nats_interface = nats_interface
        self._logger = logger
        self._event_loop = event_loop
        self.value_buffer = list()
        self.thread_running = False

    def add_value(self, value):
        self.value_buffer.append(value)

    def streaming_thread_function(self):
        # config = TCPDeviceConfig(ip='132.231.14.105', port=5025)
        # smu = KEI2600(config)

        # smu.connect()

        while self.thread_running:
            self._logger.info('Publish data')

            #  measureA = smu.measure(Unit.VOLTAGE, SMUChannel.CHANNEL_A)
            # measureB = smu.measure(Unit.VOLTAGE, SMUChannel.CHANNEL_B)
            if len(self.value_buffer) > 0:
                value = self.value_buffer.pop(0)
                asyncio.run_coroutine_threadsafe(
                    self._nats_interface.publish_topic({'topic': get_topic_str(Topic.STREAM_DATA),
                                                        'data': json.dumps([[value[0]],
                                                                            [value[1]],
                                                                            [value[2]],
                                                                            [value[3]]])}),
                    self._event_loop
                ).result()

            self._logger.info("Heartbeat thread stopped.")

            time.sleep(1)

    def start_streaming_thread(self):  # Note: Changed to async
        self._logger.info('Start streaming thread')
        self._thread.start()  # Await thread start

    def join_thread(self):
        self._thread.join()


# Additional imports and definitions needed to run the code
class Unit:
    VOLTAGE = "voltage"


class SMUChannel:
    CHANNEL_A = "A"
    CHANNEL_B = "B"


class Topic:
    STREAM_DATA = "stream_data"


def get_topic_str(topic):
    return topic
