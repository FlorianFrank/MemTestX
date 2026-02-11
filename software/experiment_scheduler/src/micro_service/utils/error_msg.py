from enum import IntEnum


class ErrorCode(IntEnum):
    NO_ERROR = 1
    CUSTOM_ERROR = 2
    INVALID_ARGUMENT = 3


class ErrorMsg:

    def __init__(self, *args):
        """
        Initialize ErrorMsg instance.

        :param args: If one argument is provided, it sets the status. If two arguments are provided,
                     it sets both status and message.
        """
        self._status = ErrorCode.NO_ERROR
        self._message = ''

        if len(args) == 1:
            self._status = args[0]
        elif len(args) == 2:
            self._status, self._message = args[0], args[1]

    def is_error(self):
        """
        Check if the error status indicates an error.

        :return: True if there is an error, False otherwise.
        """
        return self._status != ErrorCode.NO_ERROR.value
