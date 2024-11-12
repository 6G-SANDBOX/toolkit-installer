import os

from dotenv import load_dotenv

def load_dotenv_file() -> None:
    """
    Load the .env file in the current working directory
    """
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

def get_env_var(var_name: str) -> str:
    """
    Get the value of an environment variable
    
    :param var_name: the name of the environment variable, ``str``
    :return: the value of the environment variable, ``str``
    """
    return os.getenv(var_name)