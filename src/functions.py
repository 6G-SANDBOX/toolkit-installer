import subprocess
import sys
import json
import requests
import zipfile
import os
import questionary
import yaml
from datetime import datetime
from time import sleep
from github import Github


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
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        return_code = result.returncode
        return {"rc": return_code, "stdout": stdout, "stderr": stderr}
    except Exception as e:
        return {"rc": -1, "stdout": None, "stderr": str(e)}

def check_user():
    res = run_command("whoami")
    if res["rc"] != 0:
        msg("error", "Could not run woami command for user checking")
        sys.exit(255)
    if res["stdout"] != "root":
        msg("error", "Current user: " + res["stdout"] + "   Please, run this script as root. The script requires root acces in order to modify /etc/one/oned.conf configuration file.")
        sys.exit(255)
    return 0


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
    return False



def set_market_monitoring_interval(new_value):
    old_value = None

    try:
        with open("/etc/one/oned.conf", 'r') as file:
            lines = file.readlines()

        # Modify the MONITORING_INTERVAL_MARKET setting
        for i, line in enumerate(lines):
            if line.startswith('MONITORING_INTERVAL_MARKET'):
                # Extract the old value
                old_value = int(line.split('=')[1].strip())
                # Update the line with the new value
                lines[i] = f"MONITORING_INTERVAL_MARKET    = {new_value}\n"
                break

        if old_value is not None:
            # Write the updated content back to the file
            with open("/etc/one/oned.conf", 'w') as file:
                file.writelines(lines)
            msg("info", "Market monitoring interval set to " + str(new_value))

    except Exception as e:
        msg("error", e)
        sys.exit(255)

    return old_value

def restart_oned():
        msg("info", "Restarting oned...")
        res = run_command("systemctl restart opennebula")
        if res["rc"] != 0:
            msg("error", "Unable to restart OpenNebula. Error message:")
            msg("error", res["stderr"])
            sys.exit(255)
        sleep(10)
        check_one_health()
        return 0


