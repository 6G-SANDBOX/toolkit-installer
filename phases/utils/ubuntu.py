from phases.utils.cli import run_command
from phases.utils.logs import msg

def update_ubuntu_package() -> None:
    msg("info", "[UBUNTU PACKAGE UPDATE]")
    res = run_command("apt update")
    if res["rc"] != 0:
        msg("error", "Could not update Ubuntu packages")

def get_user() -> dict:
    res = run_command("whoami")
    if res["rc"] != 0:
        msg("error", "Could not run whoami command for user checking")
    return res["stdout"]