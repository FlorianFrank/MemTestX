import csv
import threading
import time
from asyncio.log import logger
from os import path
from typing import List

import numpy as np

from data_buffer import MeasureDataTuple
from definitions import MEASURE_FILE_DELIMITER, MEASURE_FILE_QUOTE_CHAR


class MeasureFileHandler:
    def __init__(self, path: str, file_name: str):
        self._lock = threading.Lock()
        self._store_data_thread = None
        self._transmit_data_thread_running = False
        self._file_name = file_name
        self._path = path
        self._file_handle = None
        self._csv_writer = None
        self._csv_reader = None
        self._is_open = False
        self._data = []
        self._data_write_ctr = 0
        self._data_read_ctr = 0
        self._current_buf_pos = 0
        logger.info(f"MeasureFileHandler initialized with path: {path}, file_name: {file_name}")

    def get_file_name(self) -> str:
        return self._file_name
    def initialize(self) -> bool:
        with self._lock:
            if self._is_open:
                logger.warning('File is already open')
                return False
            try:
                self._file_handle = open(path.join(self._path, self._file_name), 'w+')
                self._csv_writer = csv.writer(self._file_handle, delimiter=MEASURE_FILE_DELIMITER, quotechar=MEASURE_FILE_QUOTE_CHAR,
                                              quoting=csv.QUOTE_MINIMAL)
                self._csv_reader = csv.reader(self._file_handle, delimiter=MEASURE_FILE_DELIMITER, quotechar=MEASURE_FILE_QUOTE_CHAR)
                self._is_open = True
                logger.info(f"File {self._file_name} successfully opened at {self._path}")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize file {self._file_name}: {e}")
                return False

    def is_write_done(self):
        return self._data_read_ctr >= self._data_write_ctr

    def write_data(self, data: List[MeasureDataTuple]):
        #with self._lock:
            if self._is_open:
                try:
                    for data_tuple in data:
                        self._csv_writer.writerow(data_tuple.as_row())
                    #logger.info(f"{len(data)} rows written to file {self._file_name}")
                except Exception as e:
                    logger.error(f"Error while writing data to {self._file_name}: {e}")
            else:
                logger.warning("File is closed. Cannot write data.")

    def read_file(self) -> np.ndarray:
        with self._lock:
            if not self._is_open:
                logger.warning("File is not open. Cannot read data.")
                return np.array([], dtype=[('address', 'int32'), ('data', 'int32')])

            logger.info(f"Reading file {self._file_name}")
            valid_rows = []
            try:
                for row in self._csv_reader:
                    if not (row[0] == 'address' or row[1] == 'data'):
                        try:
                            address = int(row[0])
                            data = int(row[1])
                            valid_rows.append((address, data))
                        except ValueError:
                            logger.error(f"Invalid row in file {self._file_name}: {row}")
                structured_array = np.array(valid_rows, dtype=[('address', 'int32'), ('data', 'int32')])
                logger.info(f"File {self._file_name} read successfully with {len(valid_rows)} valid rows")
                return structured_array
            except Exception as e:
                logger.error(f"Error while reading file {self._file_name}: {e}")
                return np.array([], dtype=[('address', 'int32'), ('data', 'int32')])

    def store_data_thread_func(self):
        logger.info("Store data thread started.")
        while self._transmit_data_thread_running:
            with self._lock:
                if self._data_write_ctr > self._data_read_ctr:
                    try:
                        for measure_ctr in range(self._data_read_ctr, self._data_write_ctr):
                            self.write_data([self._data[measure_ctr]])
                            self._data_read_ctr += 1
                        logger.info(f"Buffered data successfully written to file. read ctr: {self._data_read_ctr}, "
                                    f"write ctr: {self._data_write_ctr}")
                    except Exception as e:
                        logger.error(f"Error in store_data_thread_func: {e}")
            time.sleep(0.001)
        logger.info("Store data thread stopped.")

    def start_store_data_thread(self):
        if not self._transmit_data_thread_running:
            self._transmit_data_thread_running = True
            self._store_data_thread = threading.Thread(target=self.store_data_thread_func)
            logger.info("Data store thread initialized and running.")
            self._store_data_thread.start()

    def stop_store_data_thread(self):
        logger.info("Waiting for store data thread to be stopped.")
        if self._transmit_data_thread_running:
            self._transmit_data_thread_running = False
            self._store_data_thread.join()
            logger.info("Store data thread stopped")
        else:
            logger.warning("Store data thread is not running!")

    def add_to_buffer(self, data: List):
        #with self._lock:
            try:
                for d in data:
                    self._data.append(MeasureDataTuple(d[0], d[1], d[2]))
                self._data_write_ctr += len(data)
              #  logger.info(f"Added {len(data)} items to buffer. Write counter: {self._data_write_ctr}")
            except Exception as e:
                logger.error(f"Error while adding to buffer: {e}")

    def close_file(self):
        with self._lock:
            if self._is_open:
                try:
                    self._file_handle.close()
                    self._is_open = False
                    self._data.clear()
                    logger.info(f"File {self._file_name} successfully closed.")
                except Exception as e:
                    logger.error(f"Error while closing file {self._file_name}: {e}")
            else:
                logger.warning(f"File {self._file_name} is already closed.")
