import os
import shutil
from typing import List

from utils.logs import msg

CURRENT_DIRECTORY = os.getcwd()
DOTENV_PATH = os.path.join(CURRENT_DIRECTORY, ".env")
PYPROJECT_TOML_PATH = os.path.join(CURRENT_DIRECTORY, "pyproject.toml")
TEMP_DIRECTORY = os.path.join(os.getcwd(), ".temp")


def exist_directory(path: str) -> bool:
    """
    Check if the directory exists

    :param path: the path to the directory, ``str``
    :return: whether the directory exists, ``bool``
    """
    return os.path.exists(path=path)


def get_dotenv_var(key: str) -> str:
    """
    Get the value of an environment variable

    :param key: the name of the environment variable, ``str``
    :return: the value of the environment variable, ``str``
    """
    value = os.getenv(key=key)
    if value is None:
        msg(level="error", message=f"Environment variable {key} not found")
    msg(level="debug", message=f"Environment variable {key} value: {value}")
    return value


def is_directory(path: str) -> bool:
    """
    Check if the path is a directory

    :param path: the path to the directory, ``str``
    :return: whether the path is a directory, ``bool``
    """
    return os.path.isdir(path)


def is_file(path: str) -> bool:
    """
    Check if the path is a file

    :param path: the path to the file, ``str``
    :return: whether the path is a file, ``bool``
    """
    return os.path.isfile(path)


def join_path(*args) -> str:
    """
    Join the paths

    :param args: the paths to be joined, ``List[str]
    :return: the joined path, ``str``
    """
    return os.path.join(*args)


def list_directory(path: str) -> List[str]:
    """
    List the files and directories in the directory

    :param path: the path to the directory, ``str``
    :return: the list of files and directories, ``List[str]``
    """
    directories = []
    for directory in os.listdir(path=path):
        if os.path.isdir(os.path.join(path, directory)) and not directory.startswith(
            "."
        ):
            directories.append(directory)
    return sorted(directories)


def make_directory(path: str) -> None:
    """
    Create the directory

    :param path: the path to the directory, ``str``
    """
    os.makedirs(path, exist_ok=True)


def remove_directory(path: str) -> None:
    """
    Remove the directory

    :param path: the path to the directory, ``str``
    """
    if is_directory(path=path):
        shutil.rmtree(path)


def remove_file(file_path: str) -> None:
    """
    Remove the file

    :param file_path: the path to the file, ``str``
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def rename_directory(old_path: str, new_path: str) -> None:
    """
    Rename the directory

    :param old_path: the old path to the directory, ``str``
    :param new_path: the new path to the directory, ``str``
    """
    if is_directory(path=old_path):
        shutil.move(old_path, new_path)
