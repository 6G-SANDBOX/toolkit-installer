import pyfiglet

from src.utils.dotenv import load_dotenv_file
from src.utils.cli import run_command
from src.utils.file import loads_toml
from src.utils.logs import msg
from src.utils.one import check_one_health
from src.utils.temp import create_temp_directory

def _generate_banner(message: str) -> None:
    """
    Generate an ASCII banner with a message
    
    :param message: the message to display in the banner, ``str``
    """
    ascii_banner = pyfiglet.figlet_format(message)
    print(ascii_banner)

def _update_ubuntu_package() -> None:
    msg("info", "[UBUNTU PACKAGE UPDATE]")
    res = run_command("apt update")
    if res["rc"] != 0:
        msg("error", "Could not update Ubuntu packages")

def _install_ansible_core() -> None:
    msg("info", "[ANSIBLE INSTALLATION]")
    res = run_command("apt install -y ansible-core")
    if res["rc"] != 0:
        msg("error", "Could not install ansible-core")

def _check_user() -> None:
    """
    Check if the script is being run as root
    """
    msg("info", "[USER CHECK]")
    res = run_command("whoami")
    if res["rc"] != 0:
        msg("error", "Could not run woami command for user checking")
    if res["stdout"] != "root":
        stdout = res["stdout"]
        msg("error", f"Current user: {stdout}. Please, run this script as root. The script requires root acces in order to modify /etc/one/oned.conf configuration file.")

def zero_phase() -> None:
    """
    The zero phase of the 6G-SANDBOX deployment
    """
    msg("info", "ZERO PHASE")
    _update_ubuntu_package()
    __version__ = loads_toml("pyproject.toml", "rt", "utf-8")["tool"]["poetry"]["version"]
    load_dotenv_file()
    _generate_banner(message="6G-SANDBOX TOOLKIT")
    _generate_banner(message=__version__)
    _install_ansible_core()
    _check_user()
    check_one_health()
    create_temp_directory()