import os

from phases.utils.file import load_file, load_yaml, get_env_var
from phases.utils.git import git_clone
from phases.utils.interactive import ask_checkbox
from phases.utils.logs import msg
from phases.utils.one import get_appliances_marketplace, add_appliances_from_marketplace
from phases.utils.parser import ansible_decrypt
from phases.utils.temp import save_temp_directory, temp_path

def fourth_phase(sixg_sandbox_group: str, jenkins_user: str, site: str, sites_token: str) -> None:
    msg("info", "FOURTH PHASE")
    sites_directory = get_env_var("SITES_DIRECTORY")
    site_core_path = temp_path(os.path.join(sites_directory, site, "core.yaml"))
    github_library_https = get_env_var("GITHUB_LIBRARY_HTTPS")
    library_directory = get_env_var("LIBRARY_DIRECTORY")
    library_path = save_temp_directory(library_directory)
    git_clone(github_library_https, library_path)
    encrypted_data = load_file(file_path=site_core_path, mode="rb", encoding=None)
    decrypted_data = ansible_decrypt(encrypted_data=encrypted_data, password=sites_token)
    data = load_yaml(file_path=decrypted_data, mode="rt", encoding="utf-8")
    site_available_components = data["site_available_components"]
    appliances = []
    if site_available_components:
        for component_name, _ in site_available_components.items():
            public_yaml_path = os.path.join(library_path, component_name, ".tnlcm", "public.yaml")
            if os.path.exists(public_yaml_path):
                public_yaml = load_yaml(file_path=public_yaml_path, mode="rt", encoding="utf-8")
                metadata = public_yaml["metadata"]
                if "appliance" in metadata:
                    appliance_name = metadata["appliance"]
                    appliances.append(appliance_name)
    sixg_sandbox_marketplace_name = get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_NAME")
    add_appliances_from_marketplace(sixg_sandbox_group=sixg_sandbox_group, jenkins_user=jenkins_user, marketplace_name=sixg_sandbox_marketplace_name, appliances=appliances)

    opennebula_public_marketplace_name = get_env_var("OPENNEBULA_PUBLIC_MARKETPLACE_NAME")    
    opennebula_public_marketplace_appliances = get_appliances_marketplace(marketplace_name=opennebula_public_marketplace_name)
    opennebula_public_appliances_selected = ask_checkbox("Select the appliances you want to import from the OpenNebula Public Marketplace", opennebula_public_marketplace_appliances)
    if opennebula_public_appliances_selected:
        add_appliances_from_marketplace(sixg_sandbox_group=sixg_sandbox_group, jenkins_user=jenkins_user, marketplace_name=opennebula_public_marketplace_name, appliances=opennebula_public_appliances_selected)
    sixg_sandbox_marketplace_appliances = get_appliances_marketplace(marketplace_name=sixg_sandbox_marketplace_name)
    for appliance in appliances:
        if appliance in sixg_sandbox_marketplace_appliances:
            sixg_sandbox_marketplace_appliances.remove(appliance)
    sixg_sandbox_marketplace_appliances.remove(toolkit_service)
    sixg_sandbox_appliances_selected = ask_checkbox("Select the appliances you want to import from the 6G-SANDBOX Marketplace", sixg_sandbox_marketplace_appliances)
    toolkit_service = get_env_var("OPENNEBULA_TOOLKIT_SERVICE")
    if sixg_sandbox_appliances_selected:
        add_appliances_from_marketplace(sixg_sandbox_group=sixg_sandbox_group, jenkins_user=jenkins_user, marketplace_name=sixg_sandbox_marketplace_name, appliances=sixg_sandbox_appliances_selected)