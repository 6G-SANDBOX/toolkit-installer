import os
import re

from time import sleep
from textwrap import dedent

from src.utils.cli import run_command
from src.utils.file import load_file, loads_json, save_file
from src.utils.interactive import ask_select
from src.utils.logs import msg
from src.utils.temp import save_temp_file

## CONFIG MANAGEMENT ##
def get_oned_conf_path() -> str:
    """
    Get the path to the oned.conf file
    
    :return: the path to the oned.conf file, ``str``
    """
    return os.path.join("/etc", "one", "oned.conf")

def get_onegate_endpoint() -> dict:
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
    return onegate_endpoint

## NETWORKS MANAGEMENT ##
def get_vnets() -> dict:
    """
    Get the list of VNets in OpenNebula
    
    :return: the list of VNets, ``dict``
    """
    msg("info", "[GET VNETS]")
    res = run_command("onevnet list -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_vnets_names() -> list:
    """
    Get the names of the VNets in OpenNebula
    
    :return: the names of the VNets, ``list``
    """
    vnets = get_vnets()
    if vnets is None:
        return None
    return [vnet["NAME"] for vnet in vnets["VNET_POOL"]["VNET"]]

def get_vnet(vnet_name: str) -> dict:
    """
    Get the details of a VNet in OpenNebula
    
    :param vnet_name: the name of the VNet, ``str``
    :return: the details of the VNet, ``dict``
    """
    msg("info", f"[GET {vnet_name} VNET]")
    res = run_command(f"onevnet show \"{vnet_name}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_vnet_id(vnet_name: str) -> int:
    """
    Get the ID of a VNet in OpenNebula
    
    :param vnet_name: the name of the VNet, ``str``
    :return: the ID of the VNet, ``int``
    """
    vnet = get_vnet(vnet_name)
    if vnet is None:
        return None
    return int(vnet["VNET"]["ID"])

## VM MANAGEMENT ##
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

def get_vm(vm_name: str) -> dict:
    """
    Get the details of a VM in OpenNebula
    
    :param vm_name: the name of the VM, ``str``
    :return: the details of the VM, ``dict``
    """
    msg("info", f"[GET {vm_name} VM]")
    res = run_command(f"onevm show \"{vm_name}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def chown_vm(vm_id: int, user_id: int, group_id: int) -> None:
    """
    Change the owner of a VM in OpenNebula
    
    :param vm_id: the ID of the VM, ``int``
    :param user_id: the ID of the user, ``int``
    :param group_id: the ID of the group, ``int``
    """
    msg("info", f"[CHANGE OWNER OF VM {vm_id}]")
    res = run_command(f"onevm chown {vm_id} {user_id} {group_id}")
    if res["rc"] != 0:
        msg("error", "Could not change the owner of the VM")

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
    res = run_command(f"onedatastore show \"{datastore_name}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_onedatastore_id(datastore_name: str) -> int:
    """
    Get the ID of a datastore in OpenNebula
    
    :param datastore_name: the name of the datastore, ``str``
    :return: the ID of the datastore, ``int``
    """
    datastore = get_onedatastore(datastore_name)
    if datastore is None:
        return None
    return int(datastore["DATASTORE"]["ID"])

## ONEFLOW MANAGEMENT ##
def get_oneflows() -> dict:
    """
    Get the list of services in OpenNebula
    
    :return: the list of services, ``dict``
    """
    msg("info", "[GET SERVICES]")
    res = run_command("oneflow list -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_oneflow(oneflow_name: str) -> dict:
    """
    Get the details of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the details of the service, ``dict``
    """
    msg("info", f"[GET {oneflow_name} SERVICE]")
    res = run_command(f"oneflow show \"{oneflow_name}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_oneflow_roles(oneflow_name: str) -> dict:
    """
    Get the roles of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the roles of the service, ``dict``
    """
    oneflow = get_oneflow(oneflow_name)
    if oneflow is None:
        return None
    return oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["roles"]

def rename_oneflow(oneflow_id: int, new_name: str) -> None:
    """
    Rename a service in OpenNebula
    
    :param oneflow_id: the ID of the service, ``int``
    :param new_name: the new name of the service, ``str``
    """
    msg("info", f"[RENAME SERVICE {oneflow_id}]")
    res = run_command(f"oneflow rename {oneflow_id} \"{new_name}\"")
    if res["rc"] != 0:
        msg("error", "Could not rename the service")

def chown_oneflow(oneflow_id: int, user_id: int, group_id: int) -> None:
    """
    Change the owner of a service in OpenNebula
    
    :param oneflow_id: the ID of the service, ``int``
    :param user_id: the ID of the user, ``int``
    :param group_id: the ID of the group, ``int``
    """
    msg("info", f"[CHANGE OWNER OF SERVICE {oneflow_id}]")
    res = run_command(f"oneflow chown {oneflow_id} {user_id} {group_id}")
    if res["rc"] != 0:
        msg("error", "Could not change the owner of the service")

## ONEFLOW TEMPLATE MANAGEMENT ##
def get_oneflow_template(oneflow_name: str) -> dict:
    """
    Get the details of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the details of the service, ``dict``
    """
    msg("info", f"[GET {oneflow_name} SERVICE]")
    res = run_command(f"oneflow-template show \"{oneflow_name}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_oneflow_template_id(oneflow_name: str) -> int:
    """
    Get the ID of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the ID of the service, ``int``
    """
    oneflow = get_oneflow_template(oneflow_name)
    if oneflow is None:
        return None
    return int(oneflow["DOCUMENT"]["ID"])

def get_oneflow_template_custom_attrs(oneflow_name: str) -> dict:
    """
    Get the custom_attrs of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the custom_attrs of the service, ``dict``
    """
    oneflow = get_oneflow_template(oneflow_name)
    if oneflow is None:
        return None
    return oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["custom_attrs"]

def instantiate_oneflow_template(oneflow_template_name: str, file_path: str) -> None:
    """
    Instantiate a service in OpenNebula
    
    :param oneflow_template_id: the ID of the service, ``int``
    :param file_path: the path to the file with params, ``str``
    """
    msg("info", f"[INSTANTIATE SERVICE {oneflow_template_name}]")
    res = run_command(f"oneflow-template instantiate \"{oneflow_template_name}\" < {file_path}")
    if res["rc"] != 0:
        msg("error", "Could not instantiate the service")
    return int(re.search(r"ID:\s*(\d+)", res["stdout"]).group(1))

def chown_oneflow_template(service_id: int, user_id: int, group_id: int) -> None:
    """
    Change the owner of an image in OpenNebula
    
    :param service_id: the ID of the service, ``int``
    :param user_id: the ID of the user, ``int``
    :param group_id: the ID of the group, ``int``
    """
    msg("info", f"[CHANGE OWNER OF IMAGE {service_id}]")
    res = run_command(f"oneflow-template chown {service_id} {user_id} {group_id}")
    if res["rc"] != 0:
        msg("error", "Could not change the owner of the image")

## USER MANAGEMENT ##
def get_group(group_name: str) -> dict:
    """
    Get the details of a group in OpenNebula
    
    :param group_name: the name of the group, ``str``
    :return: the details of the group, ``dict``
    """
    msg("info", f"[GET {group_name} GROUP]")
    res = run_command(f"onegroup show \"{group_name}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_group_id(group_name: str) -> int:
    """
    Get the ID of a group in OpenNebula
    
    :param group_name: the name of the group, ``str``
    :return: the ID of the group, ``int``
    """
    group = get_group(group_name)
    if group is None:
        return None
    return int(group["GROUP"]["ID"])

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

def get_username(username: str) -> dict:
    """
    Get the details of a user in OpenNebula
    
    :param username: the name of the user, ``str``
    :return: the details of the user, ``dict``
    """
    msg("info", f"[GET {username} USER]")
    res = run_command(f"oneuser show \"{username}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_username_id(username: str) -> int:
    """
    Get the ID of a user in OpenNebula
    
    :param username: the name of the user, ``str``
    :return: the ID of the user, ``int``
    """
    user = get_username(username=username)
    if user is None:
        return None
    return int(user["USER"]["ID"])

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
    res = run_command(f"oneuser create \"{username}\" \"{password}\"")
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

def chauth_ssh_key(username: str, ssh_key_path: str) -> None:
    """
    Update the SSH key of a user in OpenNebula
    
    :param username: the name of the user, ``int``
    :param ssh_key_path: the path with SSH key, ``str``
    """
    msg("info", f"[UPDATE SSH KEY OF USER {username}]")
    res = run_command(f"oneuser chauth \"{username}\" --ssh --key \"{ssh_key_path}\"")
    if res["rc"] != 0:
        msg("error", "Could not update the SSH key")

## TEMPLATE MANAGEMENT ##
def get_templates() -> dict:
    """
    Get the list of local templates in OpenNebula
    
    :return: the list of templates, ``dict``
    """
    msg("info", "[GET LOCAL TEMPLATES]")
    res = run_command("onetemplate list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the templates")
    return loads_json(data=res["stdout"])

def get_template(template_name: str) -> dict:
    """
    Get the details of a local template in OpenNebula
    
    :param template_name: the name of the template, ``str``
    :return: the details of the template, ``dict``
    """
    msg("info", f"[GET {template_name} TEMPLATE]")
    res = run_command(f"onetemplate show \"{template_name}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

## IMAGES MANAGEMENT ##
def get_images() -> dict:
    """
    Get the list of local images in OpenNebula
    
    :return: the list of images, ``dict``
    """
    msg("info", "[GET LOCAL IMAGES]")
    res = run_command("oneimage list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the images")
    return loads_json(data=res["stdout"])

def get_image(image_name: str) -> dict:
    """
    Get the details of a local image in OpenNebula
    
    :param image_name: the name of the image, ``str``
    :return: the details of the image, ``dict``
    """
    msg("info", f"[GET {image_name} IMAGE]")
    res = run_command(f"oneimage show \"{image_name}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_state_image(image_name: str) -> str:
    """
    Get the status of a local image in OpenNebula
    
    :param image_name: the name of the image, ``str``
    :return: the status of the image, ``str``
    """
    image = get_image(image_name)
    if image is None:
        return None
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

def rename_image(image_id: int, new_name: str) -> None:
    """
    Rename an image in OpenNebula
    
    :param image_id: the ID of the image, ``int``
    :param new_name: the new name of the image, ``str``
    """
    msg("info", f"[RENAME IMAGE {image_id}]")
    res = run_command(f"oneimage rename {image_id} \"{new_name}\"")
    if res["rc"] != 0:
        msg("error", "Could not rename the image")

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

def get_onemarket_id(marketplace_name: str) -> int:
    """
    Get the ID of a marketplace in OpenNebula
    
    :param marketplace_name: the name of the market, ``str``
    :return: the ID of the market, ``int``
    """
    marketplace = get_onemarket(marketplace_name)
    if marketplace is None:
        return None
    return int(marketplace["MARKETPLACE"]["ID"])

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
def get_appliance(appliance_name: str, marketplace_id: int) -> dict:
    """
    Get the details of an appliance in OpenNebula
    
    :param appliance_name: the name of the appliance, ``str``
    :param marketplace_id: the ID of the marketplace, ``int``
    :return: the details of the appliance, ``dict``
    """
    msg("info", f"[GET {appliance_name} APPLIANCE]")
    res = run_command(f"onemarketapp show \"{appliance_name}\" -j")
    if res["rc"] != 0:
        return None
    appliance = loads_json(data=res["stdout"])
    if appliance["MARKETPLACEAPP"]["MARKETPLACE_ID"] != str(marketplace_id):
        return None
    return appliance

def get_appliance_id(appliance_name: str, marketplace_id: int) -> int:
    """
    Get the ID of an appliance in OpenNebula
    
    :param appliance_name: the name of the appliance, ``str``
    :param marketplace_id: the ID of the marketplace, ``int``
    :return: the ID of the appliance, ``int``
    """
    appliance = get_appliance(appliance_name, marketplace_id)
    if appliance is None:
        return None
    return int(appliance["MARKETPLACEAPP"]["ID"])

def get_type_appliance(appliance_name: str, marketplace_id: int) -> str:
    """
    Get the type of an appliance in OpenNebula
    
    :param appliance_name: the name of the appliance, ``str``
    :param marketplace_id: the ID of the marketplace, ``int``
    :return: the type of the appliance, ``str``
    """
    msg("info", f"[GET TYPE OF {appliance_name} APPLIANCE]")
    appliance = get_appliance(appliance_name, marketplace_id)
    if appliance is None:
        return None
    appliance_type = appliance["MARKETPLACEAPP"]["TYPE"]
    if appliance_type == "1":
        return "IMAGE"
    elif appliance_type == "2":
        return "VM"
    elif appliance_type == "3":
        return "SERVICE"
    else:
        msg("error", "Appliance type not recognized")

def get_appliances_oneadmin() -> dict:
    """
    Get the appliances of oneadmin user in OpenNebula
        
    :return: the appliances, ``dict``
    """
    msg("info", "[GET APPLIANCES FROM ONEADMIN USER]")
    oneadmin_id = get_username_id(username="oneadmin")
    res = run_command(f"onemarketapp list {oneadmin_id} -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_appliances_marketplace(marketplace_id: int) -> list:
    """
    Get the appliances from a marketplace in OpenNebula
    
    :param marketplace_id: the ID of the market, ``int``
    :return: list of appliances, ``list``
    """
    msg("info", f"[GET APPLIANCES FROM {marketplace_id} MARKETPLACE]")
    oneadmin_appliances = get_appliances_oneadmin()
    if oneadmin_appliances is None:
        return None
    appliances = oneadmin_appliances["MARKETPLACEAPP_POOL"]["MARKETPLACEAPP"]
    return [appliance["NAME"] for appliance in appliances if appliance["MARKETPLACE_ID"] == str(marketplace_id)]
    
def export_appliance(appliance_id: int, appliance_name: str, datastore_id: int) -> None:
    """
    Export an appliance from OpenNebula
    
    :param appliance_id: the id of the appliance, ``int``
    :param appliance_name: the name of the appliance, ``str``
    :param datastore_id: the datastore where the appliance is stored, ``int``
    """
    msg("info", f"[EXPORT {appliance_name} APPLIANCE]")
    res = run_command(f"onemarketapp export {appliance_id} \"{appliance_name}\" -d {datastore_id}")
    if res["rc"] != 0:
        msg("error", "Could not export the appliance")
    data = res["stdout"]
    image_ids = [int(id_) for id_ in re.findall(r"ID:\s*(\d+)", re.search(r"IMAGE\s*\n((?:\s*ID:\s*\d+\s*\n?)*)", data).group(1))]
    template_ids = [int(id_) for id_ in re.findall(r"ID:\s*(\d+)", re.search(r"VMTEMPLATE\s*\n((?:\s*ID:\s*\d+\s*\n?)*)", data).group(1))]
    match = re.search(r"SERVICE_TEMPLATE\s*\n(?:\s*ID:\s*(\d+))+", data)
    if match:
        service_id = int(match.group(1))
    else:
        service_id = None
    return image_ids, template_ids, service_id

def add_appliances_from_marketplace(sixg_sandbox_group_id: int, jenkins_user_id: int, marketplace_id: int, appliances: list) -> None:
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
                image_ids, template_ids, service_id = export_appliance(appliance_id=appliance_id, appliance_name=appliance_name, datastore_id=datastore_id)
                sleep(10)
                for i, image_id in enumerate(image_ids):
                    rename_image(image_id=image_id, new_name=f"{appliance_name}-{i}")
                for i, image_id in enumerate(image_ids):
                    while get_state_image(f"{appliance_name}-{i}") != "1":
                        msg("info", "Please, wait 10s for the image to be ready...")
                        sleep(10)
                for i, image_id in enumerate(image_ids):
                    chown_image(image_id=image_id, user_id=jenkins_user_id, group_id=sixg_sandbox_group_id)
                for i, template_id in enumerate(template_ids):
                    chown_template(template_id=template_id, user_id=jenkins_user_id, group_id=sixg_sandbox_group_id)
                chown_oneflow_template(service_id=service_id, user_id=jenkins_user_id, group_id=sixg_sandbox_group_id)

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
    get_onegate_endpoint()
    msg("info", "OpenNebula is healthy")