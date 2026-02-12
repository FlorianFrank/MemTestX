import json
import os
from os.path import isfile, join

from micro_service.utils.device_definitions import DEVICE_TYPE_MAP
from model.device_list import DeviceList

CURRENT_FOLDER = dir_path = os.path.dirname(os.path.realpath(__file__))


CONFIG_FILE = f'{CURRENT_FOLDER}/../../../config_files/micro_service_config.json'


def load_microservice_config() -> dict:
    """
    Loads the configuration of the microservice, divided in general, nats and fpga config.
    """
    with open(CONFIG_FILE, 'r') as file:
        return json.loads(file.read())


def list_configure_files_in_folder(folder: str):
    """
    Return a list of absolute paths to all JSON configuration files in a folder.
    Not used in the memory controller implementation, as configuration of the
    connected device directly provided within the microservice config.
    """
    return [os.path.join(folder, f) for f in os.listdir(folder) if isfile(join(folder, f)) and ".json" in f]


def add_all_devices(device_list: DeviceList = None, folder: str = "./config/device_specifications"):
    """
    Load device specification files from a folder and register all device templates
    in the provided DeviceList.
    Not used in the memory controller implementation as currently only a single device can be connected.
    """
    list_of_config_files = list_configure_files_in_folder(folder)
    for file in list_of_config_files:
       with open(file, 'r') as f:
            dev_config = json.loads(f.read())
            additional_fields = list()
            for key, value in dev_config.items():
                if key != 'identifier' and key != 'name' and key != 'device_type':
                    additional_fields.append({'key': key, 'value': value})
            device_list.register_device_template(identifier=dev_config['identifier'], name=dev_config['name'],
                                                 device_type=DEVICE_TYPE_MAP[dev_config['device_type']],
                                                 additional=additional_fields)