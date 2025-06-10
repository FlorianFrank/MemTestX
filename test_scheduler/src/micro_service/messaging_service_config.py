from enum import IntEnum


class Topic(IntEnum):
    GET_DEVICES = 0
    SCHEDULE_TEST = 1
    GET_TEST_STATUS = 2
    RETRIEVE_TEST_RESULTS = 3
    TEST_STATUS = 4
    STREAM_DATA = 5


def get_topic_str(topic_identifier: Topic) -> str:
    """
    Get the string representation of a Topic, which is the lower-case enum, e.g. GET_DEVICE will
    be turned into "get_device".

    :param topic_identifier: Topic enum value.
    :return: String representation of the Topic.
    """
    return topic_identifier.name.lower()