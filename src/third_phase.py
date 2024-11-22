from src.utils.dotenv import get_env_var
from src.utils.interactive import ask_text, ask_checkbox
from src.utils.logs import msg
from src.utils.one import get_onemarket, create_group, create_user, assign_user_group

def _select_appliances(marketplace_name: str) -> None:
    """
    Select the appliances from the marketplace
    
    :param marketplace_name: the name of the marketplace, ``str``
    """
    appliances = get_onemarket()
    appliances_list = []
    for appliance in appliances["MARKETPLACEAPP_POOL"]["MARKETPLACEAPP"]:
        if appliances["MARKETPLACEAPP_POOL"]["MARKETPLACEAPP"]["MARKETPLACE"] == marketplace_name:
            appliances_list.append(appliance["NAME"])
    selected_appliances = ask_checkbox("Select the appliances to deploy:", choices=appliances_list)
    # TODO: esperar a que los appliances estén disponibles
    # wait_for_image
    # TODO: asignar el appliance al usuario de Jenkins y al grupo de 6G-SANDBOX
    # onetemplate chown 
    # pueda usar la vnet default al usuario de Jenkins y al grupo de 6G-SANDBOX

def third_phase() -> None:
    """
    The third phase of the 6G-SANDBOX deployment
    """
    msg("info", "THIRD PHASE")
    default_sixg_sandbox_group = get_env_var("OPENNEBULA_6G_SANDBOX_GROUP")
    sixg_sandbox_group = ask_text("Enter the name for the 6G-SANDBOX group:", default=default_sixg_sandbox_group, validate=True)
    sixg_sandbox_group_id = create_group(sixg_sandbox_group=sixg_sandbox_group)
    default_jenkins_user = get_env_var("OPENNEBULA_JENKINS_USER")
    jenkins_user = ask_text("Enter the username for the Jenkins user:", default=default_jenkins_user, validate=True)
    jenkins_password = ask_text("Enter the password for the Jenkins user:", default="", validate=True)
    jenkins_user_id = create_user(username=jenkins_user, password=jenkins_password)
    assign_user_group(user_id=jenkins_user_id, group_id=sixg_sandbox_group_id)
    # opennebula_marketplace = get_env_var("OPENNEBULA_MARKETPLACE")
    # sixg_sandbox_marketplace = get_env_var("OPENNEBULA_6G_SANDBOX_MARKETPLACE_NAME")
    # _select_appliances(opennebula_marketplace)
    # _select_appliances(sixg_sandbox_marketplace)