def marketapps_ready(ID):
    res = run_command("onemarket show -j " + str(ID))
    if res["rc"] != 0:
        msg("error", "Could not run 'onemarket show -j " + str(ID) + "'. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    market_dict = json.loads(res["stdout"])
    if not market_dict["MARKETPLACE"]["MARKETPLACEAPPS"]:
        return False
    return True

# Download appliance with user intervention. Lists appliances containing the specified name and lets the user select the version and datastore
def download_appliance_guided(name):
    res = run_command("onemarketapp list -j")
    if res["rc"] != 0:
        msg("error", "Could not run 'onemarketapp list -j'. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    apps_dict = json.loads(res["stdout"])
    apps_list = apps_dict["MARKETPLACEAPP_POOL"]["MARKETPLACEAPP"]
    appliance_versions = []
    for app in apps_list:
        if name.lower() in app["NAME"].lower():
            appliance_versions.append({"ID": app["ID"], "name": app["NAME"]})
    msg("info", "Available " + name + " versions:")
    for version in appliance_versions:
        print("[  ID: " + version["ID"] + "  |  Name: " + version["name"] + "  ]")

    valid_ids = {int(version["ID"]) for version in appliance_versions}
    while True:
        try:
            ID = int(questionary.text("Please, introduce the ID of the desired " + name + " version:").ask())
            if ID in valid_ids:
                break
            else:
                msg("info", "Invalid input. Please enter a valid ID.")
        except ValueError:
            msg("info", "Invalid input. Please enter a valid integer.")
    print("Chosen appliance ID: " + str(ID))

    image_ds_list = list_image_datastores()
    msg("info", "Available image datastores:")
    for ds in image_ds_list:
        print("[  ID: " + ds["ID"] + "  |  Name: " + ds["NAME"] + "  ]")


    valid_ids = {int(ds["ID"]) for ds in image_ds_list}
    while True:
        try:
            ds_ID = int(questionary.text("Please, introduce the ID of the datastore to download the " + name + " appliance:").ask())
            if ds_ID in valid_ids:
                break
            else:
                msg("info", "Invalid input. Please enter a valid datastore ID.")
        except ValueError:
            msg("info", "Invalid input. Please enter a valid integer.")

    cmd = "onemarketapp export " + str(ID) + " " + name.replace(' ', '_')  + " -d "  + str(ds_ID)
    res = run_command(cmd)
    if res["rc"] != 0:
        msg("error", "Could not run '" + cmd + "'Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    result_dict = parse_output(res["stdout"])
    for image_id in result_dict["IMAGE"]:
        wait_for_image(image_id)
    return result_dict


def list_image_datastores():
    res = run_command("onedatastore list -j")
    if res["rc"] != 0:
        msg("error", "Could not run 'onedatastore list -j'Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    ds_dict = json.loads(res["stdout"])
    ds_list = ds_dict["DATASTORE_POOL"]["DATASTORE"]

    image_ds_list = []
    for ds in ds_list:
        if ds["TEMPLATE"]["TYPE"] == "IMAGE_DS":
            image_ds_list.append(ds)
    return image_ds_list

def parse_output(output):
    lines = output.strip().split('\n')
    result = {}
    current_type = None

    for line in lines:
        line = line.strip()
        if line.startswith('IMAGE'):
            current_type = 'IMAGE'
            result[current_type] = []
        elif line.startswith('VMTEMPLATE'):
            current_type = 'VMTEMPLATE'
            result[current_type] = []
        elif line.startswith('SERVICE_TEMPLATE'):
            current_type = 'SERVICE_TEMPLATE'
            result[current_type] = []
        elif line.startswith('ID:'):
            if current_type:
                _, id_value = line.split(':')
                result[current_type].append(int(id_value.strip()))

    return result


def wait_for_image(ID):
    msg("info", "Waiting for image ID:" + str(ID) + " to be ready... This process can take several minutes.")
    while True:
        cmd = "oneimage show -j " + str(ID)
        res = run_command(cmd)
        if res["rc"] != 0:
            msg("error", "Could not run '" + cmd + "'Error:")
            msg("error", res["stderr"])
            sys.exit(255)
        img_dict = json.loads(res["stdout"])
        if img_dict["IMAGE"]["STATE"] == "1":
            break
        sleep(1)
    msg("info", "Image with ID " + str(ID) + " successfully downloaded.")




def download_repo(repo_name):
    # Construct the URL to download the repository as a ZIP file
    url = f"https://github.com/{repo_name}/archive/refs/heads/main.zip"

    # Send a GET request to download the ZIP file
    response = requests.get(url)

    # Save the ZIP file locally
    zip_path = "repo.zip"
    with open(zip_path, "wb") as f:
        f.write(response.content)

    # Extract the ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("repo")

    # Remove the ZIP file
    os.remove(zip_path)

def remove_repo():
    res = run_command("rm -rf ./repo")
    if res["rc"] != 0:
        msg("error", "Could not remove repo folder, skipping...")
        msg("error", res["stderr"])
    return 0


def extract_appliance_values(repo_name):
    # Download and extract the repository
    download_repo(repo_name)

    # Path to the extracted repository
    repo_path = f"repo/{repo_name.split('/')[1]}-main"
    # List of dictionaries to store the app names and appliance values
    app_data = []

    # Walk through the repository directory
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file == "public.yaml" and ".tnlcm" in root:
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    file_data = yaml.safe_load(f)
                    app_name = root.split(os.sep)[2]  # Get the app name from the path
                    appliance_value = file_data.get("metadata", {}).get("appliance", None)
                    if appliance_value:
                        app_data.append(appliance_value + "/download/0")
    remove_repo()
    return app_data


# Matches appliance URLs from the 6GLibrary repo with Sandbox Marketplace APPs
def match_appliance_urls(urls):
    res = run_command("onemarketapp list -j")
    if res["rc"] != 0:
        msg("error", "Could not run 'onemarketapp list -j'. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    apps_dict = json.loads(res["stdout"])
    apps_list = apps_dict["MARKETPLACEAPP_POOL"]["MARKETPLACEAPP"]
    matching_apps_list = []
    for app in apps_list:
        if app["SOURCE"] in urls:
            matching_apps_list.append(app)
    return matching_apps_list
