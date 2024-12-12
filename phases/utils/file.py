import os
import json
import tomlkit

from ruamel.yaml import YAML
from dotenv import load_dotenv

DOTENV_PATH = os.path.join(os.getcwd(), ".env")

def load_file(file_path: str, mode: str, encoding: str) -> str:
    """
    Load the content from a file as a string or a list of lines.
    
    :param file_path: the path to the file to be loaded (e.g. txt, markdown), ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the data loaded from the file, ``str`` or ``list[str]``
    """
    with open(file_path, mode=mode, encoding=encoding) as file:
        return file.read()

def load_yaml(file_path: str, mode: str, encoding: str) -> dict:
    """
    Load data from a YAML file

    :param file_path: the path to the YAML file to be loaded, ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the data loaded from the YAML file, ``dict``
    """
    yaml = YAML(typ="safe")
    yaml.indent(sequence=4, offset=2)
    yaml.preserve_quotes = True
    with open(file_path, mode=mode, encoding=encoding) as yaml_file:
        return yaml.load(yaml_file)

def loads_json(data: str) -> dict:
    """
    Load the given data as JSON
    
    :param data: the JSON data to be loaded, ``str``
    :return: the JSON data loaded, ``dict``
    """
    if data is None or data == "":
        return None
    return json.loads(data)

def loads_toml(file_path: str, mode: str, encoding: str) -> dict:
    """
    Load data from a TOML file

    :param file_path: the path to the TOML file to be loaded, ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the data loaded from the TOML file, ``dict``
    """
    with open(file_path, mode=mode, encoding=encoding) as toml_file:
        return tomlkit.loads(toml_file.read())

def load_dotenv_file() -> None:
    """
    Load the .env file in the current working directory
    """
    load_dotenv(dotenv_path=DOTENV_PATH)

def update_dotenv_file(key: str, value) -> None:
    """
    Update the .env file with the given data
    
    :param key: the key of the environment variable, ``str``
    :param value: the value of the environment variable
    """
    lines = []
    key_found = False
    with open(DOTENV_PATH, "rt") as file:
        for line in file:
            if line.strip().startswith(f"{key}="):
                lines.append(f"{key}=\"{value}\"\n")
                key_found = True
            else:
                lines.append(line)

    if key_found:
        with open(DOTENV_PATH, "w") as file:
            file.writelines(lines)
    
def get_env_var(var_name: str) -> str:
    """
    Get the value of an environment variable
    
    :param var_name: the name of the environment variable, ``str``
    :return: the value of the environment variable, ``str``
    """
    return os.getenv(var_name)

def save_file(data, file_path: str, mode: str, encoding: str) -> None:
    """
    Save the given data to a file
    
    :param data: the data to be saved to the file, ``str``
    :param file_path: the path to the file to be saved, ``str``
    :param mode: the mode in which the file is opened (e.g. wt, wb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    """
    with open(file_path, mode=mode, encoding=encoding) as file:
        file.write(data)

def save_json(data, file_path: str) -> None:
    """
    Save the data to a JSON file
    
    :param data: the data to be saved (must be serializable to JSON)
    :param file_path: The file path where the data will be saved, ``str``
    """
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)