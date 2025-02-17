import os
import requests

from phases.utils.file import load_yaml, get_env_var, save_json, save_file
from phases.utils.git import git_clone, git_switch
from phases.utils.interactive import ask_text, ask_checkbox
from phases.utils.logs import msg
from phases.utils.one import get_appliances_marketplace, add_appliances_from_marketplace, get_oneflow_template, update_oneflow_template, update_template, get_template
from phases.utils.temp import save_temp_directory, temp_path

def _extract_appliance_name(appliance_url: str) -> str:
    """
    Extract the appliance name from the URL
    
    :param appliance_url: the URL of the appliance, ``str``
    :return: the name of the appliance, ``str``
    """
    headers = {
        "Accept": "application/json"
    }
    res = requests.get(appliance_url, headers=headers)
    if res.status_code != 200:
        msg("error", f"Failed to get the appliance URL: {appliance_url}")
    appliance_name = res.json()["name"]
    return appliance_name

def third_phase(sixg_sandbox_group: str, jenkins_user: str) -> None:
    msg("info", "THIRD PHASE")
    github_sites_https = get_env_var("GITHUB_SITES_HTTPS")
    sites_directory = get_env_var("SITES_DIRECTORY")
    github_library_https = get_env_var("GITHUB_LIBRARY_HTTPS")
    github_library_tag = get_env_var("GITHUB_LIBRARY_TAG")
    library_directory = get_env_var("LIBRARY_DIRECTORY")
    toolkit_service = get_env_var("OPENNEBULA_TOOLKIT_SERVICE")
    sixg_sandbox_marketplace_name = get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_NAME")
    opennebula_public_marketplace_name = get_env_var("OPENNEBULA_PUBLIC_MARKETPLACE_NAME")
    opennebula_oneke_service = get_env_var("OPENNEBULA_ONEKE_SERVICE")
    sites_path = save_temp_directory(sites_directory)
    github_sites_token = ask_text(prompt="Enter the token for the GitHub sites repository. Please follow the instructions indicated in the following link https://6g-sandbox.github.io/docs/toolkit-installer/run-toolkit-installer#create-site-token", default="", validate=True)
    github_sites_https = github_sites_https.replace("https://", f"https://{github_sites_token}@")
    git_clone(github_sites_https, sites_path)
    library_path = save_temp_directory(library_directory)
    git_clone(github_library_https, library_path)
    git_switch(library_path, tag=github_library_tag)
    dummy_site_core_path = temp_path(os.path.join(sites_directory, ".dummy_site", "core.yaml"))
    data = load_yaml(file_path=dummy_site_core_path, mode="rt", encoding="utf-8")
    site_available_components = data["site_available_components"]
    appliances = []
    if site_available_components:
        for component_name in site_available_components.keys():
            public_yaml_path = os.path.join(library_path, component_name, ".tnlcm", "public.yaml")
            if os.path.exists(public_yaml_path):
                public_yaml = load_yaml(file_path=public_yaml_path, mode="rt", encoding="utf-8")
                metadata = public_yaml["metadata"]
                if "appliance" in metadata:
                    appliance_url = metadata["appliance"]
                    appliance_name = _extract_appliance_name(appliance_url=appliance_url)
                    appliances.append(appliance_name)
    add_appliances_from_marketplace(sixg_sandbox_group=sixg_sandbox_group, jenkins_user=jenkins_user, marketplace_name=sixg_sandbox_marketplace_name, appliances=appliances)
    add_appliances_from_marketplace(sixg_sandbox_group=sixg_sandbox_group, jenkins_user=jenkins_user, marketplace_name=opennebula_public_marketplace_name, appliances=appliances)

    oneflow_template_oneke = get_oneflow_template(oneflow_template_name=opennebula_oneke_service)
    if oneflow_template_oneke is None:
        add_appliances_from_marketplace(sixg_sandbox_group=sixg_sandbox_group, jenkins_user=jenkins_user, marketplace_name=opennebula_public_marketplace_name, appliances=[opennebula_oneke_service])
        oneflow_template_oneke = get_oneflow_template(oneflow_template_name=opennebula_oneke_service)
    oneflow_template_oneke_body = oneflow_template_oneke["DOCUMENT"]["TEMPLATE"]["BODY"]
    roles = oneflow_template_oneke_body["roles"]
    storage_vm_template_id = None
    for role in roles:
        if role["name"] == "storage":
            if role["cardinality"] != 3:
                role["cardinality"] = 3
                oneflow_template_oneke_body["roles"] = roles
                oneflow_template_path = temp_path("oneflow_template_oneke.json")
                save_json(data=oneflow_template_oneke_body, file_path=oneflow_template_path)
                update_oneflow_template(oneflow_template_name=opennebula_oneke_service, file_path=oneflow_template_path)
            
            storage_vm_template_id = role["vm_template"]
            storage_vm_template = get_template(template_id=storage_vm_template_id)
            storage_vm_template_name = storage_vm_template["VMTEMPLATE"]["NAME"]
            storage_vm_template_disk = storage_vm_template["VMTEMPLATE"]["TEMPLATE"]["DISK"]
            content = ""
            for i, disk in enumerate(storage_vm_template_disk):
                if i == 1 and ("SIZE" not in disk or disk["SIZE"] != "15360"):
                    disk["SIZE"] = "15360"
                    content += f'DISK=[ IMAGE_ID="{disk["IMAGE_ID"]}", SIZE="{disk["SIZE"]}" ]\n'
                else:
                    content += f'DISK=[ IMAGE_ID="{disk["IMAGE_ID"]}" ]\n'
            storage_vm_template_path = temp_path("oneke_storage_vm_template")
            save_file(data=content, file_path=storage_vm_template_path, mode="w", encoding="utf-8")
            update_template(template_name=storage_vm_template_name, file_path=storage_vm_template_path)
    
    opennebula_public_marketplace_appliances = get_appliances_marketplace(marketplace_name=opennebula_public_marketplace_name)
    if opennebula_oneke_service in opennebula_public_marketplace_appliances:
        opennebula_public_marketplace_appliances.remove(opennebula_oneke_service)
    opennebula_public_appliances_selected = ask_checkbox("Select the appliances you want to import from the OpenNebula Public Marketplace", opennebula_public_marketplace_appliances)
    if opennebula_public_appliances_selected:
        add_appliances_from_marketplace(sixg_sandbox_group=sixg_sandbox_group, jenkins_user=jenkins_user, marketplace_name=opennebula_public_marketplace_name, appliances=opennebula_public_appliances_selected)
    sixg_sandbox_marketplace_appliances = get_appliances_marketplace(marketplace_name=sixg_sandbox_marketplace_name)
    for appliance in appliances:
        if appliance in sixg_sandbox_marketplace_appliances:
            sixg_sandbox_marketplace_appliances.remove(appliance)
    sixg_sandbox_marketplace_appliances.remove(toolkit_service)
    sixg_sandbox_appliances_selected = ask_checkbox("Select the appliances you want to import from the 6G-SANDBOX Marketplace", sixg_sandbox_marketplace_appliances)
    if sixg_sandbox_appliances_selected:
        add_appliances_from_marketplace(sixg_sandbox_group=sixg_sandbox_group, jenkins_user=jenkins_user, marketplace_name=sixg_sandbox_marketplace_name, appliances=sixg_sandbox_appliances_selected)