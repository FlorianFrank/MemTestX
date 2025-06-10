from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from file_handler import MeasureFileHandler


class TestType(Enum):
    RELIABLE = 0,
    WRITE_LATENCY = 1,
    READ_LATENCY = 2,
    ROW_HAMMERING = 3,
    VOLTAGE_READ = 4,
    VOLTAGE_WRITE = 5,
    UNKNOWN_PUF_TEST = 6


def test_type_to_str(test_type: TestType) -> str:
    if test_type == TestType.RELIABLE:
        return "reliable"
    elif test_type == TestType.WRITE_LATENCY:
        return "writeLatency"
    elif test_type == TestType.READ_LATENCY:
        return "readLatency"
    elif test_type == TestType.ROW_HAMMERING:
        return "rowHammering"
    elif test_type == TestType.VOLTAGE_READ:
        return "voltageRead"
    elif test_type == TestType.VOLTAGE_WRITE:
        return "voltageWrite"


class TestState(Enum):
    INACTIVE = 0x00
    WAITING_FOR_RESPONSE = 0x01
    PROCESSING = 0x02
    FINISHED = 0x03
    ERROR = 0x04


class TestInternalState(Enum):
    INACTIVE = 0x00,
    INIT = 0x01,
    RUN = 0x02,
    DONE = 0x03


@dataclass
class TestTemplate:
    type: TestType
    parameters: dict
    start_ts: float
    end_ts: float
    memory_type_name: str
    comment: str


@dataclass
class Test:
    identifier: int
    state: TestState
    internal_state: TestInternalState
    memory_label: str
    test_template: TestTemplate
    measure_file: Optional[MeasureFileHandler]

    def __init__(self, memory_label: str, board: str, test_template: TestTemplate):
        self.state = TestState.INACTIVE
        self.memory_label = memory_label
        self.test_template = test_template
        self.measure_file: Optional[MeasureFileHandler] = None
        self.identifier = 0
        self.board = board
        self.internal_state: TestInternalState = TestInternalState.INACTIVE

@dataclass
class TestRange:
    lists: List[Test]
    wait_between_tests_in_ms: int
