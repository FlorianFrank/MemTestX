from __future__ import annotations
import time
from abc import abstractmethod, ABC
from typing import TYPE_CHECKING, Union

from db_handler import logger
from utils.definitions import NETWORK_TIMEOUT_WRITE_FINISH, InterfaceEnum, Command

if TYPE_CHECKING:
    from micro_service.utils.test_state_machine import Test
    from test_scheduling.memory_test import MemoryTest
    from test_scheduling.test_defines import StandaloneTest


class InterfaceWrapper(ABC):
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

    def start_recv_thread(self, test: Union[Test, MemoryTest]):
        logger.error("Call start thread method in base class not permitted!")
        pass

    def stop_thread(self):
        logger.error("Call stop thread method in base class not permitted!")
        pass

    @staticmethod
    def wait_until_writer_finishes(test: Union[MemoryTest, StandaloneTest]):
        # TODO let writer thread finish its work!
        timeout_ctr = 0

        # Use hasattr or class name string check to avoid runtime circular import if possible
        if hasattr(test, 'measure_file') and test.measure_file is not None:
            while not test.measure_file.is_write_done() and timeout_ctr < NETWORK_TIMEOUT_WRITE_FINISH:
                timeout_ctr += 1
                logger.debug("Waiting for write to be finished")
                time.sleep(0.1)

        if hasattr(test, 'done'):
            test.done()
        else:
            test.set_finished()
            if hasattr(test, 'measure_file') and test.measure_file is not None:
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
