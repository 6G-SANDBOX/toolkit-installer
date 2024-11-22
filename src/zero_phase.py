import pyfiglet

from src.utils.dotenv import load_dotenv_file, get_env_var
from src.utils.file import loads_toml
from src.utils.logs import msg
from src.utils.one import check_one_health
from src.utils.temp import create_temp_directory
from src.utils.ubuntu import update_ubuntu_package, install_ansible_core, get_user

def _generate_banner(message: str) -> None:
    """
    Generate an ASCII banner with a message
    
    :param message: the message to display in the banner, ``str``
    """
    ascii_banner = pyfiglet.figlet_format(message)
    print(ascii_banner)

def check_user() -> None:
    user = get_user()
    if user != "root":
        msg("error", "This script must be run as root")

def zero_phase() -> None:
    msg("info", "ZERO PHASE")
    __version__ = loads_toml("pyproject.toml", "rt", "utf-8")["tool"]["poetry"]["version"]
    load_dotenv_file()
    banner_message = get_env_var("BANNER_MESSAGE")
    _generate_banner(message=banner_message)
    _generate_banner(message=__version__)
    update_ubuntu_package()
    install_ansible_core()
    check_user()
    check_one_health()
    create_temp_directory()