import os

from time import sleep

from src.utils.file import load_file, load_yaml, get_env_var
from src.utils.git import git_clone
from src.utils.interactive import ask_checkbox
from src.utils.logs import msg
from src.utils.one import get_onemarket, get_onemarket_id, add_marketplace, get_marketplace_monitoring_interval, update_marketplace_monitoring_interval, restart_one, check_one_health, get_appliances_marketplace, add_appliances_from_marketplace
from src.utils.parser import ansible_decrypt
from src.utils.temp import save_temp_directory

def third_phase(sixg_sandbox_group_id: int, jenkins_user_id: int, site_core_path: str, token_path: str) -> None:
    msg("info", "THIRD PHASE")
    sixg_sandbox_marketplace_name = get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_NAME")
    sixg_sandbox_marketplace_description = get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_DESCRIPTION")
    sixg_sandbox_marketplace_endpoint = get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_ENDPOINT")
    sixg_sandbox_marketplace = get_onemarket(marketplace_name=sixg_sandbox_marketplace_name)
    if sixg_sandbox_marketplace is None:
        msg("info", f"Marketplace {sixg_sandbox_marketplace_name} not present, adding...")
        sixg_sandbox_marketplace_id = add_marketplace(sixg_sandbox_marketplace_name, sixg_sandbox_marketplace_description, sixg_sandbox_marketplace_endpoint)
        force_fast_marketplace_monitoring = get_env_var("FORCE_FAST_MARKETPLACE_MONITORING")
        if force_fast_marketplace_monitoring == "false":
            msg("info", "Please, wait 600s for the marketplace to be ready...")
            sleep(600)
        else:
            msg("info", "Forcing fast marketplace monitoring...")
            marketplace_interval = int(get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_INTERVAL"))
            old_interval = get_marketplace_monitoring_interval()
            update_marketplace_monitoring_interval(interval=marketplace_interval)
            restart_one()
            sleep(marketplace_interval+5)
            check_one_health()
            update_marketplace_monitoring_interval(interval=old_interval)
            restart_one()
            check_one_health()
    else:
        msg("info", f"Marketplace {sixg_sandbox_marketplace_name} already present")
        sixg_sandbox_marketplace_id = get_onemarket_id(marketplace_name=sixg_sandbox_marketplace_name)

    github_library_https = get_env_var("GITHUB_LIBRARY_HTTPS")
    library_directory = get_env_var("LIBRARY_DIRECTORY")
    library_path = save_temp_directory(library_directory)
    git_clone(github_library_https, library_path)
    encrypted_data = load_file(file_path=site_core_path, mode="rb", encoding=None)
    decrypted_data = ansible_decrypt(encrypted_data=encrypted_data, token_path=token_path)
    data = load_yaml(file_path=decrypted_data, mode="rt", encoding="utf-8")
    site_available_components = data["site_available_components"]
    appliances = []
    if site_available_components:
        msg("info", "Site available components:")
        for component_name, _ in site_available_components.items():
            public_yaml_path = os.path.join(library_path, component_name, ".tnlcm", "public.yaml")
            if os.path.exists(public_yaml_path):
                public_yaml = load_yaml(file_path=public_yaml_path, mode="rt", encoding="utf-8")
                metadata = public_yaml["metadata"]
                if "appliance" in metadata:
                    appliance_name = metadata["appliance"]
                    appliances.append(appliance_name)
    add_appliances_from_marketplace(sixg_sandbox_group_id=sixg_sandbox_group_id, jenkins_user_id=jenkins_user_id, marketplace_id=sixg_sandbox_marketplace_id, appliances=appliances)

    opennebula_public_marketplace = get_env_var("OPENNEBULA_PUBLIC_MARKETPLACE")
    opennebula_public_marketplace_id = get_onemarket_id(marketplace_name=opennebula_public_marketplace)
    
    opennebula_public_marketplace_appliances = get_appliances_marketplace(marketplace_id=opennebula_public_marketplace_id)
    opennebula_public_appliances_selected = ask_checkbox("Select the appliances you want to import from the OpenNebula Public Marketplace", opennebula_public_marketplace_appliances)
    if opennebula_public_appliances_selected:
        add_appliances_from_marketplace(sixg_sandbox_group_id=sixg_sandbox_group_id, jenkins_user_id=jenkins_user_id, marketplace_id=opennebula_public_marketplace_id, appliances=opennebula_public_appliances_selected)
    sixg_sandbox_marketplace_appliances = get_appliances_marketplace(marketplace_id=sixg_sandbox_marketplace_id)
    for appliance in appliances:
        if appliance in sixg_sandbox_marketplace_appliances:
            sixg_sandbox_marketplace_appliances.remove(appliance)
    sixg_sandbox_appliances_selected = ask_checkbox("Select the appliances you want to import from the 6G-SANDBOX Marketplace", sixg_sandbox_marketplace_appliances)
    toolkit_service = get_env_var("OPENNEBULA_TOOLKIT_SERVICE")
    if toolkit_service not in sixg_sandbox_appliances_selected:
        sixg_sandbox_appliances_selected.append(toolkit_service)
    if sixg_sandbox_appliances_selected:
        add_appliances_from_marketplace(sixg_sandbox_group_id=sixg_sandbox_group_id, jenkins_user_id=jenkins_user_id, marketplace_id=sixg_sandbox_marketplace_id, appliances=sixg_sandbox_appliances_selected)