import json
from typing import Dict

import yaml


def load_file(file_path: str, mode: str = "rt", encoding: str = "utf-8") -> str:
    """
    Load the content from a file as a string or a list of lines

    :param file_path: the path to the file to be loaded (e.g. txt, markdown), ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the content of the file, ``str``
    """
    with open(file=file_path, mode=mode, encoding=encoding) as file:
        return file.read()


def load_yaml(file_path: str, mode: str = "rt", encoding: str = "utf-8") -> Dict:
    """
    Load data from a YAML file

    :param file_path: the path to the YAML file to be loaded, ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the data loaded from the YAML file, ``Dict``
    """
    with open(file=file_path, mode=mode, encoding=encoding) as yaml_file:
        return yaml.safe_load(stream=yaml_file)


def loads_json(data: str) -> Dict:
    """
    Load the given data as JSON

    :param data: the JSON data to be loaded, ``str``
    :return: the JSON data loaded, ``Dict``
    """
    if data is None or data == "":
        return None
    return json.loads(data)


def save_file(data, file_path: str, mode: str = "wt", encoding: str = "utf-8") -> None:
    """
    Save the given data to a file

    :param data: the data to be saved to the file, ``str``
    :param file_path: the path to the file to be saved, ``str``
    :param mode: the mode in which the file is opened (e.g. wt, wb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    """
    with open(file=file_path, mode=mode, encoding=encoding) as file:
        file.write(data)


def save_json_file(
    data, file_path: str, mode: str = "wt", encoding: str = "utf-8"
) -> None:
    """
    Save the data to a JSON file

    :param data: the data to be saved (must be serializable to JSON)
    :param file_path: the file path where the data will be saved, ``str``
    :param mode: the mode in which the file is opened (e.g. wt, wb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    """
    with open(file=file_path, mode=mode, encoding=encoding) as json_file:
        json.dump(data, json_file, indent=4)
