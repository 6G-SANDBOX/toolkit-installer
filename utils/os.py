import os
import shutil
from typing import List

from utils.logs import msg

CURRENT_DIRECTORY = os.getcwd()
DOTENV_PATH = os.path.join(CURRENT_DIRECTORY, ".env")
PYPROJECT_TOML_PATH = os.path.join(CURRENT_DIRECTORY, "pyproject.toml")
TEMP_DIRECTORY = os.path.join(os.getcwd(), ".temp")


def check_exist_directory(path: str) -> bool:
    """
    Check if the directory exists

    :param path: the path to the directory, ``str``
    :return: whether the directory exists, ``bool``
    """
    return os.path.exists(path=path)


def create_directory(path: str) -> None:
    """
    Create the directory

    :param path: the path to the directory, ``str``
    """
    if not check_exist_directory(path=path):
        os.makedirs(path)


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
    return directories


def remove_directory(path: str) -> None:
    """
    Remove the directory

    :param path: the path to the directory, ``str``
    """
    if check_exist_directory(path=path):
        shutil.rmtree(path)
