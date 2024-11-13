import os
import json

from tempfile import NamedTemporaryFile

def load_file(file_path: str, mode: str, encoding: str) -> str:
    """
    Load the content from a file
    
    :param file_path: the path to the file to be loaded (e.g. txt, markdown), ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the data loaded from the file, ``str``
    """
    with open(file_path, mode=mode, encoding=encoding) as file:
        return file.read()

def loads_json(data: str) -> dict:
    """
    Load the given data as JSON
    
    :param data: the JSON data to be loaded, ``str``
    :return: the JSON data loaded, ``dict``
    """
    return json.loads(data)

def save_file(data: str, file_path: str, mode: str, encoding: str) -> None:
    """
    Save the given data in a file
    
    :param data: the text to be saved (e.g. txt, markdown), ``str``
    :param file_path: the file path where the data will be saved, ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    """
    with open(file_path, mode=mode, encoding=encoding) as file:
        file.write(data)

TEMP_DIRECTORY = os.path.join("root", "temp")

def save_temp_file(data, file_name: str, mode: str, encoding: str, extension: str) -> str:
    """
    Create a temporary file with the given data
    
    :param data: the data to be written in the file, ``str``
    :param file_name: the name of the file, ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :param extension: the extension of the file, ``str``
    :return: the path to the temporary file, ``str``
    """
    os.makedirs(TEMP_DIRECTORY, exist_ok=True)
    with NamedTemporaryFile(delete=False, prefix=file_name, suffix=f".{extension}", mode=mode, encoding=encoding) as temp_file:
        temp_file.write(data)
        temp_file_path = temp_file.name
    
    return temp_file_path