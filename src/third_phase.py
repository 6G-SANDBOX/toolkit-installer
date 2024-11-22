from time import sleep

from src.utils.dotenv import get_env_var
from src.utils.logs import msg
from src.utils.interactive import ask_select, ask_checkbox
from src.utils.one import get_onemarket, get_user, get_group, add_marketplace, get_marketplace_monitoring_interval, update_marketplace_monitoring_interval, restart_one, check_one_health, get_appliances_marketplace, get_local_image, get_onedatastores, get_onedatastore, export_image, get_state_image, chown_image, chown_template

def _add_appliances_from_marketplace(markeplace_id: int, appliances: list, sixg_sandbox_group: str, jenkins_user: str) -> None:
    """
    Add appliances from a marketplace to the local OpenNebula

    :param markeplace_id: the ID of the marketplace, ``int``
    :param appliances: the list of appliances to add, ``list``
    :param sixg_sandbox_group: the name of the 6G-SANDBOX group, ``str``
    :param jenkins_user: the name of the Jenkins user, ``str``
    """
    for appliance_name in appliances:
        if get_local_image(appliance_name) is not None:
            msg("info", f"Appliance {appliance_name} not present, exporting...")
            onedatastores = get_onedatastores()
            datastore = ask_select("Select the datastore where you want to store the image", onedatastores)
            datastore_id = get_onedatastore(datastore)["DATASTORE"]["ID"]
            image_id, template_id = export_image(marketplace_id=markeplace_id, appliance_name=appliance_name, datastore_id=datastore_id)
            while get_state_image(appliance_name) != "1":
                msg("info", "Please, wait 10s for the image to be ready...")
                sleep(10)
            jenkins_user_id = get_user(username=jenkins_user)["USER"]["ID"]
            sixg_sandbox_group_id = get_group(group_name=sixg_sandbox_group)["GROUP"]["ID"]
            chown_image(image_id=image_id, user_id=jenkins_user_id, group_id=sixg_sandbox_group_id)
            chown_template(template_id=template_id, user_id=jenkins_user_id, group_id=sixg_sandbox_group_id)

def third_phase(sixg_sandbox_group: str, jenkins_user: str) -> None:
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
            sleep(marketplace_interval)
            check_one_health()
            update_marketplace_monitoring_interval(interval=old_interval)
            restart_one()
            check_one_health()
    else:
        msg("info", f"Marketplace {sixg_sandbox_marketplace_name} already present")
        sixg_sandbox_marketplace_id = sixg_sandbox_marketplace["MARKETPLACE"]["ID"]

    opennebula_public_marketplace = get_env_var("OPENNEBULA_PUBLIC_MARKETPLACE")
    opennebula_public_marketplace_id = get_onemarket(marketplace_name=opennebula_public_marketplace)["MARKETPLACE"]["ID"]
    opennebula_public_marketplace_appliances = get_appliances_marketplace(marketplace_id=opennebula_public_marketplace_id)
    opennebula_public_appliances_selected = ask_checkbox("Select the appliances you want to import from the OpenNebula Public Marketplace", opennebula_public_marketplace_appliances)
    _add_appliances_from_marketplace(marketplace_id=opennebula_public_marketplace_id, appliances=opennebula_public_appliances_selected, sixg_sandbox_group=sixg_sandbox_group, jenkins_user=jenkins_user)
    sixg_sandbox_marketplace_appliances = get_appliances_marketplace(marketplace_id=sixg_sandbox_marketplace_id)
    sixg_sandbox_appliances_selected = ask_checkbox("Select the appliances you want to import from the 6G-SANDBOX Marketplace", sixg_sandbox_marketplace_appliances)
    _add_appliances_from_marketplace(markeplace_id=sixg_sandbox_marketplace_id, appliances=sixg_sandbox_appliances_selected, sixg_sandbox_group=sixg_sandbox_group, jenkins_user=jenkins_user)
    