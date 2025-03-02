import os

from utils.logs import msg

DOTENV_PATH = os.path.join(os.getcwd(), ".env")
PYPROJECT_TOML_PATH = os.path.join(os.getcwd(), "pyproject.toml")

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
