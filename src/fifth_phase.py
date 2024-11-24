import os
import requests

from src.utils.cli import run_command
from src.utils.git import git_clone
from src.utils.file import loads_json, get_env_var
from src.utils.logs import msg
from src.utils.parser import encode_base64
from src.utils.temp import load_temp_file, save_temp_directory, temp_path

def _extract_tnlcm_appliance_id(toolkit_service_id: str) -> str:
    """
    Extract TNLCM appliance ID from the toolkit service ID
    
    :param toolkit_service_id: the toolkit service ID, ``str``
    :return: the TNLCM appliance ID, ``str``
    """
    command = f"oneflow show {toolkit_service_id} -j"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", f"Could not run '{command}' command")
    svc_dict = loads_json(data=res["stdout"])
    svc_roles = svc_dict["DOCUMENT"]["TEMPLATE"]["BODY"]["roles"]
    tnlcm_appliance_id = None
    for role in svc_roles:
        if role["name"] == "tnlcm":
            pass
            # FIX: This is not the correct way to extract the VM ID
            # for node in role["nodes"]:
            #     tnlcm_appliance_id = node["vm_info"]["VM"]["ID"]
            #     break
    if tnlcm_appliance_id is not None:
        msg("error", "TNLCM VM not found, unable to parse VM ID")
    return tnlcm_appliance_id

def _extract_tnclm_ip(tnlcm_id: str) -> str:
    """
    Extract TNLCM IP from the TNLCM appliance ID
    
    :param tnlcm_id: the TNLCM appliance ID, ``str``
    :return: the TNLCM IP, ``str``
    """
    command = f"onevm show {tnlcm_id} -j"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", f"Could not run '{command}' command")
    vm_dict = loads_json(res["stdout"])
    vm_ip = vm_dict["VM"]["TEMPLATE"]["NIC"][0]["IP"]
    if not vm_ip:
        msg("error", "TNLCM IP not found")
    return vm_ip

def _extract_tnlcm_admin_user(tnlcm_appliance_id: str) -> tuple[str, str]:
    """
    Extract TNLCM admin user from the TNLCM appliance ID
    
    :param tnlcm_appliance_id: the TNLCM appliance ID, ``str``
    :return: the TNLCM admin user and password, ``tuple[str, str]``
    """
    command = f"onevm show {tnlcm_appliance_id} -j"
    res = run_command(command)
    vm_dict = loads_json(res["stdout"])
    tnlcm_admin_username = vm_dict["VM"]["USER_TEMPLATE"]["ONEAPP_TNLCM_ADMIN_USER"]
    tnlcm_admin_password = vm_dict["VM"]["USER_TEMPLATE"]["ONEAPP_TNLCM_ADMIN_PASSWORD"]
    if not tnlcm_admin_username or not tnlcm_admin_password:
        msg("error", "TNLCM admin user not found")
    return tnlcm_admin_username, tnlcm_admin_password

def _login_tnlcm(tnlcm_url: str, tnlcm_admin_username: str, tnlcm_admin_password: str) -> str:
    """
    Login to TNLCM and get the access token
    
    :param tnlcm_url: the TNLCM URL, ``str``
    :param tnlcm_admin_username: the TNLCM admin username, ``str``
    :param tnlcm_admin_password: the TNLCM admin password, ``str``
    :return: the access token, ``str``
    """
    credentials = f"{tnlcm_admin_username}:{tnlcm_admin_password}"
    encoded_credentials = encode_base64(credentials)
    headers = {
        "accept": "application/json",
        "authorization": f"Basic {encoded_credentials}"
    }
    res = requests.post(f"{tnlcm_url}/tnlcm/user/login", headers=headers)
    if res.status_code != 201:
        msg("error", res["message"])
    data = res.json()
    return data["access_token"]

def _extract_trial_network(github_tnlcm_https: str) -> str:
    """
    Extract the trial network from the TNLCM GitHub repository
    
    :param github_tnlcm_https: the TNLCM GitHub HTTPS URL, ``str``
    :return: the trial network path, ``str``
    """
    git_clone(github_tnlcm_https, save_temp_directory("tnlcm"))
    return temp_path(os.path.join("tnlcm", "tn_template_lib", "ueransim_split.yaml"))

def _create_trial_network(tnlcm_url: str, site: str, access_token: str, trial_network_path: str) -> str:
    """
    Create the trial network in TNLCM
    
    :param tnlcm_url: the TNLCM URL, ``str``
    :param site: the site where the deployment is being executed, ``str``
    :param access_token: the access token, ``str``
    :param trial_network_path: the trial network path, ``str``
    :return: the trial network ID, ``str``
    """
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
        "authorization": f"Bearer {access_token}"
    }
    files = load_temp_file(trial_network_path, mode="rb", encoding=None)
    res = requests.post(f"{tnlcm_url}/trial_networks", headers=headers, data=params, files=files)
    if res.status_code != 201:
        msg("error", res["message"])
    data = res.json()
    return data["tn_id"]

def _deploy_trial_network(tnlcm_url, tn_id, access_token):
    url = f"{tnlcm_url}/tnlcm/trial-network"
    params = {
        "jenkins_deploy_pipeline": "TN_DEPLOY",
        "tn_id": tn_id
    }
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    res = requests.put(url, headers=headers, params=params)
    if res.status_code != 200:
        msg("error", res["message"])

def _destroy_trial_network(tnlcm_url, tn_id, access_token):
    url = f"{tnlcm_url}/tnlcm/trial-network"
    params = {
        "jenkins_destroy_pipeline": "TN_DESTROY",
        "tn_id": tn_id
    }
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    res = requests.delete(url, headers=headers, params=params)
    if res.status_code != 200:
        msg("error", res["message"])

def fifth_phase(site: str, toolkit_service_id: str) -> None:
    """
    The fifth phase of the 6G-SANDBOX deployment
    
    :param site: the site where the deployment is being executed, ``str``
    :param toolkit_service_id: the toolkit service ID, ``str``
    """
    msg("info", "[TNLCM RUN TRIAL NETWORK]")
    tnlcm_appliance_id = _extract_tnlcm_appliance_id(toolkit_service_id)
    msg("info", f"TNLCM appliance ID: {tnlcm_appliance_id}")
    tnlcm_ip = _extract_tnclm_ip(tnlcm_appliance_id)
    msg("info", f"TNLCM IP: {tnlcm_ip}")
    tnlcm_port = get_env_var("TNLCM_PORT")
    tnlcm_url = f"http://{tnlcm_ip}:{tnlcm_port}"
    tnlcm_admin_username, tnlcm_admin_password = _extract_tnlcm_admin_user(tnlcm_appliance_id)
    access_token = _login_tnlcm(tnlcm_url, tnlcm_admin_username, tnlcm_admin_password)
    github_tnlcm_https = get_env_var("GITHUB_TNLCM_HTTPS")
    trial_network_path = _extract_trial_network(github_tnlcm_https)
    tn_id = _create_trial_network(tnlcm_url, site, access_token, trial_network_path)
    msg("info", f"Trial network created with ID {tn_id}")
    _deploy_trial_network(tnlcm_url, tn_id, access_token)
    msg("info", "Trial network deployed")
    _destroy_trial_network(tnlcm_url, tn_id, access_token)
    msg("info", "Trial network destroyed")