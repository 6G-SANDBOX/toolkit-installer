from time import sleep

from src.utils.file import get_env_var
from src.utils.logs import msg
from src.utils.interactive import ask_checkbox
from src.utils.one import get_onemarket, get_onemarket_id, add_marketplace, get_marketplace_monitoring_interval, update_marketplace_monitoring_interval, restart_one, check_one_health, get_appliances_marketplace, add_appliances_from_marketplace

def third_phase(sixg_sandbox_group_id: int, jenkins_user_id: int) -> None:
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

    opennebula_public_marketplace = get_env_var("OPENNEBULA_PUBLIC_MARKETPLACE")
    opennebula_public_marketplace_id = get_onemarket_id(marketplace_name=opennebula_public_marketplace)
    
    opennebula_public_marketplace_appliances = get_appliances_marketplace(marketplace_id=opennebula_public_marketplace_id)
    opennebula_public_appliances_selected = ask_checkbox("Select the appliances you want to import from the OpenNebula Public Marketplace", opennebula_public_marketplace_appliances)
    if opennebula_public_appliances_selected:
        add_appliances_from_marketplace(sixg_sandbox_group_id=sixg_sandbox_group_id, jenkins_user_id=jenkins_user_id, marketplace_id=opennebula_public_marketplace_id, appliances=opennebula_public_appliances_selected)
    sixg_sandbox_marketplace_appliances = get_appliances_marketplace(marketplace_id=sixg_sandbox_marketplace_id)
    sixg_sandbox_appliances_selected = ask_checkbox("Select the appliances you want to import from the 6G-SANDBOX Marketplace", sixg_sandbox_marketplace_appliances)
    if sixg_sandbox_appliances_selected:
        add_appliances_from_marketplace(sixg_sandbox_group_id=sixg_sandbox_group_id, jenkins_user_id=jenkins_user_id, marketplace_id=sixg_sandbox_marketplace_id, appliances=sixg_sandbox_appliances_selected)