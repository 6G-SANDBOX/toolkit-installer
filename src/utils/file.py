import os
import json

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

TEMP_DIRECTORY = os.path.join(os.getcwd(), ".temp")

def save_temp_file(data, file_path: str, mode: str, encoding: str) -> str:
    """
    Save the given data to a temporary file
    
    :param data: the data to be saved to the file, ``str``
    :param file_path: the path to the file to be saved, ``str``
    :param mode: the mode in which the file is opened (e.g. wt, wb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the path to the file where the data was saved, ``str``
    """
    if not os.path.exists(TEMP_DIRECTORY):
        os.makedirs(TEMP_DIRECTORY)
    file_path = os.path.join(TEMP_DIRECTORY, file_path)
    with open(file_path, mode=mode, encoding=encoding) as file:
        file.write(data)
    return file_path