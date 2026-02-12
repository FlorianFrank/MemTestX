"""
Defines all topics to which data can be published or subscribed within the messaging service.
"""

from enum import Enum


class Topic(Enum):
    GET_DEVICES = "get_devices"
    SCHEDULE_TEST = "schedule_test"
    GET_TEST_STATUS = "get_test_status"
    RETRIEVE_TEST_RESULTS = "retrieve_test_results"
    TEST_STATUS = "test_status"
    STREAM_DATA = "stream_data"


def get_topic_str(topic_identifier: Topic) -> str:
    """
    Get the string representation of a Topic, which is the lower-case enum, e.g. GET_DEVICE will
    be turned into "get_device".

    :param topic_identifier: Topic enum value.
    :return: String representation of the Topic.
    """
    return topic_identifier.name.lower()