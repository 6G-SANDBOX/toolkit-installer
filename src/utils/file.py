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