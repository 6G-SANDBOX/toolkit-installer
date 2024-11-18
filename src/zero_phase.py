import pyfiglet

from src.utils.dotenv import load_dotenv_file
from src.utils.cli import run_command
from src.utils.file import loads_toml
from src.utils.logs import msg
from src.utils.temp import create_temp_directory

def _generate_banner(message: str) -> None:
    """
    Generate an ASCII banner with a message
    
    :param message: the message to display in the banner, ``str``
    """
    ascii_banner = pyfiglet.figlet_format(message)
    print(ascii_banner)
    
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

    # Testing onegate health with curl
    command = "cat /etc/one/oned.conf | grep 'ONEGATE_ENDPOINT ='" # Mejor entrar en el fichero y aplicar una expresión regular
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", f"Unable to run '{command}' command")
    if not res["stdout"]:
        msg("error", "ONEGATE_ENDPOINT not found in the OpenNebula configuration")
    onegate_endpoint = res["stdout"].split('"')[1]
    
    command = f"curl {onegate_endpoint}"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", f"OpenNebula CLI healthcheck failed. Command: '{command}'")

    # CHANGE: pending to add futher health checks
    msg("info", "OpenNebula is healthy")

def zero_phase() -> None:
    """
    The zero phase of the 6G-SANDBOX deployment
    """
    __version__ = loads_toml("pyproject.toml", "rt", "utf-8")["tool"]["poetry"]["version"]
    load_dotenv_file()
    _generate_banner(message="6G-SANDBOX TOOLKIT")
    _generate_banner(message=__version__)
    _check_user()
    check_one_health()
    create_temp_directory()