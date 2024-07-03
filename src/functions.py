import subprocess
import sys
import json
from datetime import datetime


def msg(msg_type, *args):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if msg_type == "info":
        print(f"[{timestamp}] => INFO:", *args)
    elif msg_type == "debug":
        print(f"[{timestamp}] => DEBUG:", *args)
    elif msg_type == "warning":
        print(f"[{timestamp}] => WARNING [!]:", *args)
    elif msg_type == "error":
        print(f"[{timestamp}] => ERROR [!!]:", *args)
        return 1
    else:
        print(f"[{timestamp}] => UNKNOWN [?!]:", *args)
        return 2
    return 0


def run_command(command):
    """
    Run a bash command and return the stdout, stderr, and return code.

    Parameters:
    command (str): The bash command to run.

    Returns:
    tuple: A tuple containing stdout, stderr, and return code.

    Example use:
    res = run_command("echo hello!")
    if res["rc"] == 0:
        print("it worked")
    """
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout = result.stdout
        stderr = result.stderr
        return_code = result.returncode
        return {"rc": return_code, "stdout": stdout, "stderr": stderr}
    except Exception as e:
        return {"rc": -1, "stdout": None, "stderr": str(e)}


def check_one_health():

    # Check that CLI tools are working and can be used => this implies that XMLRPC API is healthy and reachable
    res = run_command("onevm list")
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed.")
        sys.exit(255) # For UNIX systems, exit code must be unsiged in the 0-255 range
    res = run_command("onevm list")
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed.")
        sys.exit(255)
    res = run_command("onedatastore list")
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed.")
        sys.exit(255)

    # Pending to add futher health checks

    msg("info", "OpenNebula is healthy")
    return 0





def add_sandbox_marketplace():
    template_content = """
NAME = "6GSandbox"
DESCRIPTION = "6GSandbox Appliance repository"
ENDPOINT = "https://marketplace.mobilesandbox.cloud:9443/"
MARKET_MAD = one
"""

    # Write the content to a file
    with open("./market_template", 'w') as file:
        file.write(template_content)
    res = run_command("onemarket create market_template")
    if res["rc"] != 0:
        msg("error", "The 6GSANDBOX marketplace could not be registered. Please, review the market_template file. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    market_id = res["stdout"].split()[1]
    msg("info", "6GSANDBOX marketplace registered successfully with ID " + market_id)
    run_command("rm market_template")
    return int(market_id)



def find_sandbox_marketplace():
    res = run_command("onemarket list -j")
    markets_dict = json.loads(res["stdout"])
    for marketplace in markets_dict["MARKETPLACE_POOL"]["MARKETPLACE"]:
        if marketplace["NAME"] == "6GSandbox":
            if marketplace["TEMPLATE"]["ENDPOINT"] == "https://marketplace.mobilesandbox.cloud:9443/":
                msg("info", "6GSANDBOX marketplace already present with ID " + marketplace["ID"])
                return int(marketplace["ID"])
    msg("info", "6GSANDBOX marketplace not present, adding...")
    return False
