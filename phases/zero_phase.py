import os
import pyfiglet

from phases.utils.file import loads_toml, load_dotenv_file, get_env_var
from phases.utils.logs import msg
from phases.utils.one import check_one_health
from phases.utils.temp import create_temp_directory
from phases.utils.ubuntu import get_user

def _generate_banner(message: str) -> None:
    """
    Generate an ASCII banner with a message
    
    :param message: the message to display in the banner, ``str``
    """
    ascii_banner = pyfiglet.figlet_format(message)
    print(ascii_banner)

def zero_phase() -> None:
    pyproject_toml = os.path.join(os.getcwd(), "pyproject.toml")
    version = loads_toml(file_path=pyproject_toml, mode="rt", encoding="utf-8")["project"]["version"]
    load_dotenv_file()
    banner_message = get_env_var("BANNER_MESSAGE")
    _generate_banner(message=banner_message)
    _generate_banner(message=version)
    msg("info", "ZERO PHASE")
    user = get_user()
    if user != "root":
        msg("error", "This script must be run as root")
    check_one_health()
    create_temp_directory()