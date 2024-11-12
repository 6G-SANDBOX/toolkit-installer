import pyfiglet

from src.utils.cli import run_command
from src.utils.logs import msg

def generate_banner(message: str) -> None:
    """
    Generate an ASCII banner with a message
    
    :param message: the message to display in the banner, ``str``
    """
    ascii_banner = pyfiglet.figlet_format(message)
    print(ascii_banner)
    
def check_user() -> None:
    """
    Check if the script is being run as root
    """
    print()
    msg("info", "[USER CHECK]")
    print()
    res = run_command("whoami")
    if res["rc"] != 0:
        msg("error", "Could not run woami command for user checking")
    if res["stdout"] != "root":
        msg("error", "Current user: " + res["stdout"] + "Please, run this script as root. The script requires root acces in order to modify /etc/one/oned.conf configuration file.")

def check_one_health() -> None:
    """
    Check the health of the OpenNebula installation
    """
    print()
    msg("info", "[OPENNEBULA HEALTHCHECK]")
    print()
    # Check that CLI tools are working and can be used => this implies that XMLRPC API is healthy and reachable
    command = "onevm list"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed. Command: " + command)

    command = "onevm list"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed. Command: " + command)

    command = "onedatastore list"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed. Command: " + command)

    command = "oneflow list"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed. Command: " + command)

    # Testing onegate health with curl
    command = "curl " + get_onegate_endpoint()
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed. Command: " + command)

    # CHANGE: pending to add futher health checks
    msg("info", "OpenNebula is healthy")

def get_onegate_endpoint() -> str:
    command = "cat /etc/one/oned.conf | grep 'ONEGATE_ENDPOINT ='" # Mejor entrar en el fichero y aplicar una expresión regular
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "Unable to run '" + command + "'")
    if not res["stdout"]:
        msg("error", "ONEGATE_ENDPOINT not found in the OpenNebula configuration")
    return res["stdout"].split('"')[1]