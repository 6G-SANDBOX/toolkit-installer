import os

TEMP_DIRECTORY = os.path.join(os.getcwd(), ".temp")

def load_temp_file(file_path: str, mode: str, encoding: str) -> str:
    """
    Load the content from a temporary file
    
    :param file_path: the path to the file to be loaded (e.g. txt, markdown), ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the data loaded from the file, ``str``
    """
    file_path = os.path.join(TEMP_DIRECTORY, file_path)
    with open(file_path, mode=mode, encoding=encoding) as file:
        return file.read()

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

def save_temp_directory(directory_path: str) -> str:
    """
    Save the given directory to a temporary directory
    
    :param directory_path: the path to the directory to be saved, ``str``
    :return: the path to the directory where the data was saved, ``str``
    """
    temp_directory = os.path.join(TEMP_DIRECTORY, directory_path)
    os.makedirs(temp_directory, exist_ok=True)
    return temp_directory

def temp_path(file_path: str) -> str:
    """
    Create a temporary path for the given file
    
    :param file_path: the path to the file, ``str``
    :return: the temporary path for the file, ``str``
    """
    return os.path.join(TEMP_DIRECTORY, file_path)