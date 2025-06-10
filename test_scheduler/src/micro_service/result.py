from abc import ABC, abstractmethod
from typing import Any, List


class Result(ABC):
    """
    A container for the data collected by executing the test. Provides an interface for accessing the data and should be
    used for all post processors and exporters. Always use concrete Result objects instead of raw data.
    """

    @abstractmethod
    def raw_data(self) -> Any:
        """
        Returns the raw data contained in this result object. Useful for directly accessing a copy of the data.

        :return: The raw data of this result. Can be anything.
        """
        pass
