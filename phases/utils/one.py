import os
import re

from time import sleep
from textwrap import dedent

from phases.utils.cli import run_command
from phases.utils.file import load_file, loads_json, save_file
from phases.utils.interactive import ask_select
from phases.utils.logs import msg
from phases.utils.temp import save_temp_file

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
    res = run_command(f"onevnet show \"{vnet_name}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_vnet_id(vnet_name: str) -> int:
    """
    Get the ID of a VNet in OpenNebula
    
    :param vnet_name: the name of the VNet, ``str``
    :return: the id of the VNet, ``int``
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
    msg("info", f"Getting OpenNebula VM: {vm_name}")
    res = run_command(f"onevm show \"{vm_name}\" -j")
    if res["rc"] != 0:
        msg("info", "VM not found")
        return None
    msg("info", "VM found")
    return loads_json(data=res["stdout"])

def chown_vm(vm_id: int, username: str, group_name: str) -> None:
    """
    Change the owner of a VM in OpenNebula
    
    :param vm_id: the id of the VM, ``int``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    msg("info", f"Changing owner of OpenNebula VM {vm_id} to {username}:{group_name}")
    res = run_command(f"onevm chown {vm_id} \"{username}\" \"{group_name}\"")
    if res["rc"] != 0:
        msg("error", "Could not change the owner of the VM")
    msg("info", "Owner of VM changed")

def get_vm_ip(vm_name: str) -> str:
    """
    Get the IP of a VM in OpenNebula
    
    :param vm_name: the name of the VM, ``str``
    :return: the id of the VM, ``str``
    """
    vm = get_vm(vm_name)
    msg("info", f"Getting IP of OpenNebula VM {vm_name}")
    if vm is None:
        return None
    vm_ip = vm["VM"]["TEMPLATE"]["NIC"][0]["IP"]
    msg("info", f"IP of VM {vm_name} is {vm_ip}")
    return vm_ip

## DATASTORE MANAGEMENT ##
def get_onedatastores() -> dict:
    """
    Get the list of datastores in OpenNebula
    
    :return: the list of datastores, ``dict``
    """
    msg("info", "Getting OpenNebula datastores")
    res = run_command("onedatastore list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the datastores")
    onedatastores = loads_json(data=res["stdout"])
    msg("info", "Datastores found")
    return [datastore["NAME"] for datastore in onedatastores["DATASTORE_POOL"]["DATASTORE"]]

def get_onedatastore(datastore_name: str) -> dict:
    """
    Get the details of a datastore in OpenNebula
    
    :param datastore_name: the name of the datastore, ``str``
    :return: the details of the datastore, ``dict``
    """
    res = run_command(f"onedatastore show \"{datastore_name}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_onedatastore_id(datastore_name: str) -> int:
    """
    Get the id of a datastore in OpenNebula
    
    :param datastore_name: the name of the datastore, ``str``
    :return: the id of the datastore, ``int``
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
    msg("info", f"Getting roles of OpenNebula service {oneflow_name}")
    oneflow = get_oneflow(oneflow_name)
    if oneflow is None:
        return None
    msg("info", "Roles found")
    return oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["roles"]

def rename_oneflow(oneflow_id: int, new_name: str) -> None:
    """
    Rename a service in OpenNebula
    
    :param oneflow_id: the id of the service, ``int``
    :param new_name: the new name of the service, ``str``
    """
    res = run_command(f"oneflow rename {oneflow_id} \"{new_name}\"")
    if res["rc"] != 0:
        msg("error", "Could not rename the service")

def chown_oneflow(oneflow_id: int, username: str, group_name: str) -> None:
    """
    Change the owner of a service in OpenNebula
    
    :param oneflow_id: the id of the service, ``int``
    :param user_id: the name of the user, ``str``
    :param group_id: the id of the group, ``str``
    """
    msg("info", f"Changing owner of OpenNebula service {oneflow_id} to {username}:{group_name}")
    res = run_command(f"oneflow chown {oneflow_id} \"{username}\" \"{group_name}\"")
    if res["rc"] != 0:
        msg("error", "Could not change the owner of the service")
    msg("info", "Owner of service changed")

## ONEFLOW TEMPLATE MANAGEMENT ##
def get_oneflow_template(oneflow_name: str) -> dict:
    """
    Get the details of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the details of the service, ``dict``
    """
    res = run_command(f"oneflow-template show \"{oneflow_name}\" -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_oneflow_template_id(oneflow_name: str) -> int:
    """
    Get the id of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the id of the service, ``int``
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
    msg("info", f"Getting custom_attrs of OpenNebula service {oneflow_name}")
    oneflow = get_oneflow_template(oneflow_name)
    if oneflow is None:
        return None
    custom_attrs = oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["custom_attrs"]
    msg("info", "Custom_attrs found")
    return custom_attrs

def get_oneflow_template_networks(oneflow_name: str) -> dict:
    """
    Get the networks of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the networks of the service, ``dict``
    """
    msg("info", f"Getting networks of OpenNebula service {oneflow_name}")
    oneflow = get_oneflow_template(oneflow_name)
    if oneflow is None:
        return None
    networks = oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["networks"]
    msg("info", "Networks found")
    return networks

def instantiate_oneflow_template(oneflow_template_name: str, file_path: str) -> None:
    """
    Instantiate a service in OpenNebula
    
    :param oneflow_template_id: the id of the service, ``int``
    :param file_path: the path to the file with params, ``str``
    """
    msg("info", f"Instantiating OpenNebula service {oneflow_template_name}")
    res = run_command(f"oneflow-template instantiate \"{oneflow_template_name}\" < {file_path}")
    if res["rc"] != 0:
        msg("error", "Could not instantiate the service")
    msg("info", "Service instantiated")
    return int(re.search(r"ID:\s*(\d+)", res["stdout"]).group(1))

def chown_oneflow_template(service_id: int, username: str, group_name: str) -> None:
    """
    Change the owner of an image in OpenNebula
    
    :param service_id: the id of the service, ``int``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    msg("info", f"Changing owner of OpenNebula service {service_id} to {username}:{group_name}")
    res = run_command(f"oneflow-template chown {service_id} \"{username}\" \"{group_name}\"")
    if res["rc"] != 0:
        msg("error", "Could not change the owner of the image")
    msg("info", "Owner of service changed")

## USER MANAGEMENT ##
def get_group(group_name: str) -> dict:
    """
    Get the details of a group in OpenNebula
    
    :param group_name: the name of the group, ``str``
    :return: the details of the group, ``dict``
    """
    msg("info", f"Getting OpenNebula group: {group_name}")
    res = run_command(f"onegroup show \"{group_name}\" -j")
    if res["rc"] != 0:
        msg("info", "Group not found")
        return None
    msg("info", "Group found")
    return loads_json(data=res["stdout"])

def get_group_id(group_name: str) -> int:
    """
    Get the id of a group in OpenNebula
    
    :param group_name: the name of the group, ``str``
    :return: the id of the group, ``int``
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
    msg("info", f"Getting OpenNebula user: {username}")
    res = run_command(f"oneuser show \"{username}\" -j")
    if res["rc"] != 0:
        msg("info", "User not found")
        return None
    msg("info", "User found")
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
    res = run_command("oneuser list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the users")
    return loads_json(data=res["stdout"])

def create_group(group_name: str) -> int:
    """
    Create a group in OpenNebula
    
    :param group_name: the name of the group, ``str``
    :return: the id of the group, ``int``
    """
    msg("info", f"Creating OpenNebula group: {group_name}")
    res = run_command(f"onegroup create {group_name}")
    if res["rc"] != 0:
        msg("error", "Group could not be registered")
    msg("info", "Group created")
    return re.search(r"ID:\s*(\d+)", res["stdout"]).group(1)

def create_user(username: str, password: str) -> int:
    """
    Create a user in OpenNebula
    
    :param username: the user name, ``str``
    :param password: the user password, ``str``
    :return: the id of the user, ``int``
    """
    msg("info", f"Creating OpenNebula user: {username}")
    res = run_command(f"oneuser create \"{username}\" \"{password}\"")
    if res["rc"] != 0:
        msg("error", "User could not be registered")
    msg("info", "User created")
    return re.search(r"ID:\s*(\d+)", res["stdout"]).group(1)

def assign_user_group(username: str, group_name: str) -> None:
    """
    Assign the user to group
    
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    msg("info", f"Assigning user {username} to group {group_name}")
    res = run_command(f"oneuser chgrp \"{username}\" \"{group_name}\"")
    if res["rc"] != 0:
        msg("error", "Could not assign the user to the group")
    msg("info", "User assigned to group")

def add_ssh_key(username: str, jenkins_ssh_key: str) -> None:
    """
    Update the SSH key of a user in OpenNebula
    
    :param username: the name of the user, ``int``
    :param jenkins_ssh_key: the SSH key, ``str``
    """
    msg("info", f"Updating SSH key of OpenNebula user {username}")
    res = f"echo \'SSH_PUBLIC_KEY=\"{jenkins_ssh_key}\"\' | oneuser update {username}"
    if res["rc"] != 0:
        msg("error", "Could not update the SSH key")
    msg("info", "SSH key updated")

## TEMPLATE MANAGEMENT ##
def get_templates() -> dict:
    """
    Get the list of local templates in OpenNebula
    
    :return: the list of templates, ``dict``
    """
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
    msg("info", f"Getting OpenNebula image: {image_name}")
    res = run_command(f"oneimage show \"{image_name}\" -j")
    if res["rc"] != 0:
        msg("info", "Image not found")
        return None
    msg("info", "Image found")
    return loads_json(data=res["stdout"])

def get_state_image(image_name: str) -> str:
    """
    Get the status of a local image in OpenNebula
    
    :param image_name: the name of the image, ``str``
    :return: the status of the image, ``str``
    """
    msg("info", f"Getting state of OpenNebula image: {image_name}")
    image = get_image(image_name)
    if image is None:
        return None
    state = image["IMAGE"]["STATE"]
    msg("info", f"State of image {image_name} is {state}")
    return state

def chown_image(image_id: int, username: str, group_name: str) -> None:
    """
    Change the owner of an image in OpenNebula
    
    :param image_id: the id of the image, ``int``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    msg("info", f"Changing owner of OpenNebula image {image_id} to {username}:{group_name}")
    res = run_command(f"oneimage chown {image_id} \"{username}\" \"{group_name}\"")
    if res["rc"] != 0:
        msg("error", "Could not change the owner of the image")
    msg("info", "Owner of image changed")

def rename_image(image_id: int, new_name: str) -> None:
    """
    Rename an image in OpenNebula
    
    :param image_id: the id of the image, ``int``
    :param new_name: the new name of the image, ``str``
    """
    msg("info", f"Renaming OpenNebula image {image_id} to {new_name}")
    res = run_command(f"oneimage rename {image_id} \"{new_name}\"")
    if res["rc"] != 0:
        msg("error", "Could not rename the image")
    msg("info", "Image renamed")

## TEMPLATE MANAGEMENT ##
def chown_template(template_id: int, username: str, group_name: str) -> None:
    """
    Change the owner of a template in OpenNebula
    
    :param template_id: the id of the template, ``int``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    msg("info", f"Changing owner of OpenNebula template {template_id} to {username}:{group_name}")
    res = run_command(f"onetemplate chown {template_id} \"{username}\" \"{group_name}\"")
    if res["rc"] != 0:
        msg("error", "Could not change the owner of the template")
    msg("info", "Owner of template changed")

## MARKETPLACE MANAGEMENT ##
def get_onemarkets() -> dict:
    """
    Get the list of market in OpenNebula
    
    :return: the list of marketplaces, ``dict``
    """
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
    msg("info", f"Getting OpenNebula marketplace: {marketplace_name}")
    res = run_command(f"onemarket show \"{marketplace_name}\" -j")
    if res["rc"] != 0:
        msg("info", "Marketplace not found")
        return None
    msg("info", "Marketplace found")
    return loads_json(data=res["stdout"])

def get_onemarket_id(marketplace_name: str) -> int:
    """
    Get the id of a marketplace in OpenNebula
    
    :param marketplace_name: the name of the market, ``str``
    :return: the id of the market, ``int``
    """
    marketplace = get_onemarket(marketplace_name)
    if marketplace is None:
        return None
    return int(marketplace["MARKETPLACE"]["ID"])

def add_marketplace(marketplace_name: str, marketplace_description: str, marketplace_endpoint: str) -> int:
    """
    Add a marketplace in OpenNebula
    
    :param marketplace_name: the name of the marketplace, ``str``
    :param marketplace_description: the description of the marketplace, ``str``
    :param marketplace_endpoint: the endpoint of the marketplace, ``str``
    :return: the id of the marketplace, ``int``
    """
    marketplace_content = dedent(f"""
        NAME = "{marketplace_name}"
        DESCRIPTION = "{marketplace_description}"
        ENDPOINT = "{marketplace_endpoint}"
        MARKET_MAD = one
    """).strip()
    marketplace_template_path = save_temp_file(data=marketplace_content, file_path="marketplace_template", mode="w", encoding="utf-8")
    msg("info", f"Creating OpenNebula marketplace: {marketplace_name}")
    res = run_command(f"onemarket create {marketplace_template_path}")
    if res["rc"] != 0:
        msg("error", "Marketplace could not be registered. Please, review the marketplace_template file")
    msg("info", "Marketplace created")
    return re.search(r"ID:\s*(\d+)", res["stdout"]).group(1)

def get_marketplace_monitoring_interval() -> int:
    """
    Get the monitoring interval of the marketplace
    
    :return: the interval in seconds, ``int``
    """
    msg("info", "Getting OpenNebula marketplace monitoring interval")
    oned_conf_path = get_oned_conf_path()
    oned_conf = load_file(file_path=oned_conf_path, mode="rt", encoding="utf-8")
    match = re.search(r"^\s*MONITORING_INTERVAL_MARKET\s*=\s*\"?(\d+)\"?", oned_conf, re.MULTILINE)
    if match is None:
        msg("error", "Could not find MONITORING_INTERVAL_MARKET in oned.conf")
    data = int(match.group(1))
    msg("info", f"OpenNebula current marketplace monitoring interval set to {data} seconds")
    return data
    
def update_marketplace_monitoring_interval(interval: int) -> None:
    """
    Update the monitoring interval of the marketplace
    
    :param interval: the interval in seconds, ``int``
    """
    msg("info", f"Updating OpenNebula marketplace monitoring interval to {interval} seconds")
    oned_conf_path = get_oned_conf_path()
    oned_conf = load_file(file_path=oned_conf_path, mode="rt", encoding="utf-8")
    pattern = r"^\s*MONITORING_INTERVAL_MARKET\s*=\s*\"?(\d+)\"?"
    updated_conf = re.sub(pattern, f"MONITORING_INTERVAL_MARKET = {interval}", oned_conf, flags=re.MULTILINE)
    save_file(data=updated_conf, file_path=oned_conf_path, mode="w", encoding="utf-8")
    msg("info", "OpenNebula marketplace monitoring interval updated")

## APPLIANCE MANAGEMENT ##
def get_appliance(appliance_name: str, marketplace_name: str) -> dict:
    """
    Get the details of an appliance in OpenNebula
    
    :param appliance_name: the name of the appliance, ``str``
    :param marketplace_id: the id of the marketplace, ``int``
    :return: the details of the appliance, ``dict``
    """
    msg("info", f"Getting appliance {appliance_name}")
    res = run_command(f"onemarketapp show \"{appliance_name}\" -j")
    if res["rc"] != 0:
        msg("info", "Appliance not found")
        return None
    msg("info", "Appliance found")
    appliance = loads_json(data=res["stdout"])
    if appliance["MARKETPLACEAPP"]["MARKETPLACE"] != marketplace_name:
        msg("info", f"Appliance {appliance_name} not in {marketplace_name} marketplace")
        return None
    msg("info", f"Appliance {appliance_name} in {marketplace_name} marketplace")
    return appliance

def get_appliance_id(appliance_name: str, marketplace_name: str) -> int:
    """
    Get the id of an appliance in OpenNebula
    
    :param appliance_name: the name of the appliance, ``str``
    :param marketplace_name: the name of the marketplace, ``int``
    :return: the id of the appliance, ``int``
    """
    appliance = get_appliance(appliance_name, marketplace_name)
    if appliance is None:
        return None
    return int(appliance["MARKETPLACEAPP"]["ID"])

def get_type_appliance(appliance_name: str, marketplace_name: str) -> str:
    """
    Get the type of an appliance in OpenNebula
    
    :param appliance_name: the name of the appliance, ``str``
    :param marketplace_name: the name of the marketplace, ``int``
    :return: the type of the appliance, ``str``
    """
    msg("info", f"Getting type of appliance {appliance_name}")
    appliance = get_appliance(appliance_name, marketplace_name)
    if appliance is None:
        return None
    appliance_type = appliance["MARKETPLACEAPP"]["TYPE"]
    if appliance_type == "1":
        msg("info", "Appliance type is IMAGE")
        return "IMAGE"
    elif appliance_type == "2":
        msg("info", "Appliance type is VM")
        return "VM"
    elif appliance_type == "3":
        msg("info", "Appliance type is SERVICE")
        return "SERVICE"
    else:
        msg("error", "Appliance type not recognized")

def get_appliances_oneadmin() -> dict:
    """
    Get the appliances of oneadmin user in OpenNebula
        
    :return: the appliances, ``dict``
    """
    oneadmin_id = get_username_id(username="oneadmin")
    res = run_command(f"onemarketapp list {oneadmin_id} -j")
    if res["rc"] != 0:
        return None
    return loads_json(data=res["stdout"])

def get_appliances_marketplace(marketplace_name: str) -> list:
    """
    Get the appliances from a marketplace in OpenNebula
    
    :param marketplace_name: the name of the market, ``str``
    :return: list of appliances, ``list``
    """
    oneadmin_appliances = get_appliances_oneadmin()
    if oneadmin_appliances is None:
        return None
    appliances = oneadmin_appliances["MARKETPLACEAPP_POOL"]["MARKETPLACEAPP"]
    return [appliance["NAME"] for appliance in appliances if appliance["MARKETPLACE"] == marketplace_name]
    
def export_appliance(appliance_name: str, datastore_id: int) -> None:
    """
    Export an appliance from OpenNebula
    
    :param appliance_name: the name of the appliance, ``str``
    :param datastore_id: the datastore where the appliance is stored, ``int``
    """
    msg("info", f"Exporting appliance {appliance_name} in datastore {datastore_id}")
    res = run_command(f"onemarketapp export \"{appliance_name}\" \"{appliance_name}\" -d {datastore_id}")
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
    msg("info", "Appliance exported")
    return image_ids, template_ids, service_id

def add_appliances_from_marketplace(sixg_sandbox_group: str, jenkins_user: str, marketplace_name: str, appliances: list) -> None:
    """
    Add appliances from a marketplace to the local OpenNebula

    :param sixg_sandbox_group: the name of the 6G-SANDBOX group, ``str``
    :param jenkins_user: the name of the Jenkins user, ``str``
    :param marketplace_name: the name of the marketplace, ``str``
    :param appliances: the list of appliances to add, ``list``
    """
    for appliance_name in appliances:
        appliance_type = get_type_appliance(appliance_name=appliance_name, marketplace_name=marketplace_name)
        if appliance_type == "IMAGE":
            if get_image(appliance_name) is None:
                onedatastores = get_onedatastores()
                datastore = ask_select(prompt="Select the datastore where you want to store the image", choices=onedatastores)
                datastore_id = get_onedatastore_id(datastore)
                image_id, template_id, _ = export_appliance(appliance_name=appliance_name, datastore_id=datastore_id)
                sleep(10)
                rename_image(image_id=image_id[0], new_name=appliance_name)
                while get_state_image(appliance_name) != "1":
                    sleep(10)
                chown_image(image_id=image_id[0], username=jenkins_user, group_name=sixg_sandbox_group)
                chown_template(template_id=template_id[0], username=jenkins_user, group_name=sixg_sandbox_group)
        elif appliance_type == "VM":
            if get_template(appliance_name) is None:
                onedatastores = get_onedatastores()
                datastore = ask_select(prompt="Select the datastore where you want to store the image", choices=onedatastores)
                datastore_id = get_onedatastore_id(datastore)
                image_ids, template_id, _ = export_appliance(appliance_name=appliance_name, datastore_id=datastore_id)
                sleep(10)
                for i, image_id in enumerate(image_ids):
                    rename_image(image_id=image_id, new_name=f"{appliance_name}-{i}")
                    chown_image(image_id=image_id, username=jenkins_user, group_name=sixg_sandbox_group)
                for i, image_id in enumerate(image_ids):
                    while get_state_image(f"{appliance_name}-{i}") != "1":
                        sleep(10)
                chown_template(template_id=template_id[0], username=jenkins_user, group_name=sixg_sandbox_group)
        else:
            if get_oneflow_template(appliance_name) is None:
                onedatastores = get_onedatastores()
                datastore = ask_select(prompt="Select the datastore where you want to store the image", choices=onedatastores)
                datastore_id = get_onedatastore_id(datastore)
                image_ids, template_ids, service_id = export_appliance(appliance_name=appliance_name, datastore_id=datastore_id)
                sleep(10)
                for i, image_id in enumerate(image_ids):
                    rename_image(image_id=image_id, new_name=f"{appliance_name}-{i}")
                    chown_image(image_id=image_id, username=jenkins_user, group_name=sixg_sandbox_group)
                for i, image_id in enumerate(image_ids):
                    while get_state_image(f"{appliance_name}-{i}") != "1":
                        sleep(10)
                for template_id in template_ids:
                    chown_template(template_id=template_id, username=jenkins_user, group_name=sixg_sandbox_group)
                chown_oneflow_template(service_id=service_id, username=jenkins_user, group_name=sixg_sandbox_group)

## SERVICE MANAGEMENT ##
def restart_one() -> None:
    """
    Restart the OpenNebula daemon
    """
    msg("info", "Restarting OpenNebula daemon")
    res = run_command("systemctl restart opennebula")
    if res["rc"] != 0:
        msg("error", "Could not restart the OpenNebula daemon")
    msg("info", "OpenNebula daemon restarted")

## HEALTH MANAGEMENT ##
def check_one_health() -> None:
    """
    Check the health of OpenNebula
    """
    msg("info", "Checking OpenNebula health")
    get_groups()
    get_users()
    get_vms()
    get_onedatastores()
    get_oneflows()
    get_onemarkets()
    get_onegate_endpoint()
    msg("info", "OpenNebula healthcheck passed")