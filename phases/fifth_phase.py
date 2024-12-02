import os
import requests

from phases.utils.file import get_env_var
from phases.utils.git import git_clone
from phases.utils.logs import msg
from phases.utils.one import get_vm_ip, get_vm
from phases.utils.parser import encode_base64
from phases.utils.temp import load_temp_file, save_temp_directory, temp_path

def _login_tnlcm(tnlcm_url: str, tnlcm_admin_username: str, tnlcm_admin_password: str) -> str:
    """
    Login to TNLCM and get the access token
    
    :param tnlcm_url: the TNLCM URL, ``str``
    :param tnlcm_admin_username: the TNLCM admin username, ``str``
    :param tnlcm_admin_password: the TNLCM admin password, ``str``
    :return: the access token, ``str``
    """
    msg("info", "Logging in to TNLCM")
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
    msg("info", "Logged in to TNLCM")
    return data["access_token"]

def _create_trial_network(tnlcm_url: str, site: str, access_token: str, trial_network_path: str) -> str:
    """
    Create the trial network in TNLCM
    
    :param tnlcm_url: the TNLCM URL, ``str``
    :param site: the site where the deployment is being executed, ``str``
    :param access_token: the access token, ``str``
    :param trial_network_path: the trial network path, ``str``
    :return: the trial network ID, ``str``
    """
    msg("info", "Creating trial network")
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
    tn_id = data["tn_id"]
    msg("info", f"Trial network created with tn_id: {tn_id}")
    return tn_id

def _deploy_trial_network(tnlcm_url, tn_id, access_token):
    msg("info", "Deploying trial network")
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
    msg("info", "Trial network deployed")

def _destroy_trial_network(tnlcm_url, tn_id, access_token):
    msg("info", "Destroying trial network")
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
    msg("info", "Trial network destroyed")

def fifth_phase(site: str, vm_tnlcm_name: str) -> None:
    msg("info", "FIFTH PHASE")
    tnlcm_port = get_env_var("TNLCM_PORT")
    tnlcm_directory = get_env_var("TNLCM_DIRECTORY")
    github_tnlcm_https = get_env_var("GITHUB_TNLCM_HTTPS")
    tnlcm_ip = get_vm_ip(vm_tnlcm_name)
    tnlcm_url = f"http://{tnlcm_ip}:{tnlcm_port}"
    tnlcm_vm = get_vm(vm_name=vm_tnlcm_name)
    tnlcm_admin_username = tnlcm_vm["VM"]["USER_TEMPLATE"]["ONEAPP_TNLCM_ADMIN_USER"]
    tnlcm_admin_password = tnlcm_vm["VM"]["USER_TEMPLATE"]["ONEAPP_TNLCM_ADMIN_PASSWORD"]
    access_token = _login_tnlcm(tnlcm_url, tnlcm_admin_username, tnlcm_admin_password)
    git_clone(github_tnlcm_https, save_temp_directory(tnlcm_directory))
    trial_network_path = temp_path(os.path.join(tnlcm_directory, "tn_template_lib", "ueransim_split.yaml"))
    tn_id = _create_trial_network(tnlcm_url, site, access_token, trial_network_path)
    _deploy_trial_network(tnlcm_url, tn_id, access_token)
    _destroy_trial_network(tnlcm_url, tn_id, access_token)