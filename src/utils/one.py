import os
import re

from textwrap import dedent

from src.utils.cli import run_command
from src.utils.file import load_file, loads_json, save_file
from src.utils.logs import msg
from src.utils.temp import save_temp_file

def get_oned_conf_path() -> str:
    """
    Get the path to the oned.conf file
    
    :return: the path to the oned.conf file, ``str``
    """
    return os.path.join("/etc", "one", "oned.conf")

def get_vms() -> dict:
    """
    Get the list of VMs in OpenNebula
    
    :return: the list of VMs, ``dict``
    """
    msg("info", "[GET VMS]")
    res = run_command("onevm list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the VMs")
    return loads_json(data=res["stdout"])

## DATASTORE MANAGEMENT ##
def get_onedatastores() -> dict:
    """
    Get the list of datastores in OpenNebula
    
    :return: the list of datastores, ``dict``
    """
    msg("info", "[GET DATASTORES]")
    res = run_command("onedatastore list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the datastores")
    onedatastores = loads_json(data=res["stdout"])
    return [datastore["NAME"] for datastore in onedatastores["DATASTORE_POOL"]["DATASTORE"]]

def get_onedatastore(datastore_name: str) -> dict:
    """
    Get the details of a datastore in OpenNebula
    
    :param datastore_name: the name of the datastore, ``str``
    :return: the details of the datastore, ``dict``
    """
    msg("info", f"[GET {datastore_name} DATASTORE]")
    res = run_command(f"onedatastore show {datastore_name} -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_oneflows() -> dict:
    """
    Get the list of flows in OpenNebula
    
    :return: the list of flows, ``dict``
    """
    
    msg("info", "[GET FLOWS]")
    res = run_command("oneflow list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the flows")
    return loads_json(data=res["stdout"])

def get_onegate() -> dict:
    oned_conf_path = get_oned_conf_path()
    oned_conf = load_file(file_path=oned_conf_path, mode="rt", encoding="utf-8")
    match = re.search(r"^\s*ONEGATE_ENDPOINT\s*=\s*\"([^\"]+)\"", oned_conf, re.MULTILINE)
    if match is None:
        msg("error", "Could not find ONEGATE_ENDPOINT in oned.conf")
    onegate_endpoint = match.group(1)
    command = f"curl {onegate_endpoint}"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", f"OpenNebula CLI healthcheck failed. Command: '{command}'")

## USER MANAGEMENT ##
def get_group(group_name: str) -> dict:
    """
    Get the details of a group in OpenNebula
    
    :param group_name: the name of the group, ``str``
    :return: the details of the group, ``dict``
    """
    msg("info", f"[GET {group_name} GROUP]")
    res = run_command(f"onegroup show {group_name} -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_groups() -> dict:
    """
    Get the list of groups in OpenNebula
    
    :return: the list of groups, ``dict``
    """
    msg("info", "[GET GROUPS]")
    res = run_command("onegroup list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the groups")
    return loads_json(data=res["stdout"])

def get_user(username: str) -> dict:
    """
    Get the details of a user in OpenNebula
    
    :param username: the name of the user, ``str``
    :return: the details of the user, ``dict``
    """
    msg("info", f"[GET {username} USER]")
    res = run_command(f"oneuser show {username} -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_users() -> dict:
    """
    Get the list of users in OpenNebula
    
    :return: the list of users, ``dict``
    """
    msg("info", "[GET USERS]")
    res = run_command("oneuser list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the users")
    return loads_json(data=res["stdout"])

def create_group(group_name: str) -> int:
    """
    Create a group in OpenNebula
    
    :param group_name: the name of the group, ``str``
    :return: the ID of the group, ``int``
    """
    msg("info", f"[CREATE {group_name} GROUP]")
    res = run_command(f"onegroup create {group_name}")
    if res["rc"] != 0:
        msg("error", "Group could not be registered")
    return re.search(r"ID:\s*(\d+)", res["stdout"]).group(1)

def create_user(username: str, password: str) -> int:
    """
    Create a user in OpenNebula
    
    :param username: the user name, ``str``
    :param password: the user password, ``str``
    :return: the ID of the user, ``int``
    """
    msg("info", f"[CREATE {username} USER]")
    res = run_command(f"oneuser create {username} {password}")
    if res["rc"] != 0:
        msg("error", "User could not be registered")
    return re.search(r"ID:\s*(\d+)", res["stdout"]).group(1)

def assign_user_group(user_id, group_id) -> None:
    """
    Assign the user to group
    
    :param user_id: the ID of the user, ``int``
    :param group_id: the ID of the group, ``int``
    """
    msg("info", "[ASSIGN USER TO GROUP]")
    res = run_command(f"oneuser chgrp {user_id} {group_id}")
    if res["rc"] != 0:
        msg("error", "Could not assign the user to the group")

## IMAGES MANAGEMENT ##
def get_local_images() -> dict:
    """
    Get the list of local images in OpenNebula
    
    :return: the list of images, ``dict``
    """
    msg("info", "[GET LOCAL IMAGES]")
    res = run_command("oneimage list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the images")
    return loads_json(data=res["stdout"])

def get_local_image(image_name: str) -> dict:
    """
    Get the details of a local image in OpenNebula
    
    :param image_name: the name of the image, ``str``
    :return: the details of the image, ``dict``
    """
    msg("info", f"[GET {image_name} IMAGE]")
    res = run_command(f"oneimage show {image_name} -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_state_image(image_name: str) -> str:
    """
    Get the status of a local image in OpenNebula
    
    :param image_name: the name of the image, ``str``
    :return: the status of the image, ``str``
    """
    image = get_local_image(image_name)
    return image["IMAGE"]["STATE"]

def chown_image(image_id: int, user_id: int, group_id: int) -> None:
    """
    Change the owner of an image in OpenNebula
    
    :param image_id: the ID of the image, ``int``
    :param user_id: the ID of the user, ``int``
    :param group_id: the ID of the group, ``int``
    """
    msg("info", f"[CHANGE OWNER OF IMAGE {image_id}]")
    res = run_command(f"oneimage chown {image_id} {user_id} {group_id}")
    if res["rc"] != 0:
        msg("error", "Could not change the owner of the image")
        
## TEMPLATE MANAGEMENT ##
def chown_template(template_id: int, user_id: int, group_id: int) -> None:
    """
    Change the owner of a template in OpenNebula
    
    :param template_id: the ID of the template, ``int``
    :param user_id: the ID of the user, ``int``
    :param group_id: the ID of the group, ``int``
    """
    msg("info", f"[CHANGE OWNER OF TEMPLATE {template_id}]")
    res = run_command(f"onetemplate chown {template_id} {user_id} {group_id}")
    if res["rc"] != 0:
        msg("error", "Could not change the owner of the template")

## MARKETPLACE MANAGEMENT ##
def get_onemarkets() -> dict:
    """
    Get the list of market in OpenNebula
    
    :return: the list of marketplaces, ``dict``
    """
    msg("info", "[GET MARKETPLACES]")
    res = run_command("onemarket list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the market")
    return loads_json(data=res["stdout"])

def get_onemarket(marketplace_name: str) -> dict:
    """
    Get the details of a marketplace in OpenNebula
    
    :param marketplace_name: the name of the market, ``str``
    :return: the details of the market, ``dict``
    """
    msg("info", f"[GET {marketplace_name} MARKETPLACE]")
    res = run_command(f"onemarket show \"{marketplace_name}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def add_marketplace(marketplace_name: str, marketplace_descriptrion: str, marketplace_endpoint: str) -> int:
    """
    Add a marketplace in OpenNebula
    
    :param marketplace_name: the name of the marketplace, ``str``
    :param marketplace_descriptrion: the description of the marketplace, ``str``
    :param marketplace_endpoint: the endpoint of the marketplace, ``str``
    :return: the ID of the marketplace, ``int``
    """
    marketplace_content = dedent(f"""
        NAME = {marketplace_name}
        DESCRIPTION = {marketplace_descriptrion}
        ENDPOINT = {marketplace_endpoint}
        MARKET_MAD = one
    """).strip()
    marketplace_template_path = save_temp_file(data=marketplace_content, file_path="marketplace_template", mode="w", encoding="utf-8")
    res = run_command(f"onemarket create {marketplace_template_path}")
    if res["rc"] != 0:
        msg("error", "Marketplace could not be registered. Please, review the marketplace_template file")
    return re.search(r"ID:\s*(\d+)", res["stdout"]).group(1)

def get_marketplace_monitoring_interval() -> int:
    """
    Get the monitoring interval of the marketplace
    
    :return: the interval in seconds, ``int``
    """
    oned_conf_path = get_oned_conf_path()
    oned_conf = load_file(file_path=oned_conf_path, mode="rt", encoding="utf-8")
    match = re.search(r"^\s*MONITORING_INTERVAL_MARKET\s*=\s*\"?(\d+)\"?", oned_conf, re.MULTILINE)
    if match is None:
        msg("error", "Could not find MONITORING_INTERVAL_MARKET in oned.conf")
    return int(match.group(1))
    
def update_marketplace_monitoring_interval(interval: int) -> None:
    """
    Update the monitoring interval of the marketplace
    
    :param interval: the interval in seconds, ``int``
    """
    oned_conf_path = get_oned_conf_path()
    oned_conf = load_file(file_path=oned_conf_path, mode="rt", encoding="utf-8")
    pattern = r"^\s*MONITORING_INTERVAL_MARKET\s*=\s*\"?(\d+)\"?"
    updated_conf = re.sub(pattern, f"MONITORING_INTERVAL_MARKET = {interval}", oned_conf, flags=re.MULTILINE)
    save_file(data=updated_conf, file_path=oned_conf_path, mode="w", encoding="utf-8")
    msg("info", f"Marketplace monitoring interval set to interval {interval}")

## APPLIANCE MANAGEMENT ##
def get_appliances_oneadmin() -> list:
    """
    Get the appliances from the oneadmin user in OpenNebula
        
    :return: the appliances, ``list``
    """
    msg("info", "[GET APPLIANCES FROM ONEADMIN USER]")
    oneadmin_id = int(get_user(username="oneadmin")["USER"]["ID"])
    res = run_command(f"onemarketapp list {oneadmin_id} -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_appliances_marketplace(marketplace_id: str) -> list:
    """
    Get the appliances from a marketplace in OpenNebula
    
    :param marketplace_id: the ID of the market, ``str``
    :return: the appliances, ``list``
    """
    msg("info", f"[GET APPLIANCES FROM {marketplace_id} MARKETPLACE]")
    oneadmin_appliances = get_appliances_oneadmin()
    if oneadmin_appliances is None:
        return None
    return [app["NAME"] for app in oneadmin_appliances if app["MARKETPLACEAPP"]["MARKETPLACE_ID"] == marketplace_id]

def export_image(marketplace_id: int, appliance_name: str, datastore_id: int) -> None:
    """
    Export an image from OpenNebula
    
    :param marketplace_id: the id of the market, ``int``
    :param appliance_name: the name of the image, ``str``
    :param datastore_id: the datastore where the image is stored, ``int``
    """
    msg("info", f"[EXPORT {appliance_name} IMAGE]")
    res = run_command(f"onemarketapp export {marketplace_id} {appliance_name} -d {datastore_id} -j")
    if res["rc"] != 0:
        msg("error", "Could not export the image")
    image_id = re.search(r"IMAGE\s+ID:\s*(\d+)", res["stdout"]).group(1)
    template_id = re.search(r"VMTEMPLATE\s+ID:\s*(\d+)", res["stdout"]).group(1)
    return image_id, template_id

## SERVICE MANAGEMENT ##
def restart_one() -> None:
    """
    Restart the OpenNebula daemon
    """
    res = run_command("systemctl restart opennebula")
    if res["rc"] != 0:
        msg("error", "Could not restart the OpenNebula daemon")
    msg("info", "OpenNebula daemon restarted")

## HEALTH MANAGEMENT ##
def check_one_health() -> None:
    """
    Check the health of OpenNebula
    """
    msg("info", "[OPENNEBULA HEALTH CHECK]")
    get_groups()
    get_users()
    get_vms()
    get_onedatastores()
    get_oneflows()
    get_onemarkets()
    get_onegate()
    msg("info", "OpenNebula is healthy")