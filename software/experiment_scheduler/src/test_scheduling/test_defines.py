from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from message_handling.file_handler import MeasureFileHandler


class TestStatus(Enum):
    """
    The various possible statuses of the test execution.
    """
    IDLE = 0
    INIT = 1
    RUNNING = 2
    STOPPED = 3
    FAILED = 4


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


def string_to_test_type(test_str: str) -> TestType:
    if test_str == "reliable":
        return TestType.RELIABLE
    elif test_str == "writeLatency":
        return TestType.WRITE_LATENCY
    elif test_str == "readLatency":
        return TestType.READ_LATENCY
    elif test_str == "rowHammering":
        return TestType.ROW_HAMMERING
    elif test_str == "voltageRead":
        return TestType.VOLTAGE_READ
    elif test_str == "voltageWrite":
        return TestType.VOLTAGE_WRITE
    else:
        raise TypeError(f"Undefined test type {test_str}")


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

    def __str__(self):
        param_preview = ', '.join(f"{k}={v}" for k, v in self.parameters.items())
        return (
            f"TestTemplate("
            f"type={self.type.name}, "
            f"memory_type='{self.memory_type_name}', "
            f"params={{ {param_preview} }}, "
            f"start_ts={self.start_ts}, end_ts={self.end_ts}, "
            f"comment='{self.comment[:50]}{'...' if len(self.comment) > 50 else ''}')"
        )


@dataclass
class StandaloneTest:
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

    def set_error(self):
        self.state = TestState.ERROR

    def get_state(self) -> TestState:
        return self.state

    def set_processing(self):
        self.state = TestState.PROCESSING

    def set_finished(self):
        self.state = TestState.FINISHED

    def set_init(self):
        self.internal_state = TestInternalState.INIT

    def set_running(self):
        self.internal_state = TestInternalState.RUN

    def set_done(self):
        self.internal_state = TestInternalState.DONE


@dataclass
class TestRange:
    lists: List[StandaloneTest]
    wait_between_tests_in_ms: int
