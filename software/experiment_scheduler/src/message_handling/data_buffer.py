from dataclasses import dataclass
from typing import List, Callable
from threading import Lock


@dataclass
class MeasureDataTuple:
    """
    Represents a measurement tuple returned by each PUF experiment.

    Contains the data address and a checksum to ensure the integrity of the received data.
    """
    data: int
    address: int
    checksum: int

    def as_row(self):
        return [self.data, self.address, self.checksum]


class DataBuffer:
    """
    Thread-safe buffer for storing and processing measurement data.
    """

    def __init__(self):
        self._data_list: List[MeasureDataTuple] = []
        self._lock = Lock()

    def add(self, data: MeasureDataTuple):
        """Adds a new MeasureDataTuple to the buffer."""
        with self._lock:
            self._data_list.append(data)

    def clear(self):
        """Clears the buffer."""
        with self._lock:
            self._data_list.clear()

    def flush(self, function_ptr: Callable[[List[MeasureDataTuple]], None]):
        """
        Passes the buffer contents to a callback function and clears the buffer.

        Args:
            function_ptr (Callable): A function that processes the buffer.
        """
        with self._lock:
            data_copy = self._data_list[:]
            self._data_list.clear()

        function_ptr(data_copy)
