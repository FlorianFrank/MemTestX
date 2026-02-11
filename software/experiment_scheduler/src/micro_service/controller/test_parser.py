import logging
from typing import Optional, List, Tuple, Type

from micro_service.utils.test_state_machine import Test
from test_scheduling.memory_test import MemoryTest


class TestParser:
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._test_types: List[Tuple[str, Optional[Type[MemoryTest]]]] = []

    def register_test_type(self, test_idn: str, test_class: Type[Test] | Type[MemoryTest]) -> None:
        """
        Register a test type with its identifier and class.

        Args:
            test_idn (str): The identifier of the test type.
            test_class (Type[Test]): The class of the test type to be registered.
        """
        self._logger.info(f"Registering test type: {test_idn} -> {test_class.__name__}")
        self._test_types.append((test_idn, test_class))

    def get_test_type(self, test_idn: str) -> Type[MemoryTest]:
        """
        Get the class of the test type with the given identifier.

        Args:
            test_idn (str): The identifier of the test type.

        Returns:
            Optional[Type[Test]]: The class of the test type if found, otherwise None.
        """

        for test_id, test_class in self._test_types:
            if test_id == test_idn:
                self._logger.info(f"Test {test_idn} identified")
                return test_class
        self._logger.error(f"Test type with identifier {test_idn} not found")
        raise Exception(f"Test type with identifier {test_idn} not found")
