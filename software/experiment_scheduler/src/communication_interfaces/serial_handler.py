import json
import threading
import time
from abc import abstractmethod

import serial
import serial.tools.list_ports

from db_handler import logger
from definitions import InterfaceEnum, Command
from interface_wrapper import InterfaceWrapper
from test_defines import Test, TestState, TestInternalState

MAX_RECV_BUF_LEN = 4096
TIMEOUT_RESPONSE = 2.0
TIMEOUT_WRITE_FINISH = 10
DEFAULT_BAUDRATE = 921600


class SerialHandler(InterfaceWrapper):
    """
    Handles serial communication with a device, including sending and receiving data,
    as well as managing a background thread for receiving data asynchronously.
    """

    def __init__(self, serial_if: str, baudrate: int):
        """
        Initializes the SerialHandler.

        Args:
            serial_if (str): Serial interface (e.g., '/dev/ttyUSB0').
            baudrate (int): Baud rate for serial communication.
        """
        super().__init__()
        self._incomplete_msg = ""
        self._serial_if = serial_if
        self._baudrate = baudrate
        self._serial_if = serial.Serial(serial_if, baudrate, timeout=TIMEOUT_RESPONSE)

    def write(self, data: bytes):
        """
        Writes data to the serial interface.

        Args:
            data (bytes): Data to be sent.
        """
        self._serial_if.write(data)

    def read(self, size):
        """
        Reads a specified number of bytes from the serial interface.

        Args:
            size (int): Number of bytes to read.

        Returns:
            bytes: Data read from the serial interface.
        """
        return self._serial_if.read(size)

    def read_list(self, size):
        """
        Reads a line from the serial interface.

        Args:
            size (int): Maximum number of bytes to read.

        Returns:
            bytes: Line read from the serial interface.
        """
        return self._serial_if.readline(size)

    def start_recv_thread(self, test: Test):
        """
        Starts a background thread to receive data from the serial interface.

        Args:
            test (Test): Test object to handle received data.
        """
        self._stop_thread = False
        self._recv_thread = threading.Thread(target=self.recv_thread_func, args=(test,))
        self._recv_thread.start()
        logger.info("Receive thread started.")

    def stop_thread(self):
        """
        Stops the reception thread if it is running.
        """
        logger.info("Stopping receive thread.")
        self._stop_thread = True
        if self._recv_thread and self._recv_thread.is_alive():
            self._recv_thread.join()
            logger.info("Receive thread stopped successfully.")
        else:
            logger.warning("Receive thread was not running.")

    def recv_thread_func(self, test: Test):
        """
        Function executed by the reception thread to continuously read data from the serial interface.

        Args:
            test (Test): Test object to handle received data.
        """
        logger.info(f"Starting Receive Thread on serial port to: {self._serial_if} with baudrate {self._baudrate}")
        try:
            while not self._stop_thread:
                logger.info("Wait for incoming data...")
                try:
                    response = self._serial_if.read(MAX_RECV_BUF_LEN)
                    if len(response) > 0:
                        self.parse_msg(response, test)
                except TimeoutError:
                    if test.state == TestState.WAITING_FOR_RESPONSE:
                        logger.error(f"Timed out waiting {TIMEOUT_RESPONSE} seconds for response")
                        test.state = TestState.ERROR
                    if self._stop_thread:
                        logger.info(f"Stopping recv_thread function")
        except Exception as e:
            logger.error("Error in Receive Thread: %s", e)

    def parse_msg(self, response: bytes, test: Test):
        """
        Parses incoming messages and handles different response types.

        Args:
            response (bytes): Raw response from the serial interface.
            test (Test): Test object to handle parsed messages.
        """
        try:
            response_parsed = response.decode('utf-8').replace('\x00', '')
            response_list = (self._incomplete_msg + response_parsed).split('\n')
            self._incomplete_msg = response_list.pop() if response_parsed[-1] != '\n' else ''

            for single_response in response_list:
                if len(single_response) > 0:
                    if single_response[0] == 'R':
                        logger.info(f"Received response {single_response}")
                        single_response = single_response.strip().split(':')
                        if single_response[1] == 'idn':
                            logger.info(f"Device identified as {response_parsed[2]}")
                        if single_response[1] == 'processing':
                            logger.info(f"Response -> board is processing is received")
                            test.state = TestState.PROCESSING
                        if single_response[1] == 'ready':
                            self._incomplete_msg = ''
                            logger.info(f"Response -> processing finished is received")
                            InterfaceWrapper.wait_until_writer_finishes(test)

                        # Only required for voltage variations
                        if single_response[1] == 'init':
                            logger.info(f"Response -> init phase completed")
                            test.internal_state = TestInternalState.INIT

                        if single_response[1] == 'run':
                            logger.info(f"Response -> run phase completed")
                            test.internal_state = TestInternalState.RUN

                        if single_response[1] == 'done':
                            logger.info(f"Response -> done phase completed")
                            test.internal_state = TestInternalState.DONE

                    if single_response[0] == 'm':
                        # e.g. 'm:55,aa,10'
                        split = single_response.split(':')
                        test.measure_file.add_to_buffer([[int(x, 16) for x in split[1].split(',')]])
                    if response_parsed[0] == 'E':
                        response_parsed = response_parsed.replace('\n', '').replace('\r', '').split(': ')
                        logger.error(f"Error returned {response_parsed[1]}")
                        test.state = TestState.ERROR
        except Exception as e:
            logger.error(f"Failed to decode response ({response.decode()}): {e}")

    def is_recv_thread_running(self):
        """
        Checks if the reception thread is running.

        Returns:
            bool: True if the reception thread is running, False otherwise.
        """
        return not self._stop_thread

    # @override
    def get_if_type(self) -> InterfaceEnum:
        return InterfaceEnum.SERIAL_IF

    @abstractmethod
    def send_config(self, cmd: Command, config, cfg: dict = None):
        cmd = (json.dumps(cfg).replace(', ', ",\n").
               replace('}', '\n}').
               replace('{', '{\n'))
        chunks = cmd.split('\n')
        for chunk in chunks:
            self.write(bytearray(chunk + "\n", 'ascii'))
            print(f"Sent chunk: {chunk}")
        time.sleep(0.05)  # Short delay between chunks to avoid overwhelming the receiver

    @abstractmethod
    def send_continue(self, config):
        logger.info(f"Send continue msg")
        self.write(bytearray('continue\n', 'ascii'))
        time.sleep(0.05)  # Short delay between chunks to avoid overwhelming the receiver

    @staticmethod
    def find_usbmodem_ports():
        """Find all UART devices matching '/dev/tty.usbmodem*' on macOS."""
        ports = serial.tools.list_ports.comports()
        usbmodem_ports = [port.device for port in ports if 'usbmodem' in port.device]

        return usbmodem_ports
