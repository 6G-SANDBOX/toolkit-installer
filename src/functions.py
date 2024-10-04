import subprocess
import sys
import json
import requests
import zipfile
import os
import questionary
import yaml
import shutil
import base64
from datetime import datetime
from time import sleep


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
    exit_code = process.returncode

    # Return the final stdout and exit code
    return {"rc": exit_code, "stdout": final_output}


def check_user():
    print()
    msg("info", "[USER CHECK]")
    print()
    res = run_command("whoami")
    if res["rc"] != 0:
        msg("error", "Could not run woami command for user checking")
        sys.exit(255)
    if res["stdout"] != "root":
        msg("error", "Current user: " + res["stdout"] + "   Please, run this script as root. The script requires root acces in order to modify /etc/one/oned.conf configuration file.")
        sys.exit(255)
    return 0


def check_one_health():
    print()
    msg("info", "[OPENNEBULA HEALTHCHECK]")
    print()
    # Check that CLI tools are working and can be used => this implies that XMLRPC API is healthy and reachable
    command = "onevm list"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed. Command: " + command)
        sys.exit(255) # For UNIX systems, exit code must be unsiged in the 0-255 range

    command = "onevm list"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed. Command: " + command)
        sys.exit(255)
    command = "onedatastore list"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed. Command: " + command)
        sys.exit(255)

    command = "oneflow list"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed. Command: " + command)
        sys.exit(255)

    # Testing onegate health with curl
    command = "curl " + get_onegate_endpoint()
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "OpenNebula CLI healthcheck failed. Command: " + command)
        sys.exit(255)


    # Pending to add futher health checks

    msg("info", "OpenNebula is healthy")
    return 0


def get_onegate_endpoint():
    command = "cat /etc/one/oned.conf | grep 'ONEGATE_ENDPOINT ='"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "Unable to run '" + command + "'")
        sys.exit(255)
    if not res["stdout"]:
        msg("error", "ONEGATE_ENDPOINT not found in the OpenNebula configuration.")
        sys.exit(255)
    return res["stdout"].split('"')[1]


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

# Checks whether the SANDBOX marketplace contains any APPs. If it does, it means that the marketplace has been monitored and is ready to be used
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

# Downloads appliance without user intervention.
def download_appliance(name, ID, ds_ID):
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


