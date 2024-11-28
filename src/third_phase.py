from time import sleep

from src.utils.file import get_env_var
from src.utils.logs import msg
from src.utils.interactive import ask_select, ask_checkbox
from src.utils.one import get_onemarket, get_template, get_appliance_id, get_onemarket_id, get_oneflow_template, get_type_appliance, rename_image, get_onedatastore_id, add_marketplace, get_marketplace_monitoring_interval, update_marketplace_monitoring_interval, restart_one, check_one_health, get_appliances_marketplace, get_image, get_onedatastores, export_appliance, get_state_image, chown_image, chown_template

def _add_appliances_from_marketplace(sixg_sandbox_group_id: int, jenkins_user_id: int, marketplace_id: int, appliances: list) -> None:
    """
    Add appliances from a marketplace to the local OpenNebula

    :param sixg_sandbox_group: the ID of the 6G-SANDBOX group, ``int``
    :param jenkins_user: the ID of the Jenkins user, ``int``
    :param marketplace_id: the ID of the marketplace, ``int``
    :param appliances: the list of appliances to add, ``list``
    """
    for appliance_name in appliances:
        appliance_id = get_appliance_id(appliance_name=appliance_name, marketplace_id=marketplace_id)
        appliance_type = get_type_appliance(appliance_name=appliance_name, marketplace_id=marketplace_id)
        if appliance_type == "IMAGE":
            if get_image(appliance_name) is None:
                msg("info", f"Appliance {appliance_name} not present, exporting...")
                onedatastores = get_onedatastores()
                datastore = ask_select(prompt="Select the datastore where you want to store the image", choices=onedatastores)
                datastore_id = get_onedatastore_id(datastore)
                image_id, template_id, _ = export_appliance(appliance_id=appliance_id, appliance_name=appliance_name, datastore_id=datastore_id)
                sleep(10)
                rename_image(image_id=image_id[0], new_name=appliance_name)
                while get_state_image(appliance_name) != "1":
                    msg("info", "Please, wait 10s for the image to be ready...")
                    sleep(10)
                chown_image(image_id=image_id[0], user_id=jenkins_user_id, group_id=sixg_sandbox_group_id)
                chown_template(template_id=template_id[0], user_id=jenkins_user_id, group_id=sixg_sandbox_group_id)
        elif appliance_type == "VM":
            if get_template(appliance_name) is None:
                msg("info", f"Appliance {appliance_name} not present, exporting...")
                onedatastores = get_onedatastores()
                datastore = ask_select(prompt="Select the datastore where you want to store the image", choices=onedatastores)
                datastore_id = get_onedatastore_id(datastore)
                image_ids, template_id, _ = export_appliance(appliance_id=appliance_id, appliance_name=appliance_name, datastore_id=datastore_id)
                sleep(10)
                print(image_ids)
                print(template_id)
                for i, image_id in enumerate(image_ids):
                    rename_image(image_id=image_id, new_name=f"{appliance_name}-{i}")
                for i, image_id in enumerate(image_ids):
                    while get_state_image(f"{appliance_name}-{i}") != "1":
                        msg("info", "Please, wait 10s for the image to be ready...")
                        sleep(10)
                for i, image_id in enumerate(image_ids):
                    chown_image(image_id=image_id, user_id=jenkins_user_id, group_id=sixg_sandbox_group_id)
                chown_template(template_id=template_id[0], user_id=jenkins_user_id, group_id=sixg_sandbox_group_id)
        else:
            if get_oneflow_template(appliance_name) is None:
                msg("info", f"Appliance {appliance_name} not present, exporting...")
                onedatastores = get_onedatastores()
                datastore = ask_select(prompt="Select the datastore where you want to store the image", choices=onedatastores)
                datastore_id = get_onedatastore_id(datastore)
                appliance_id = export_appliance(appliance_id=appliance_id, appliance_name=appliance_name, datastore_id=datastore_id)
                sleep(10)
                # TODO

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
        _add_appliances_from_marketplace(sixg_sandbox_group_id=sixg_sandbox_group_id, jenkins_user_id=jenkins_user_id, marketplace_id=opennebula_public_marketplace_id, appliances=opennebula_public_appliances_selected)
    sixg_sandbox_marketplace_appliances = get_appliances_marketplace(marketplace_id=sixg_sandbox_marketplace_id)
    sixg_sandbox_appliances_selected = ask_checkbox("Select the appliances you want to import from the 6G-SANDBOX Marketplace", sixg_sandbox_marketplace_appliances)
    if sixg_sandbox_appliances_selected:
        _add_appliances_from_marketplace(sixg_sandbox_group_id=sixg_sandbox_group_id, jenkins_user_id=jenkins_user_id, marketplace_id=sixg_sandbox_marketplace_id, appliances=sixg_sandbox_appliances_selected)
    # Añadir los apliances de los componentes que se han añadido al repositorio de sites