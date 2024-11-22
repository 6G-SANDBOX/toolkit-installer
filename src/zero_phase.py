import os
import re
import pyfiglet

from src.utils.dotenv import load_dotenv_file
from src.utils.cli import run_command
from src.utils.file import load_file, loads_toml
from src.utils.logs import msg
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

def check_one_health() -> None:
    """
    Check the health of the OpenNebula installation
    """
    msg("info", "[OPENNEBULA HEALTHCHECK]")
    # Check that CLI tools are working and can be used => this implies that XMLRPC API is healthy and reachable
    command = "onevm list"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error",  f"OpenNebula CLI healthcheck failed. Command: '{command}'")

    command = "onedatastore list"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error",  f"OpenNebula CLI healthcheck failed. Command: '{command}'")

    command = "oneflow list"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", f"OpenNebula CLI healthcheck failed. Command: '{command}'")

    command = "onemarket list"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", f"OpenNebula CLI healthcheck failed. Command: '{command}'")

    oned_config_path = os.path.join("/etc", "one", "oned.conf")
    oned_conf = load_file(file_path=oned_config_path, mode="rt", encoding="utf-8")
    match = re.search(r"^\s*ONEGATE_ENDPOINT\s*=\s*\"([^\"]+)\"", oned_conf, re.MULTILINE)
    if match is None:
        msg("error", "Could not find ONEGATE_ENDPOINT in oned.conf")
    onegate_endpoint = match.group(1)
    command = f"curl {onegate_endpoint}"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", f"OpenNebula CLI healthcheck failed. Command: '{command}'")

    msg("info", "OpenNebula is healthy")

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