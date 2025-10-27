import json
from typing import Dict, List

import yaml

from utils.logs import msg
from utils.os import is_file
from utils.questionary import ask_confirm, ask_text

SITES_SKIP_KEYS = {
    "site_dns",
    "site_hypervisor",
    "site_onegate",
    "site_s3_server",
    #"site_routemanager",
    "site_available_components",
}


def is_encrypted_ansible(file_path: str) -> bool:
    """
    Check if a file is an Ansible Vault encrypted file

    :param file_path: the path to the file to be checked, ``str``
    :return: whether the file is an Ansible Vault encrypted file, ``bool``
    """
    file = load_file(file_path=file_path)
    return file.startswith("$ANSIBLE_VAULT;")


def load_file(file_path: str, mode: str = "rt", encoding: str = "utf-8") -> str:
    """
    Load the content from a file as a string or a list of lines

    :param file_path: the path to the file to be loaded (e.g. txt, markdown), ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the content of the file, ``str``
    """
    if not is_file(path=file_path):
        msg(level="error", message=f"File not found: {file_path}")
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
    if not is_file(path=file_path):
        msg(level="error", message=f"File not found: {file_path}")
    with open(file=file_path, mode=mode, encoding=encoding) as yaml_file:
        return yaml.safe_load(stream=yaml_file)


def loads_json(data: str) -> Dict | None:
    """
    Load the given data as JSON

    :param data: the JSON data to be loaded, ``str``
    :return: the JSON data loaded, ``Dict``
    """
    if data is None or data == "":
        return None
    return json.loads(data)


def read_component_site_variables(data: Dict) -> Dict:
    """
    Read the given data as YAML

    :param data: the YAML data to be read, ``Dict``
    :return: the YAML data read, ``Dict``
    """
    aux = {}
    for key, value in data.items():
        if isinstance(value, Dict):
            msg(level="info", message=f"Reading nested fields in {key}:")
            aux[key] = read_site_yaml(value)
        elif isinstance(value, str):
            aux[key] = ask_text(
                message=f"Reading the value of {key}. This key indicates {value}:"
            )
            if key == "template_id" or key == "image_id":
                aux[key] = int(aux[key])
        else:
            msg(
                level="info",
                message=f"Reading the value of {key}. This key indicates {value}:",
            )
            aux[key] = value
    return aux


def read_site_yaml(data: Dict) -> Dict:
    """
    Read the given data as YAML

    :param data: the YAML data to be read, ``Dict``
    :return: the YAML data read, ``Dict``
    """
    aux = {}
    for key, value in data.items():
        if key in SITES_SKIP_KEYS:
            continue
        elif isinstance(value, Dict):
            msg(level="info", message=f"Reading nested fields in {key}:")
            aux[key] = read_site_yaml(value)
        elif isinstance(value, List):
            aux[key] = [
                int(item.strip())
                for item in ask_text(
                    message=f"Reading the value of {key} separated by commas. For example: 0, 1, 2:",
                    default=str(value),
                ).split(",")
            ]
        elif isinstance(value, str):
            aux[key] = ask_text(message=f"Reading the value of {key}:", default=value)
        elif isinstance(value, int):
            aux[key] = int(
                ask_text(message=f"Enter the value of {key}:", default=str(value))
            )
        elif isinstance(value, bool):
            new_value = ask_confirm(message=f"Enter the value of {key}:", default=value)
            aux[key] = new_value
        else:
            aux[key] = value
    return aux


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


def save_yaml_file(
    data, file_path: str, mode: str = "wt", encoding: str = "utf-8"
) -> None:
    """
    Save the data to a YAML file

    :param data: the data to be saved (must be serializable to YAML)
    :param file_path: the file path where the data will be saved, ``str``
    :param mode: the mode in which the file is opened (e.g. wt, wb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    """
    with open(file=file_path, mode=mode, encoding=encoding) as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False, sort_keys=False)
