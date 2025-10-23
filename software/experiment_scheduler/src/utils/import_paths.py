import sys


def set_import_paths():
    """
    Adds these paths to the python path in order to allow the execution of ./run.sh and ./setup.sh
    """
    sys.path.append("src")
    sys.path.append("src/communication_interfaces")
    sys.path.append("src/evaluation")
    sys.path.append("src/message_handling")
    sys.path.append("src/micro_service")
    sys.path.append("src/test_scheduling")
    sys.path.append("src/utils")
    sys.path.append("src/py_instrument_control_lib")
    sys.path.append("src/py_instrument_control_lib/device_base")
    sys.path.append("src/py_instrument_control_lib/channels")
    sys.path.append("src/py_instrument_control_lib/device_generation")
    sys.path.append("src/py_instrument_control_lib/device_types")
    sys.path.append("src/py_instrument_control_lib/devices")
    sys.path.append("src/py_instrument_control_lib/manufacturers")
    sys.path.append("src/py_instrument_control_lib/playground")
    sys.path.append("src/py_instrument_control_lib/specifications")