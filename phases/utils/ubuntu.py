from phases.utils.cli import run_command
from phases.utils.logs import msg

def get_user() -> dict:
    msg("info", "Checking Ubuntu user")
    res = run_command("whoami")
    if res["rc"] != 0:
        msg("error", "Could not run whoami command for user checking")
    data = res["stdout"]
    msg("info", f"Ubuntu user: {data}")
    return data