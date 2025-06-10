import json
import os
from os import listdir
from os.path import isfile, join

from micro_service.device_definitions import DEVICE_TYPE_MAP
from micro_service.device_list import DeviceList

CONFIG_FILE = 'config_files/general.json'


def load_app_config() -> dict:
    """
    Loads the config parameters
    """
    with open(CONFIG_FILE, 'r') as file:
        return json.loads(file.read())


def list_configure_files_in_folder(folder: str):
    return [os.path.join(folder, f) for f in listdir(folder) if isfile(join(folder, f)) and ".json" in f]


def add_all_devices(device_list: DeviceList = None, folder: str = "./config/device_specifications"):
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
                                                 device_instance=None,
                                                 additional=additional_fields)
