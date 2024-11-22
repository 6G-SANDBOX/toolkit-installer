from src.utils.dotenv import get_env_var
from src.utils.interactive import ask_text, ask_checkbox, ask_password
from src.utils.logs import msg
from src.utils.one import get_onemarkets, get_group, create_group, get_user, create_user, assign_user_group

def _select_appliances(marketplace_name: str) -> None:
    """
    Select the appliances from the marketplace
    
    :param marketplace_name: the name of the marketplace, ``str``
    """
    appliances = get_onemarkets()
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
    default_sandbox_group = get_env_var("OPENNEBULA_SANDBOX_GROUP")
    sixg_sandbox_group = ask_text("Enter the name for the 6G-SANDBOX group:", default=default_sandbox_group, validate=True)
    while True:
        sixg_sandbox_group_data = get_group(group_name=sixg_sandbox_group)
        if sixg_sandbox_group_data:
            sixg_sandbox_group = ask_text("Group already exists. Enter new name for the 6G-SANDBOX group:", default=default_sandbox_group, validate=True)
        else:
            break
    sixg_sandbox_group_id = create_group(group_name=sixg_sandbox_group)
    default_jenkins_user = get_env_var("OPENNEBULA_JENKINS_USER")
    jenkins_user = ask_text("Enter the username for the Jenkins user:", default=default_jenkins_user, validate=True)
    while True:
        jenkins_user_data = get_user(username=jenkins_user)
        if jenkins_user_data:
            jenkins_user = ask_text("User already exists. Enter new username for the Jenkins user:", default=default_jenkins_user, validate=True)
        else:
            break
    jenkins_password = ask_password("Enter the password for the Jenkins user:", default="", validate=True)
    jenkins_user_id = create_user(username=jenkins_user, password=jenkins_password)
    assign_user_group(user_id=jenkins_user_id, group_id=sixg_sandbox_group_id)
    # opennebula_marketplace = get_env_var("OPENNEBULA_PUBLIC_MARKETPLACE")
    # sixg_sandbox_marketplace = get_env_var("OPENNEBULA_6G_SANDBOX_MARKETPLACE_NAME")
    # _select_appliances(OPENNEBULA_PUBLIC_MARKETPLACE)
    # _select_appliances(sixg_sandbox_marketplace)