from src.utils.cli import run_command
from src.utils.logs import msg

def update_ubuntu_package() -> None:
    msg("info", "[UBUNTU PACKAGE UPDATE]")
    res = run_command("apt update")
    if res["rc"] != 0:
        msg("error", "Could not update Ubuntu packages")

def install_ansible_core() -> None:
    msg("info", "[ANSIBLE INSTALLATION]")
    res = run_command("apt install -y ansible-core")
    if res["rc"] != 0:
        msg("error", "Could not install ansible-core")

def get_user() -> dict:
    res = run_command("whoami")
    if res["rc"] != 0:
        msg("error", "Could not run whoami command for user checking")
    return res["stdout"]