# Downloads appliance with user intervention. Lists appliances containing the specified name and lets the user select the version and datastore
def download_appliance_guided(name, appliance_type):
    res = run_command("onemarketapp list -j")
    if res["rc"] != 0:
        msg("error", "Could not run 'onemarketapp list -j'. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    apps_dict = json.loads(res["stdout"])
    apps_list = apps_dict["MARKETPLACEAPP_POOL"]["MARKETPLACEAPP"]
    appliance_versions = []
    # Filtering appliances by name and type
    for app in apps_list:
        if name.lower() in app["NAME"].lower():
            if appliance_type == "VM" and (app["TYPE"] == "1" or app["TYPE"] == "2"):
                appliance_versions.append(app)
            elif appliance_type == "SERVICE" and app["TYPE"] == "3":
                appliance_versions.append(app)
    #ID = select_elements(appliance_versions, elem_type= name + " appliance", action="download", display_field="NAME", select_single=True)["ID"]
    selected_app = select_elements(appliance_versions, elem_type= name + " appliance", action="download", display_field="NAME", select_single=True)
    ID = selected_app["ID"]
    NAME = selected_app["NAME"].replace(' ', '_')
    selected_datastore = select_elements(list_image_datastores(), elem_type="datastore", action="use", display_field="ID", select_single=True)
    ds_ID = selected_datastore["ID"]

    # Searching whether the appliance already exists in the cluster. If it exists, it returns it.
    found_appliance = appliance_search(NAME, appliance_type)
    if found_appliance is not False:
        msg("info", "VM template " + NAME + " already present, skipping download...")
        if appliance_type == "VM":
            return {'IMAGE': [], 'VMTEMPLATE': [found_appliance["ID"]]}
        elif appliance_type == "SERVICE":
            templates_list = []
            for role in found_appliance["TEMPLATE"]["BODY"]["roles"]:
                templates_list.append(role["vm_template"])
            return {'IMAGE': [], 'VMTEMPLATE': templates_list, 'SERVICETEMPLATE': found_appliance["ID"]}
        else:
            msg("error", "Invalid appliance type. Valid appliance types are 'VM' and 'SERVICE'.")
    cmd = "onemarketapp export " + str(ID) + " " + str(NAME) + " -d "  + str(ds_ID)
    res = run_command(cmd)
    if res["rc"] != 0:
        msg("error", "Could not run '" + cmd + "'Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    result_dict = parse_output(res["stdout"])
    for image_id in result_dict["IMAGE"]:
        wait_for_image(image_id)
    return result_dict


# Searches for appliances in the OpenNebula templates. Returns the first matching appliance.
# name => appliance name to search for
# appliance_type => defines whether it should search for VM templates or for service template. Valid options are "VM" and "SERVICE"
def appliance_search(name, appliance_type):
    if appliance_type == "VM":
        res = run_command("onetemplate list -j")
        if res["rc"] != 0:
            msg("error", "Could not run 'onetemplate list -j'. Error:")
            msg("error", res["stderr"])
            sys.exit(255)
        apps_dict = json.loads(res["stdout"])
        apps_list = apps_dict["VMTEMPLATE_POOL"]["VMTEMPLATE"]
        for app in apps_list:
            if app["NAME"] == name:
                return app
        return False
    elif appliance_type == "SERVICE":
        res = run_command("oneflow-template list -j")
        if res["rc"] != 0:
            msg("error", "Could not run 'oneflow-template list -j'. Error:")
            msg("error", res["stderr"])
            sys.exit(255)
        apps_dict = json.loads(res["stdout"])

        # No service templates present
        if not "DOCUMENT" in apps_dict["DOCUMENT_POOL"]:
            return False
        apps_list = apps_dict["DOCUMENT_POOL"]["DOCUMENT"]
        for app in apps_list:
            if app["NAME"] == name:
                return app
        return False
    else:
        msg("error", "Invalid appliance type. Valid appliance types are 'VM' and 'SERVICE'.")
        sys.exit(255)

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


def wait_for_service_running(ID):
    msg("info", "Waiting for service ID:" + str(ID) + " to be in running state... This process can take several minutes.")
    while True:
        cmd = "oneflow show -j " + str(ID)
        res = run_command(cmd)
        if res["rc"] != 0:
            msg("error", "Could not run '" + cmd + "'Error:")
            msg("error", res["stderr"])
            sys.exit(255)
        svc_dict = json.loads(res["stdout"])
        svc = svc_dict["DOCUMENT"]
        # Check if the service is in running state (2)
        if str(svc["TEMPLATE"]["BODY"]["state"]) == "2":
            break
        sleep(1)
    msg("info", "Service with ID " + str(ID) + " is running.")




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

# Receives a list of elements and lets the user chose one/several. 
# Parameters:
#   elements => list of dicts (objects) from where the user will choose
#   action => action that will be performed with the selected elements. Visual only
#   display_field => attribute of each object that will be shown to the user for selection
#   select_single => determines wether the user can select more than one element (select_single=False)

def select_elements(elements, elem_type="elements", action="download", display_field="NAME", select_single=False):
    choices = [element[display_field] for element in elements]
    if select_single == False:
        selected_display_names = questionary.checkbox(
            "Please select the " + elem_type + " you want to " + action + ":",
            choices=choices
        ).ask()
        # Map the selected display names back to the original elements
        result = [element for element in elements if element[display_field] in selected_display_names]
    else:
        selected_display_name = questionary.select(
            "Please select the " + elem_type + " you want to " + action + ":",
            choices=choices
        ).ask()
        # Map the selected display name back to the original element
        result = [element for element in elements if element[display_field] == selected_display_name][0]
    return result

def instantiate_sandbox_service(ID):
    res = run_command("oneflow-template list -j")
    if res["rc"] != 0:
        msg("error", "Could not run 'oneflow-template list -j'. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    svc_dict = json.loads(res["stdout"])

    # Edge case: no service templates present
    if not "DOCUMENT" in svc_dict["DOCUMENT_POOL"]:
        return False
    svc_list = svc_dict["DOCUMENT_POOL"]["DOCUMENT"]

    # Checking if the Sandbox service exists
    svc_exists = False
    for svc in svc_list:
        if svc["ID"] == str(ID):
            svc_name = svc["NAME"]
            svc_exists = True
            break

    if svc_exists == False:
        msg("error", "Unable not download service with ID " + str(ID) + ". Service not found.")
        sys.exit(255)
    msg("info", "Instantiating service " + svc_name + "...")

    msg("info", "PLEASE, INTRODUCE THE REQUIRED PARAMETERS FOR THE 6G-SANDBOX CORE APPLIANCES")
    params = get_sandbox_svc_parameters()
    # Write parameters to a JSON service template file
    with open('svc_params.json', 'w') as file:
        json.dump(params, file, indent=2)


    # Check if jenkins user exists
    jenkins_user = params["custom_attrs_values"]["oneapp_jenkins_opennebula_username"]
    jenkins_user_password = params["custom_attrs_values"]["oneapp_jenkins_opennebula_password"]

    command = "oneuser list -j"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "Could not run '" + command + "'. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    user_dict = json.loads(res["stdout"])
    user_list = user_dict["USER_POOL"]["USER"]
    found = False
    for user in user_list:
        if user["NAME"] == jenkins_user:
            jenkins_user_id = user["ID"]
            found = True

    if found:
        msg("info", "Jenkins OpenNebula user already present as " + jenkins_user +". Please, make sure that the password introduced is the one configurd for the already-present user.")
    else:
        #Create jenkins user
        msg("info", "Jenkins OpenNebula user not found, creating Jenkins user...")
        command = "oneuser create " + jenkins_user + " " + jenkins_user_password
        res = run_command(command)
        if res["rc"] != 0:
            msg("error", "Could not run '" + command + "'. Error:")
            msg("error", res["stderr"])
            sys.exit(255)
        jenkins_user_id = res["stdout"].split(" ")[1]
        msg("info", jenkins_user + " user created successfully with ID " + jenkins_user_id)

    #Instantiate service
    command = "oneflow-template instantiate " + str(ID) + " < svc_params.json"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "Could not run '" + command + "'. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    svc_ID = res["stdout"].split(" ")[1]
    wait_for_service_running(svc_ID)
    run_command("rm svc_params.json")


    # Parse Jenkins VM ID from service
    command = "oneflow show " + str(svc_ID) + " -j"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "Could not run '" + command + "'. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    svc_dict = json.loads(res["stdout"])
    svc_roles = svc_dict["DOCUMENT"]["TEMPLATE"]["BODY"]["roles"]
    for role in svc_roles:
        if role["name"] == "jenkins":
            for node in role["nodes"]:
                jenkins_id = node["vm_info"]["VM"]["ID"]
    
    if not jenkins_id:
        msg("error", "Jenkins VM not found, unable to parse VM ID.")
        sys.exit(255)
    
    # Wait for Jenkins to report SSH key
    msg("info", "Waiting for Jenkins VM to report SSH key.")
    while True:
        command = "onevm show " + jenkins_id + " -j"
        res = run_command(command)
        if res["rc"] != 0:
            msg("error", "Could not run '" + command + "'. Error:")
            msg("error", res["stderr"])
            sys.exit(255)
        jenkins_dict = json.loads(res["stdout"])
        try:
            jenkins_ssh_key = jenkins_dict["VM"]["USER_TEMPLATE"]["SSH_KEY"]
            break
        except:
            pass
    msg ("info", "Jenkins reported public SSH key, adding key to OpenNebula Jenkins user...")
    command = "echo \'SSH_PUBLIC_KEY=\"" + jenkins_ssh_key + "\"\' | oneuser update " + jenkins_user_id
    print("Command: " + command)
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "Could not run '" + command + "'. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    msg("info", "Jenkins SSH key added successfully to user " + jenkins_user)




def get_sandbox_svc_parameters():
    attrs = {
    "custom_attrs" : {
    "oneapp_minio_hostname": "O|text|MinIO hostname for TLS certificate||localhost,minio-*.example.net",
    "oneapp_minio_opts": "O|text|Additional commandline options for MinIO server||--console-address :9001",
    "oneapp_minio_root_user": "O|text|MinIO root user for MinIO server. At least 3 characters||myminioadmin",
    "oneapp_minio_root_password": "M|password|MinIO root user password for MinIO server. At least 8 characters",
    "oneapp_minio_tls_cert": "O|text64|MinIO TLS certificate (.crt)||",
    "oneapp_minio_tls_key": "O|text64|MinIO TLS key (.key)||",
    "oneapp_jenkins_username": "O|text|The username for the Jenkins admin user||admin",
    "oneapp_jenkins_password": "M|password|The password for the Jenkins admin user",
    "oneapp_jenkins_ansible_vault": "M|password|Passphrase to encrypt and decrypt the 6G-Sandbox-Sites repository files for your site using Ansible Vault",
    "oneapp_jenkins_opennebula_endpoint": "M|text|The URL of your OpenNebula XML-RPC Endpoint API (for example, 'http://example.com:2633/RPC2')||",
    "oneapp_jenkins_opennebula_flow_endpoint": "M|text|The URL of your OneFlow HTTP Endpoint API (for example, 'http://example.com:2474')||",
    "oneapp_jenkins_opennebula_username": "M|text|The OpenNebula username used by Jenkins to deploy each component||",
    "oneapp_jenkins_opennebula_password": "M|password|The password for the OpenNebula user used by Jenkins to deploy each component",
    "oneapp_jenkins_opennebula_insecure": "O|boolean|Allow insecure connexions into the OpenNebula XML-RPC Endpoint API (skip TLS verification)||YES"
        }
    }

    custom_attrs = attrs["custom_attrs"]

    responses = {}

    for key, value in custom_attrs.items():
        parts = value.split('|')
        required = parts[0] == 'M'
        field_type = parts[1]
        description = parts[2]

        # Handling default value extraction
        if len(parts) > 3:
            default_value = value.split('||')[1] if '||' in value else parts[3]
        else:
            default_value = ''

        prompt_text = f"{description} (default: {default_value})"
        
        custom_style = questionary.Style([
            ('question', '#cda02b')
        ])
        if field_type == 'text' or field_type == 'boolean':
            response = questionary.text(prompt_text, default=default_value, style=custom_style).ask()
        elif field_type == 'password':
            response = questionary.password(prompt_text, style=custom_style).ask()
        elif field_type == 'text64':
            # Assuming text64 is a text field with default value
            response = questionary.text(prompt_text, default=default_value, style=custom_style).ask()
        else:
            raise ValueError(f"Unsupported field type: {field_type}")

        responses[key] = response

    res = run_command("onevnet list -j")
    if res["rc"] != 0:
        msg("error", "Could not run 'onevnet list -j'. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    vnet_dict = json.loads(res["stdout"])["VNET_POOL"]["VNET"]
    selected_vnet = select_elements(vnet_dict, elem_type="network", action="instantiate the 6G-SANDBOX CORE service", display_field="NAME", select_single=True)
    selected_vnet_id = selected_vnet["ID"]

    output_dict = {
        "custom_attrs_values": responses,  
        "networks_values": [
            {
                "Public": {
                    "id": str(selected_vnet_id)
                }
            }
        ]
    }
    return output_dict

def create_jenkins_user():
    res = run_command("whoami")
    if res["rc"] != 0:
        msg("error", "Could not run woami command for user checking")
        sys.exit(255)

def extract_tnlcm_id(toolkit_service_id):
    command = "oneflow show " + str(toolkit_service_id) + " -j"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "Could not run '" + command + "'. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    svc_dict = json.loads(res["stdout"])
    svc_roles = svc_dict["DOCUMENT"]["TEMPLATE"]["BODY"]["roles"]
    for role in svc_roles:
        if role["name"] == "tnlcm":
            for node in role["nodes"]:
                tnlcm_id = node["vm_info"]["VM"]["ID"]
    
    if not tnlcm_id:
        msg("error", "TNLCM VM not found, unable to parse VM ID.")
        sys.exit(255)
    
    return tnlcm_id
    
def extract_tnclm_ip(tnlcm_id):
    command = "onevm show " + str(tnlcm_id) + " -j"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", "Could not run '" + command + "'. Error:")
        msg("error", res["stderr"])
        sys.exit(255)
    vm_dict = json.loads(res["stdout"])
    vm_ip = vm_dict["VM"]["TEMPLATE"]["NIC"][0]["IP"]

    if not vm_ip:
        msg("error", "TNLCM IP not found.")
        sys.exit(255)
    
    return vm_ip

def extract_tnlcm_admin_user(tnlcm_id):
    command = "onevm show " + str(tnlcm_id) + " -j"
    res = run_command(command)
    vm_dict = json.loads(res["stdout"])
    vm_tnlcm_admin_username = vm_dict["VM"]["USER_TEMPLATE"]["ONEAPP_TNLCM_ADMIN_USER"]
    vm_tnlcm_admin_password = vm_dict["VM"]["USER_TEMPLATE"]["ONEAPP_TNLCM_ADMIN_PASSWORD"]

    if not vm_tnlcm_admin_username or not vm_tnlcm_admin_password:
        msg("error", "TNLCM admin user not found.")
        sys.exit(255)
    
    return vm_tnlcm_admin_username, vm_tnlcm_admin_password

def login_tnlcm(tnlcm_url, vm_tnlcm_admin_username, vm_tnlcm_admin_password):
    credentials = f"{vm_tnlcm_admin_username}:{vm_tnlcm_admin_password}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    headers = {
        "accept": "application/json",
        "authorization": f"Basic {encoded_credentials}"
    }
    res = requests.post(f"{tnlcm_url}/tnlcm/user/login", headers=headers)
    if res.status_code != 201:
        msg("error", res["message"])
        sys.exit(255)
    data = res.json()
    return data["access_token"]

def extract_trial_network(tnlcm_repo):
    download_repo(tnlcm_repo)
    tnlcm_path = f"repo/{tnlcm_repo.split('/')[1]}-main"

    file_path = os.path.join(tnlcm_path, "tnlcm", "tn_template_lib", "08_descriptor.yaml")

    if not os.path.exists(file_path):
        msg("error", f"File not found in {file_path} path")
        sys.exit(255)
    destination_path = "08_descriptor.yaml"
    shutil.copy(file_path, destination_path)
    remove_repo()
    return destination_path

def select_platform(tnlcm_url):
    url = f"{tnlcm_url}/tnlcm/6G-Sandbox-Sites/branches/"
    res = requests.get(url)
    if res.status_code != 200:
        msg("error", res["message"])
        sys.exit(255)
    platforms = res.json()
    prompt_text = "Please choose a platform:"
    default_value = platforms[0]
    chosen_platform = questionary.select(
        prompt_text,
        choices=platforms,
        default=default_value
    ).ask()

    return chosen_platform

def create_trial_network(tnlcm_url, site, access_token, trial_network):
    url = f"{tnlcm_url}/tnlcm/trial-network"
    params = {
        "tn_id": "test",
        "deployment_site": site,
        "github_6g_library_reference_type": "branch",
        "github_6g_library_reference_value": "main",
        "github_6g_sandbox_sites_reference_type": "branch",
        "github_6g_sandbox_sites_reference_value": site
    }
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    try:
        with open(trial_network, "rb") as file:
            files = {
                "descriptor": file
            }
            res = requests.post(url, headers=headers, params=params, files=files)
        if res.status_code != 201:
            msg("error", res["message"])
            sys.exit(255)
        data = res.json()
        return data["tn_id"]
    except FileNotFoundError:
        msg("error", f"File {trial_network} not found")
        sys.exit(255)

def deploy_trial_network(tnlcm_url, tn_id, access_token):
    url = f"{tnlcm_url}/tnlcm/trial-network"
    params = {
        "tn_id": tn_id
    }
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    res = requests.put(url, headers=headers, params=params)
    if res.status_code != 200:
        msg("error", res["message"])
        sys.exit(255)