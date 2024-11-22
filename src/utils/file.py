import json
import yaml
import tomlkit

def load_file(file_path: str, mode: str, encoding: str, as_lines: bool = False) -> str:
    """
    Load the content from a file as a string or a list of lines.
    
    :param file_path: the path to the file to be loaded (e.g. txt, markdown), ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :param as_lines: if True, returns a list of lines. Otherwise, returns a single string, ``bool``
    :return: the data loaded from the file, ``str`` or ``list[str]``
    """
    with open(file_path, mode=mode, encoding=encoding) as file:
        return file.readlines() if as_lines else file.read()

def load_yaml(file_path: str, mode: str, encoding: str) -> dict:
    """
    Load data from a YAML file

    :param file_path: the path to the YAML file to be loaded, ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the data loaded from the YAML file, ``dict``
    """
    with open(file_path, mode=mode, encoding=encoding) as yaml_file:
        return yaml.safe_load(yaml_file)

def loads_json(data: str) -> dict:
    """
    Load the given data as JSON
    
    :param data: the JSON data to be loaded, ``str``
    :return: the JSON data loaded, ``dict``
    """
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

def save_file(data, file_path: str, mode: str, encoding: str, as_lines: bool = False) -> None:
    """
    Save the given data to a file
    
    :param data: the data to be saved to the file, ``str``
    :param file_path: the path to the file to be saved, ``str``
    :param mode: the mode in which the file is opened (e.g. wt, wb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :param as_lines: if True, returns a list of lines. Otherwise, returns a single string, ``bool``
    """
    with open(file_path, mode=mode, encoding=encoding) as file:
        file.writelines(data) if as_lines else file.write(data)

def save_yaml(data, file_path: str) -> None:
    """
    Save the data to a YAML file
    
    :param data: the data to be saved (must be serializable to YAML)
    :param file_path: The file path where the data will be saved, ``str``
    """
    with open(file_path, "w") as yaml_file:
        yaml.safe_dump(data, yaml_file, default_flow_style=False)