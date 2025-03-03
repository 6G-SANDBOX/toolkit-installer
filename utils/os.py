import os
import shutil

from utils.logs import msg

DOTENV_PATH = os.path.join(os.getcwd(), ".env")

def check_exist_directory(path: str) -> bool:
    """
    Check if the directory exists
    
    :param path: the path to the directory, ``str``
    :return: whether the directory exists, ``bool``
    """
    return os.path.exists(path=path)

def get_current_directory() -> str:
    """
    Get the current working directory
    
    :return: the current working directory, ``str``
    """
    current_directory = os.getcwd()
    msg(level="debug", message=f"Current working directory: {current_directory}")
    return current_directory

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

def remove_directory(path: str) -> None:
    """
    Remove the directory
    
    :param path: the path to the directory, ``str``
    """
    if check_exist_directory(path=path):
        shutil.rmtree(path)
        msg(level="debug", message=f"Directory {path} removed")
    else:
        msg(level="warning", message=f"Directory {path} does not exist")
