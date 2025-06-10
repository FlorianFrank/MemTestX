import json
from os import walk, path
from typing import List


class JSONParser:
    def __init__(self):
        pass

    @staticmethod
    def grep_all_json_files_in_directory(directory: str) -> List[str]:
        return_list = []
        for (dir_path, dir_names, file_names) in walk(directory):
            for f in file_names:
                if '.json' in f:
                    return_list.append(f)
            break
        return return_list

    @staticmethod
    def read_json_file( file_path: str, file: str) -> dict:
        with open(path.join(file_path, file), 'r') as f:
            return json.load(f)