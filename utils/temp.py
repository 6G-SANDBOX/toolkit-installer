import json
import os
import shutil

TEMP_DIRECTORY = os.path.join(os.getcwd(), ".temp")


def check_exist_directory(path: str) -> bool:
    """
    Check if the directory exists in temporary

    :param path: the path to the directory, ``str``
    :return: whether the directory exists, ``bool``
    """
    return os.path.exists(os.path.join(TEMP_DIRECTORY, path))


def check_exist_temp_directory() -> bool:
    """
    Check if the temporary directory exists

    :return: whether the temporary directory exists, ``bool``
    """
    return os.path.exists(TEMP_DIRECTORY)


def create_temp_directory() -> None:
    """
    Create temporary directory if it not exist
    """
    if not check_exist_temp_directory():
        os.makedirs(name=TEMP_DIRECTORY)


# def load_temp_file(file_path: str, mode: str, encoding: str) -> str:
#     """
#     Load the content from a temporary file

#     :param file_path: the path to the file to be loaded (e.g. txt, markdown), ``str``
#     :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
#     :param encoding: the file encoding (e.g. utf-8), ``str``
#     :return: the data loaded from the file, ``str``
#     """
#     file_path = os.path.join(TEMP_DIRECTORY, file_path)
#     with open(file_path, mode=mode, encoding=encoding) as file:
#         return file.read()

# def load_temp_json_file(file_path: str, mode: str, encoding: str) -> dict:
#     """
#     Load the content from a temporary JSON file

#     :param file_path: the path to the file to be loaded (e.g. txt, markdown), ``str``
#     :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
#     :param encoding: the file encoding (e.g. utf-8), ``str``
#     :return: the data loaded from the file, ``dict``
#     """
#     file_path = os.path.join(TEMP_DIRECTORY, file_path)
#     with open(file_path, mode=mode, encoding=encoding) as file:
#         return json.load(file)


def remove_directory(path: str) -> None:
    """
    Remove the directory

    :param path: the path to the directory, ``str``
    """
    if check_exist_directory(path=path):
        shutil.rmtree(os.path.join(TEMP_DIRECTORY, path))


def remove_temp_directory() -> None:
    """
    Remove temporary directory
    """
    if check_exist_temp_directory():
        shutil.rmtree(TEMP_DIRECTORY)


def save_temp_file(
    data, file_name: str, mode: str = "wt", encoding: str = "utf-8"
) -> str:
    """
    Save the given data to a temporary file

    :param data: the data to be saved to the file, ``str``
    :param file_name: the name of the file to be saved, ``str``
    :param mode: the mode in which the file is opened (e.g. wt, wb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the path to the file where the data was saved, ``str``
    """
    file_path = os.path.join(TEMP_DIRECTORY, file_name)
    with open(file=file_path, mode=mode, encoding=encoding) as file:
        file.write(data)
    return file_path


def save_temp_json_file(
    data, file_name: str, mode: str = "wt", encoding: str = "utf-8"
) -> str:
    """
    Save the given data to a temporary JSON file

    :param data: the data to be saved to the file, ``str``
    :param file_name: the name of the file to be saved, ``str``
    :param mode: the mode in which the file is opened (e.g. wt, wb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the path to the file where the data was saved, ``str``
    """
    file_path = os.path.join(TEMP_DIRECTORY, file_name)
    with open(file=file_path, mode=mode, encoding=encoding) as file:
        json.dump(data, file, indent=4)
    return file_path


def save_temp_directory(path: str) -> str:
    """
    Save the given directory to a temporary directory

    :param path: the path to the directory to be saved, ``str``
    :return: the path to the directory where the data was saved, ``str``
    """
    temp_directory = os.path.join(TEMP_DIRECTORY, path)
    if not check_exist_directory(path=path):
        os.makedirs(name=temp_directory)
    return temp_directory
