import threading
import time
from abc import abstractmethod

from db_handler import logger
from definitions import NETWORK_TIMEOUT_WRITE_FINISH, InterfaceEnum, Command
from test_defines import Test, TestState


class InterfaceWrapper:
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
        self._stop_thread = False
        self._recv_thread = threading.Thread(target=self.recv_thread_func, args=(test,))
        self._recv_thread.start()
        logger.info("Receive thread started.")

    def stop_thread(self):
        logger.info("Stopping receive thread.")
        self._stop_thread = True
        if self._recv_thread and self._recv_thread.is_alive():
            self._recv_thread.join()
            logger.info("Receive thread stopped successfully.")
        else:
            logger.warning("Receive thread was not running.")

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
