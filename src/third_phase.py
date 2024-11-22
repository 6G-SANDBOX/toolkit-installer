from textwrap import dedent

from src.utils.cli import run_command
from src.utils.dotenv import get_env_var
from src.utils.file import loads_json
from src.utils.interactive import ask_text, ask_checkbox
from src.utils.logs import msg
from src.utils.temp import save_temp_file

def _create_sixg_sandbox_group(sixg_sandbox_group: str) -> int:
    """
    Create a 6G-SANDBOX group in the OpenNebula installation
    
    :param sixg_sandbox_group: the name of the 6G-SANDBOX group, ``str``
    :return: the ID of the group, ``int``
    """
    msg("info", "[CREATE 6G-SANDBOX GROUP]")
    group = ask_text("Enter the name for the 6G-SANDBOX group:", default=sixg_sandbox_group, validate=True)
    res = run_command("onegroup list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the groups")
    groups = loads_json(data=res["stdout"])
    group_id = None
    for group in groups["GROUP_POOL"]["GROUP"]:
        if group["NAME"] == group:
            msg("info", "6G-SANDBOX group already present with ID " + group["ID"])
            group_id = int(group["ID"])
            break
    if not group_id:
        msg("info", "6G-SANDBOX group not found, creating 6G-SANDBOX group...")
        group_content = dedent(f"""
            NAME = {group}
        """).strip()
        group_template_path = save_temp_file(data=group_content, file_path="group_template", mode="w", encoding="utf-8")
        res = run_command(f"onegroup create {group_template_path}")
        if res["rc"] != 0:
            msg("error", "The 6G-SANDBOX group could not be registered. Please, review the group_template file")
        group_id = res["stdout"].split()[1]
        msg("info", f"6G-SANDBOX group registered successfully with ID {group_id}")
    return group_id

def _create_jenkins_user(jenkins_user: str) -> None:
    """
    Create a Jenkins user in the OpenNebula installation
    
    :param jenkins_user: the username for the Jenkins user, ``str``
    """
    msg("info", "[CREATE JENKINS USER]")
    username = ask_text("Enter the username for the Jenkins user:", default=jenkins_user, validate=True)
    password = ask_text("Enter the password for the Jenkins user:", default="", validate=True)
    res = run_command("oneuser list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the users")
    users = loads_json(data=res["stdout"])
    user_id = None
    for user in users["USER_POOL"]["USER"]:
        if user["NAME"] == username:
            msg("info", "Jenkins user already present with ID " + user["ID"])
            user_id = int(user["ID"])
            break
    if not user_id:
        msg("info", "Jenkins OpenNebula user not found, creating Jenkins user...")
        user_content = dedent(f"""
            NAME = {username}
            PASSWORD = {password}
        """).strip()
        user_template_path = save_temp_file(data=user_content, file_path="jenkins_user_template", mode="w", encoding="utf-8")
        res = run_command(f"oneuser create {user_template_path}")
        if res["rc"] != 0:
            msg("error", "The Jenkins user could not be registered. Please, review the user_template file")
        user_id = res["stdout"].split()[1]
        msg("info", f"Jenkins user registered successfully with ID {user_id}")

def _assign_jenkins_user_to_group(user_id: int, group_id: int) -> None:
    """
    Assign the Jenkins user to the 6G-SANDBOX group
    
    :param user_id: the ID of the Jenkins user, ``int``
    :param group_id: the ID of the 6G-SANDBOX group, ``int``
    """
    msg("info", "[ASSIGN JENKINS USER TO 6G-SANDBOX GROUP]")
    res = run_command(f"oneuser chgrp {user_id} {group_id}")
    if res["rc"] != 0:
        msg("error", "Could not assign the Jenkins user to the 6G-SANDBOX group")

def _select_appliances(marketplace_name: str) -> None:
    """
    Select the appliances from the marketplace
    
    :param marketplace_name: the name of the marketplace, ``str``
    """
    msg("info", f"[SELECT APPLIANCES FROM {marketplace_name}]")
    res = run_command("onemarketplace list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the appliances")
    appliances = loads_json(data=res["stdout"])
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
    sixg_sandbox_group = get_env_var("OPENNEBULA_6G_SANDBOX_GROUP")
    group_id = _create_sixg_sandbox_group(sixg_sandbox_group)
    jenkins_user = get_env_var("OPENNEBULA_JENKINS_USER")
    user_id = _create_jenkins_user(jenkins_user=jenkins_user)
    _assign_jenkins_user_to_group(user_id=user_id, group_id=group_id)
    opennebula_marketplace = get_env_var("OPENNEBULA_MARKETPLACE")
    sixg_sandbox_marketplace = get_env_var("OPENNEBULA_6G_SANDBOX_MARKETPLACE_NAME")
    _select_appliances(opennebula_marketplace)
    _select_appliances(sixg_sandbox_marketplace)