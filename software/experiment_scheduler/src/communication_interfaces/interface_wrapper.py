import time
from abc import abstractmethod

from db_handler import logger
from definitions import NETWORK_TIMEOUT_WRITE_FINISH, InterfaceEnum, Command
from test_defines import Test, TestState


class InterfaceWrapper:
    """
    Base class that defines a unified interface for communication handlers,
    such as UART, Ethernet, or other transport layers.
    """

    def __init__(self):
        self._recv_thread = None
        self._stop_thread = True

    @abstractmethod
    def parse_msg(self, response: bytes, test: Test):
        pass

    @abstractmethod
    def recv_thread_func(self, test: Test):
        pass

    def start_recv_thread(self, test: Test):
        logger.error("Call start thread method in base class not permitted!")
        pass

    def stop_thread(self):
        logger.error("Call stop thread method in base class not permitted!")
        pass

    @staticmethod
    def wait_until_writer_finishes(test: Test):
        test.state = TestState.FINISHED
        # TODO let writer thread finish its work!
        timeout_ctr = 0
        while not test.measure_file.is_write_done() or timeout_ctr < NETWORK_TIMEOUT_WRITE_FINISH:
            timeout_ctr += 1
            logger.debug("Waiting for write to be finished")
            time.sleep(0.1)
        test.measure_file.stop_store_data_thread()
        test.measure_file.close_file()

    def is_recv_thread_running(self):
        return not self._stop_thread

    @abstractmethod
    def get_if_type(self) -> InterfaceEnum:
        pass

    @abstractmethod
    def send_config(self, cmd: Command, config, cfg: dict = None):
        pass

    def send_continue(self, config):
        pass
