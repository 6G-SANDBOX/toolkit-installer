import os
import re

from time import sleep
from textwrap import dedent
from typing import Dict, List, Optional, Tuple

from utils.cli import run_command
from utils.file import load_file, loads_json, save_file
from utils.questionary import ask_select
from utils.logs import msg
from utils.temp import save_temp_file

## CONFIG MANAGEMENT ##
def get_oned_conf_path() -> str:
    """
    Get the path to the oned.conf file
    
    :return: the path to the oned.conf file, ``str``
    """
    msg(level="debug", message="Getting OpenNebula oned.conf path")
    return os.path.join("/etc", "one", "oned.conf")

## ONEGATE MANAGEMENT ##
# def get_onegate_endpoint() -> Dict:
#     oned_conf_path = get_oned_conf_path()
#     oned_conf = load_file(file_path=oned_conf_path)
#     match = re.search(r"^\s*ONEGATE_ENDPOINT\s*=\s*\"([^\"]+)\"", oned_conf, re.MULTILINE)
#     if match is None:
#         msg("error", "Could not find ONEGATE_ENDPOINT in oned.conf")
#     url = match.group(1)
#     ip_match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", url)
#     if ip_match is None:
#         msg("error", "Could not extract IP from ONEGATE_ENDPOINT")
#     return ip_match.group(1)

## RESIZE DISK ##
# def resize_disk(vm_name: str, disk_id: int, size: int) -> None:
#     """
#     Resize the disk of a VM in OpenNebula

#     :param vm_name: the name of the VM, ``str``
#     :param disk_id: the id of the disk, ``int``
#     :param size: the new size of the disk, ``int``
#     """
#     res = run_command(f"onevm disk-resize \"{vm_name}\" {disk_id} {size}G")
#     if res["rc"] != 0:
#         msg("error", res["stderr"])

## NETWORKS MANAGEMENT ##
# def get_vnets() -> dict:
#     """
#     Get the list of VNets in OpenNebula
    
#     :return: the list of VNets, ``dict``
#     """
#     res = run_command("onevnet list -j")
#     if res["rc"] != 0:
#         return None
#     return loads_json(data=res["stdout"])

# def get_vnets_names() -> list:
#     """
#     Get the names of the VNets in OpenNebula
    
#     :return: the names of the VNets, ``list``
#     """
#     vnets = get_vnets()
#     if vnets is None:
#         return None
#     return [vnet["NAME"] for vnet in vnets["VNET_POOL"]["VNET"]]

# def get_vnet(vnet_name: str) -> dict:
#     """
#     Get the details of a VNet in OpenNebula
    
#     :param vnet_name: the name of the VNet, ``str``
#     :return: the details of the VNet, ``dict``
#     """
#     res = run_command(f"onevnet show \"{vnet_name}\" -j")
#     if res["rc"] != 0:
#         return None
#     return loads_json(data=res["stdout"])

# def get_vnet_id(vnet_name: str) -> int:
#     """
#     Get the ID of a VNet in OpenNebula
    
#     :param vnet_name: the name of the VNet, ``str``
#     :return: the id of the VNet, ``int``
#     """
#     vnet = get_vnet(vnet_name)
#     if vnet is None:
#         return None
#     return int(vnet["VNET"]["ID"])

## VM MANAGEMENT ##
# def get_vms() -> dict:
#     """
#     Get the list of VMs in OpenNebula
    
#     :return: the list of VMs, ``dict``
#     """
#     res = run_command("onevm list -j")
#     if res["rc"] != 0:
#         msg("error", res["stderr"])
#     return loads_json(data=res["stdout"])

# def get_vm(vm_name: str) -> dict:
#     """
#     Get the details of a VM in OpenNebula
    
#     :param vm_name: the name of the VM, ``str``
#     :return: the details of the VM, ``dict``
#     """
#     msg("info", f"Getting OpenNebula VM: {vm_name}")
#     res = run_command(f"onevm show \"{vm_name}\" -j")
#     if res["rc"] != 0:
#         msg("info", "VM not found")
#         return None
#     msg("info", "VM found")
#     return loads_json(data=res["stdout"])

# def chown_vm(vm_id: int, username: str, group_name: str) -> None:
#     """
#     Change the owner of a VM in OpenNebula
    
#     :param vm_id: the id of the VM, ``int``
#     :param username: the name of the user, ``str``
#     :param group_name: the name of the group, ``str``
#     """
#     msg("info", f"Changing owner of OpenNebula VM {vm_id} to {username}:{group_name}")
#     res = run_command(f"onevm chown {vm_id} \"{username}\" \"{group_name}\"")
#     if res["rc"] != 0:
#         msg("error", res["stderr"])
#     msg("info", "Owner of VM changed")

# def get_vm_ip(vm_name: str) -> str:
#     """
#     Get the IP of a VM in OpenNebula
    
#     :param vm_name: the name of the VM, ``str``
#     :return: the id of the VM, ``str``
#     """
#     vm = get_vm(vm_name)
#     msg("info", f"Getting IP of OpenNebula VM {vm_name}")
#     if vm is None:
#         return None
#     vm_ip = vm["VM"]["TEMPLATE"]["NIC"][0]["IP"]
#     msg("info", f"IP of VM {vm_name} is {vm_ip}")
#     return vm_ip

## DATASTORE MANAGEMENT ##
def onedatastore_list() -> Dict:
    """
    Get the list of datastores in OpenNebula
    
    :return: the list of datastores, ``Dict``
    """
    command = "onedatastore list -j"
    stdout, _, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"OpenNebula datastores not found. Create a datastore in OpenNebula before adding an appliance. Command executed: {command}")
    else:
        msg(level="debug", message=f"OpenNebula datastores found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        return loads_json(data=stdout)

def get_datastores_names() -> List[str]:
    """
    Get the names of the datastores in OpenNebula
    
    :return: the names of the datastores, ``List[str]``
    """
    datastores = onedatastore_list()
    datastores_names = []
    if "DATASTORE_POOL" not in datastores or "DATASTORE" not in datastores["DATASTORE_POOL"]:
        msg(level="error", message="DATASTORE_POOL key not found in datastores or DATASTORE key not found in DATASTORE_POOL")
    for datastore in datastores["DATASTORE_POOL"]["DATASTORE"]:
        if datastore is None:
            msg(level="error", message="Datastore is empty")
        if "NAME" not in datastore:
            msg(level="error", message=f"NAME key not found in datastore {datastore}")
        datastores_names.append(datastore["NAME"])
    return datastores_names

## ONEFLOW MANAGEMENT ##
# def get_oneflows() -> dict:
#     """
#     Get the list of services in OpenNebula
    
#     :return: the list of services, ``dict``
#     """
#     res = run_command("oneflow list -j")
#     if res["rc"] != 0:
#         return None
#     return loads_json(data=res["stdout"])

# def oneflow_show(oneflow_name: str) -> Dict:
#     """
#     Get the details of a service instantiated in OpenNebula
    
#     :param oneflow_name: the name of the service, ``str``
#     :return: the details of the service, ``Dict``
#     """
#     command = f"oneflow show \"{oneflow_name}\" -j"
#     stdout, _, rc = run_command(command=command)
#     if rc != 0:
#         msg(level="debug", message=f"Service {oneflow_name} not found. Command executed: {command}")
#         return None
#     else:
#         msg(level="debug", message=f"Service {oneflow_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
#         return loads_json(data=stdout)

# def get_oneflow_roles(oneflow_name: str) -> dict:
#     """
#     Get the roles of a service in OpenNebula
    
#     :param oneflow_name: the name of the service, ``str``
#     :return: the roles of the service, ``dict``
#     """
#     msg("info", f"Getting roles of OpenNebula service {oneflow_name}")
#     oneflow = oneflow_show(oneflow_name)
#     if oneflow is None:
#         return None
#     msg("info", "Roles found")
#     return oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["roles"]

# def get_oneflow_custom_attrs_values(oneflow_name: str) -> dict:
#     """
#     Get the custom_attrs of a service in OpenNebula
    
#     :param oneflow_name: the name of the service, ``str``
#     :return: the custom_attrs of the service, ``dict``
#     """
#     oneflow = get_oneflow(oneflow_name)
#     if oneflow is None:
#         return None
#     return oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["custom_attrs_values"]

# def rename_oneflow(oneflow_id: int, new_name: str) -> None:
#     """
#     Rename a service in OpenNebula
    
#     :param oneflow_id: the id of the service, ``int``
#     :param new_name: the new name of the service, ``str``
#     """
#     res = run_command(f"oneflow rename {oneflow_id} \"{new_name}\"")
#     if res["rc"] != 0:
#         msg("error", res["stderr"])

# def chown_oneflow(oneflow_id: int, username: str, group_name: str) -> None:
#     """
#     Change the owner of a service in OpenNebula
    
#     :param oneflow_id: the id of the service, ``int``
#     :param user_id: the name of the user, ``str``
#     :param group_id: the id of the group, ``str``
#     """
#     msg("info", f"Changing owner of OpenNebula service {oneflow_id} to {username}:{group_name}")
#     res = run_command(f"oneflow chown {oneflow_id} \"{username}\" \"{group_name}\"")
#     if res["rc"] != 0:
#         msg("error", res["stderr"])
#    msg("info", "Owner of service changed")

## ONEFLOW TEMPLATE MANAGEMENT ##
def oneflow_template_show(oneflow_template_name: str) -> Dict | None:
    """
    Get the details of a service in OpenNebula
    
    :param oneflow_template_name: the name of the service, ``str``
    :return: the details of the service, ``Dict``
    """
    command = f"oneflow-template show \"{oneflow_template_name}\" -j"
    stdout, _, rc = run_command(command=command)
    if rc != 0:
        msg(level="debug", message=f"Service {oneflow_template_name} not found. Command executed: {command}")
        return None
    else:
        msg(level="debug", message=f"Service {oneflow_template_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        return loads_json(data=stdout)

def get_oneflow_template_roles(oneflow_template_name: str) -> List[Dict]:
    """
    Get the roles of a service in OpenNebula
    
    :param oneflow_template_name: the name of the service, ``str``
    :return: the roles of the service, ``List[Dict]``
    """
    oneflow_template = oneflow_template_show(oneflow_template_name=oneflow_template_name)
    if oneflow_template is None:
        msg(level="error", message=f"Service {oneflow_template_name} not found")
    if "DOCUMENT" not in oneflow_template or "TEMPLATE" not in oneflow_template["DOCUMENT"] or "BODY" not in oneflow_template["DOCUMENT"]["TEMPLATE"]:
        msg(level="error", message=f"DOCUMENT key not found in service {oneflow_template_name} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE")
    oneflow_template_roles = oneflow_template["DOCUMENT"]["TEMPLATE"]["BODY"]["roles"]
    if oneflow_template_roles is None:
        msg(level="error", message=f"Could not get roles of service {oneflow_template_name}")
    return oneflow_template_roles

def get_oneflow_template_ids(oneflow_template_name: str) -> List[int]:
    """
    Get the template ids of a service in OpenNebula

    :param oneflow_template_name: the name of the service, ``str``
    :return: the template ids of the service, ``List[int]``
    """
    oneflow_template = get_oneflow_template_roles(oneflow_template_name=oneflow_template_name)
    oneflow_template_ids = []
    for role in oneflow_template:
        if "vm_template" not in role:
            msg(level="error", message="vm_template key not found in role")
        oneflow_template_ids.append(int(role["vm_template"]))
    return oneflow_template_ids

def get_oneflow_image_ids(oneflow_template_name: str) -> List[int]:
    """
    Get the image ids of a service in OpenNebula

    :param oneflow_template_name: the name of the service, ``str``
    :return: the image ids of the service, ``List[int]``
    """
    template_ids = get_oneflow_template_ids(oneflow_template_name=oneflow_template_name)
    oneflow_image_ids = []
    for template_id in template_ids:
        image_ids = get_template_image_ids(template_id=template_id)
        oneflow_image_ids.extend(image_ids)
    return oneflow_image_ids

def get_oneflow_template_custom_attrs(oneflow_template_name: str) -> Dict | None:
    """
    Get the custom_attrs key of a service in OpenNebula
    
    :param oneflow_template_name: the name of the service, ``str``
    :return: the custom_attrs key of the service, ``Dict``
    """
    oneflow_template = oneflow_template_show(oneflow_template_name=oneflow_template_name)
    if oneflow_template is None:
        msg(level="error", message=f"Service {oneflow_template_name} not found")
    if "DOCUMENT" not in oneflow_template or "TEMPLATE" not in oneflow_template["DOCUMENT"] or "BODY" not in oneflow_template["DOCUMENT"]["TEMPLATE"]:
        msg(level="error", message=f"DOCUMENT key not found in service {oneflow_template_name} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE")
    if "custom_attrs" not in oneflow_template["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(level="error", message=f"custom_attrs key not found in service {oneflow_template_name}")
    custom_attrs = oneflow_template["DOCUMENT"]["TEMPLATE"]["BODY"]["custom_attrs"]
    if custom_attrs is None:
        return None
    return custom_attrs

# def get_oneflow_template_networks(oneflow_template_name: str) -> dict:
#     """
#     Get the networks of a service in OpenNebula
    
#     :param oneflow_template_name: the name of the service, ``str``
#     :return: the networks of the service, ``dict``
#     """
#     msg("info", f"Getting networks of OpenNebula service {oneflow_template_name}")
#     oneflow_template = get_oneflow_template(oneflow_template_name)
#     if oneflow_template is None:
#         return None
#     networks = oneflow_template["DOCUMENT"]["TEMPLATE"]["BODY"]["networks"]
#     msg("info", "Networks found")
#     return networks

# def instantiate_oneflow_template(oneflow_template_name: str, file_path: str) -> None:
#     """
#     Instantiate a service in OpenNebula
    
#     :param oneflow_template_id: the id of the service, ``int``
#     :param file_path: the path to the file with params, ``str``
#     """
#     msg("info", f"Instantiating OpenNebula service {oneflow_template_name}")
#     res = run_command(f"oneflow-template instantiate \"{oneflow_template_name}\" < {file_path}")
#     if res["rc"] != 0:
#         msg("error", res["stderr"])
#     msg("info", "Service instantiated")
#     return int(re.search(r"ID:\s*(\d+)", res["stdout"]).group(1))

# def update_oneflow_template(oneflow_template_name: str, file_path: str) -> None:
#     """
#     Update a service in OpenNebula
    
#     :param oneflow_template_name: the name of the service, ``str``
#     :param file_path: the path to the file with params, ``str``
#     """
#     msg("info", f"Updating OpenNebula service {oneflow_template_name}")
#     res = run_command(f"oneflow-template update \"{oneflow_template_name}\" {file_path}")
#     if res["rc"] != 0:
#         msg("error", res["stderr"])
#     msg("info", "Service updated")

def oneflow_template_chown(oneflow_template_name: str, username: str, group_name: str) -> None:
    """
    Change the owner of a service in OpenNebula
    
    :param oneflow_template_name: the name of the service, ``str``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f"oneflow-template chown \"{oneflow_template_name}\" \"{username}\" \"{group_name}\""
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not change owner of service {oneflow_template_name} to {username}:{group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Owner of service {oneflow_template_name} changed to {username}:{group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

## GROUP MANAGEMENT ##
def onegroup_show(group_name: str) -> Dict | None:
    """
    Get the details of a group in OpenNebula

    :param group_name: the name of the group, ``str``
    :return: the details of the group, ``Dict``
    """
    command = f"onegroup show \"{group_name}\" -j"
    stdout, _, rc = run_command(command=command)
    if rc != 0:
        msg(level="debug", message=f"Group {group_name} not found. Command executed: {command}")
        return None
    else:
        msg(level="debug", message=f"Group {group_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        return loads_json(data=stdout)

def get_group_id(group_name: str) -> int:
    """
    Get the id of a group in OpenNebula
    
    :param group_name: the name of the group, ``str``
    :return: the id of the group, ``int``
    """
    group = onegroup_show(group_name=group_name)
    if group is None:
        msg(level="error", message=f"Group {group_name} not found")
    if "GROUP" not in group or "ID" not in group["GROUP"]:
        msg(level="error", message=f"GROUP key not found in group {group_name} or ID key not found in GROUP")
    group_id = group["GROUP"]["ID"]
    if group_id is None:
        msg(level="error", message=f"Could not get id of group {group_name}")
    return int(group_id)
    
def onegroup_list() -> Dict | None:
    """
    Get the list of groups in OpenNebula
    
    :return: the list of groups, ``Dict``
    """
    command = "onegroup list -j"
    stdout, _, rc = run_command(command=command)
    if rc != 0:
        msg(level="debug", message=f"OpenNebula groups not found. Command executed: {command}")
        return None
    else:
        msg(level="debug", message=f"OpenNebula groups found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        return loads_json(data=stdout)

def get_groups_names() -> List[str]:
    """
    Get the list of groups names in OpenNebula
    
    :return: the list of groups names, ``List[str]``
    """
    groups = onegroup_list()
    groups_names = []
    if groups is None:
        return []
    if "GROUP_POOL" not in groups or "GROUP" not in groups["GROUP_POOL"]:
        msg(level="error", message="GROUP_POOL key not found in groups or GROUP key not found in GROUP_POOL")
    for group in groups["GROUP_POOL"]["GROUP"]:
        if group is None:
            msg(level="error", message="Group is empty")
        if "NAME" not in group:
            msg(level="error", message=f"NAME key not found in group {group}")
        groups_names.append(group["NAME"])
    return groups_names

def onegroup_create(group_name: str) -> int:
    """
    Create a group in OpenNebula
    
    :param group_name: the name of the group, ``str``
    :return: the id of the group, ``int``
    """
    command = f"onegroup create \"{group_name}\""
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not create group {group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Group {group_name} created. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
    return re.search(r"ID:\s*(\d+)", stdout).group(1)

def check_group_admin(username: str, group_name: str) -> bool:
    """
    Check if user is admin of group in OpenNebula
    
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    :return: if user is admin of group, ``bool``
    """
    group = onegroup_show(group_name=group_name)
    if group is None:
        msg(level="error", message=f"Group {group_name} not found")
    if "GROUP" not in group or "ADMINS" not in group["GROUP"]:
        msg(level="error", message=f"GROUP key not found in group {group_name} or ADMINS key not found in GROUP")
    if "ID" not in group["GROUP"]["ADMINS"]:
        return False
    elif isinstance(group["GROUP"]["ADMINS"]["ID"], str):
        user = get_username(user_id=int(group["GROUP"]["ADMINS"]["ID"]))
        return user == username
    elif isinstance(group["GROUP"]["ADMINS"]["ID"], List):
        for user_id in group["GROUP"]["ADMINS"]["ID"]:
            user = get_username(user_id=int(user_id))
            if user == username:
                return True
    else:
        msg(level="error", message=f"ADMINS key not found in group {group_name}")
    return False

def onegroup_addadmin(username: str, group_name: str) -> None:
    """
    Assign user as admin to group in OpenNebula
    
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    if check_group_admin(username=username, group_name=group_name):
        msg(level="debug", message=f"User {username} is already admin of group {group_name}")
    else:
        command = f"onegroup addadmin \"{group_name}\" \"{username}\""
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(level="error", message=f"Could not assign user {username} as admin to group {group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
        msg(level="debug", message=f"User {username} assigned as admin to group {group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def oneacl_list() -> Dict | None:
    """
    Get the list of ACLs in OpenNebula
    
    :return: the list of ACLs, ``Dict``
    """
    command = "oneacl list -j"
    stdout, _, rc = run_command(command=command)
    if rc != 0:
        msg(level="debug", message=f"OpenNebula ACLs not found. Command executed: {command}")
        return None
    else:
        msg(level="debug", message=f"OpenNebula ACLs found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        return loads_json(data=stdout)

def check_group_acl(group_id: str, resources: str, rights: str) -> bool:
    """
    Check if group has ACL in OpenNebula
    
    :param group_id: the id of the group, ``int``
    :param resources: the resources to check, ``str``
    :param rights: the rights to check, ``str``
    :return: if group has ACL, ``bool``
    """
    acls = oneacl_list()
    if acls is None:
        return False
    if "ACL_POOL" not in acls or "ACL" not in acls["ACL_POOL"]:
        msg(level="error", message="ACL_POOL key not found in acls or ACL key not found in ACL_POOL")
    acl_pool = acls["ACL_POOL"]["ACL"]
    if acl_pool is None:
        return False
    for acl in acl_pool:
        if acl is None:
            msg(level="error", message="ACL is empty")
        if "STRING" not in acl:
            msg(level="error", message="STRING key not found in acl")
        acl_string = f"@{group_id} {resources} {rights}"
        print(acl_string)
        print(acl["STRING"])
        if acl_string == acl["STRING"]:
            return True
    return False

def oneacl_create(group_id: int, resources: str, rights: str) -> None:
    """
    Add an ACL to a group in OpenNebula
    
    :param group_id: the id of the group, ``int``
    :param resources: the resources to add, ``str``
    :param rights: the rights to add, ``str``
    """
    if check_group_acl(group_id=group_id, resources=resources, rights=rights):
        msg(level="debug", message=f"Group with id {group_id} already has ACL. Resources: {resources}. Rights: {rights}")
    else:
        command = f"oneacl create \"@{group_id} {resources} {rights}\""
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(level="error", message=f"Could not add ACL to group. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
        msg(level="debug", message=f"ACL added to group. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        return int(re.search(r"ID:\s*(\d+)", stdout).group(1))

## USER MANAGEMENT ##
def oneuser_show(username: Optional[str] = None, user_id: Optional[int] = None) -> Dict | None:
    """
    Get the details of an user in OpenNebula

    :param username: the name of the user, ``str``
    :param user_id: the id of the user, ``int``
    :return: the details of the user, ``Dict``
    """
    if username is None and user_id is None:
        msg(level="error", message="Either username or user_id must be provided")
    if username is not None and user_id is not None:
        msg(level="error", message="Either username or user_id must be provided, not both")
    if username is None:
        command = f"oneuser show {user_id} -j"
        stdout, _, rc = run_command(command=command)
        if rc != 0:
            msg(level="debug", message=f"User with id {user_id} not found. Command executed: {command}")
            return None
        else:
            msg(level="debug", message=f"User with id {user_id} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
            return loads_json(data=stdout)
    else:
        command = f"oneuser show \"{username}\" -j"
        stdout, _, rc = run_command(command=command)
        if rc != 0:
            msg(level="debug", message=f"User {username} not found. Command executed: {command}")
            return None
        else:
            msg(level="debug", message=f"User {username} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
            return loads_json(data=stdout)

def get_username_id(username: str) -> int:
    """
    Get the id of an user in OpenNebula

    :param username: the name of the user, ``str``
    :return: the id of the user, ``int``
    """
    user = oneuser_show(username=username)
    if user is None:
        msg(level="error", message=f"User {username} not found")
    if "USER" not in user or "ID" not in user["USER"]:
        msg(level="error", message=f"USER key not found in user {username} or ID key not found in USER")
    user_id = user["USER"]["ID"]
    if user_id is None:
        msg(level="error", message=f"Could not get id of user {username}")
    return int(user_id)

def get_username(user_id: int) -> str:
    """
    Get the name of an user in OpenNebula
    
    :param user_id: the id of the user, ``int``
    :return: the name of the user, ``str``
    """
    user = oneuser_show(user_id=user_id)
    if user is None:
        msg(level="error", message=f"User with id {user_id} not found")
    if "USER" not in user or "NAME" not in user["USER"]:
        msg(level="error", message=f"USER key not found in user id {user_id} or NAME key not found in USER")
    username = user["USER"]["NAME"]
    if username is None:
        msg(level="error", message=f"Could not get name of user with id {user_id}")
    return username

def oneuser_list() -> Dict | None:
    """
    Get the list of users in OpenNebula
    
    :return: the list of users, ``Dict``
    """
    command = "oneuser list -j"
    stdout, _, rc = run_command(command=command)
    if rc != 0:
        msg(level="debug", message=f"OpenNebula users not found. Command executed: {command}")
        return None
    else:
        msg(level="debug", message=f"OpenNebula users found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        return loads_json(data=stdout)

def get_usernames() -> List[str]:
    """
    Get the list of usernames in OpenNebula
    
    :return: the list of usernames, ``List[str]``
    """
    users = oneuser_list()
    usernames = []
    if users is None:
        return []
    if "USER_POOL" not in users or "USER" not in users["USER_POOL"]:
        msg(level="error", message="USER_POOL key not found in users or USER key not found in USER_POOL")
    user_pool = users["USER_POOL"]["USER"]
    if user_pool is None:
        return []
    for user in user_pool:
        if user is None:
            msg(level="error", message="User is empty")
        if "NAME" not in user:
            msg(level="error", message="NAME key not found in user")
        usernames.append(user["NAME"])
    return usernames

def oneuser_create(username: str, password: str) -> int:
    """
    Create an user in OpenNebula
    
    :param username: the name of the user, ``str``
    :param password: the password of the user, ``str``
    :return: the id of the user, ``int``
    """
    command = f"oneuser create \"{username}\" \"{password}\""
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not create user {username} with password {password}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"User {username} created with password {password}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
    return re.search(r"ID:\s*(\d+)", stdout).group(1)

def oneuser_chgrp(username: str, group_name: str) -> None:
    """
    Assign user to group in OpenNebula
    
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f"oneuser chgrp \"{username}\" \"{group_name}\""
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not assign user {username} to group {group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"User {username} assigned to group {group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def oneuser_update_ssh_key(username: str, ssh_key: str) -> None:
    """
    Update the SSH key of an user in OpenNebula
    
    :param username: the name of the user, ``str``
    :param jenkins_ssh_key: the SSH key, ``str``
    """
    command = f"echo \'SSH_PUBLIC_KEY=\"{ssh_key}\"\' | oneuser update \"{username}\" --append"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not update SSH key of user {username} to {ssh_key}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"SSH key of user {username} updated to {ssh_key}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

## TEMPLATE MANAGEMENT ##
def onetemplate_show(template_name: Optional[str] = None, template_id: Optional[int] = None) -> Dict | None:
    """
    Get the details of a template in OpenNebula

    :param template_name: the name of the template, ``str``
    :param template_id: the id of the template, ``int``
    :return: the details of the template, ``Dict``
    """
    if template_id is None and template_name is None:
        msg(level="error", message="Either template_name or template_id must be provided")
    if template_id is not None and template_name is not None:
        msg(level="error", message="Either template_name or template_id must be provided, not both")
    if template_name is None:
        command = f"onetemplate show {template_id} -j"
        stdout, _, rc = run_command(command=command)
        if rc != 0:
            msg(level="debug", message=f"Template with id {template_id} not found. Command executed: {command}")
            return None
        else:
            msg(level="debug", message=f"Template with id {template_id} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
            return loads_json(data=stdout)
    else:
        command = f"onetemplate show \"{template_name}\" -j"
        stdout, _, rc = run_command(command=command)
        if rc != 0:
            msg(level="debug", message=f"Template {template_name} not found. Command executed: {command}")
            return None
        else:
            msg(level="debug", message=f"Template {template_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
            return loads_json(data=stdout)

def get_template_name(template_id: int) -> str:
    """
    Get the name of a template in OpenNebula
    
    :param template_id: the id of the template, ``int``
    :return: the name of the template, ``str``
    """
    template = onetemplate_show(template_id=template_id)
    if template is None:
        msg(level="error", message=f"Template with id {template_id} not found")
    if "VMTEMPLATE" not in template or "NAME" not in template["VMTEMPLATE"]:
        msg(level="error", message=f"VMTEMPLATE key not found in template id {template_id} or NAME key not found in VMTEMPLATE")
    template_name = template["VMTEMPLATE"]["NAME"]
    if template_name is None:
        msg(level="error", message=f"Could not get name of template with id {template_id}")
    return template_name

def get_template_image_ids(template_name: Optional[str] = None, template_id: Optional[int] = None) -> List[int]:
    """
    Get the image id of a template in OpenNebula
    
    :param template_name: the name of the template, ``str``
    :param template_id: the id of the template, ``int``
    :return: the list of image ids, ``List[int]``
    """
    if template_id is None and template_name is None:
        msg(level="error", message="Either template_name or template_id must be provided")
    if template_id is not None and template_name is not None:
        msg(level="error", message="Either template_name or template_id must be provided, not both")
    if template_id is None:
        template = onetemplate_show(template_name=template_name)
        if template is None:
            msg(level="error", message=f"Template {template_name} not found")
        if "VMTEMPLATE" not in template or "TEMPLATE" not in template["VMTEMPLATE"] or "DISK" not in template["VMTEMPLATE"]["TEMPLATE"]:
            msg(level="error", message=f"VMTEMPLATE key not found in template {template_name} or TEMPLATE key not found in VMTEMPLATE or DISK key not found in TEMPLATE")
        template_image_ids = template["VMTEMPLATE"]["TEMPLATE"]["DISK"]
        image_ids = []
        if template_image_ids is None:
            msg(level="error", message=f"Could not get image id of template {template_name}")
        elif isinstance(template_image_ids, Dict):
            if "IMAGE_ID" not in template_image_ids:
                msg(level="error", message="IMAGE_ID key not found in DISK")
            image_ids.append(int(template_image_ids["IMAGE_ID"]))
        elif isinstance(template_image_ids, List):
            for disk in template_image_ids:
                if "IMAGE_ID" not in disk:
                    msg(level="error", message="IMAGE_ID key not found in DISK")
                image_ids.append(int(disk["IMAGE_ID"]))
        else:
            msg(level="error", message="Invalid type of DISK")
        return image_ids
    else:
        template = onetemplate_show(template_id=template_id)
        if template is None:
            msg(level="error", message=f"Template with id {template_id} not found")
        if "VMTEMPLATE" not in template or "TEMPLATE" not in template["VMTEMPLATE"] or "DISK" not in template["VMTEMPLATE"]["TEMPLATE"]:
            msg(level="error", message=f"VMTEMPLATE key not found in template id {template_id} or TEMPLATE key not found in VMTEMPLATE or DISK key not found in TEMPLATE")
        template_image_ids = template["VMTEMPLATE"]["TEMPLATE"]["DISK"]
        image_ids = []
        if template_image_ids is None:
            msg(level="error", message=f"Could not get image id of template with id {template_id}")
        elif isinstance(template_image_ids, Dict):
            if "IMAGE_ID" not in template_image_ids:
                msg(level="error", message="IMAGE_ID key not found in DISK")
            image_ids.append(int(template_image_ids["IMAGE_ID"]))
        elif isinstance(template_image_ids, List):
            for disk in template_image_ids:
                if "IMAGE_ID" not in disk:
                    msg(level="error", message="IMAGE_ID key not found in DISK")
                image_ids.append(int(disk["IMAGE_ID"]))
        else:
            msg(level="error", message="Invalid type of DISK")
        return image_ids

def onetemplate_chown(template_name: str, username: str, group_name: str) -> None:
    """
    Change the owner of a template in OpenNebula
    
    :param template_name: the name of the template, ``str``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f"onetemplate chown \"{template_name}\" \"{username}\" \"{group_name}\""
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not change owner of template {template_name} to {username}:{group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Owner of template {template_name} changed to {username}:{group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

# def update_template(template_name: str, file_path: str) -> None:
#     """
#     Update a local template in OpenNebula
    
#     :param template_name: the name of the template, ``str``
#     :param file_path: the path with the data, ``str``
#     """
#     msg("info", f"Updating OpenNebula template: {template_name}")
#     res = run_command(f"onetemplate update -a \"{template_name}\" {file_path}")
#     if res["rc"] != 0:
#         msg("error", res["stderr"])
#     msg("info", "Template updated")

## IMAGES MANAGEMENT ##
def oneimage_show(image_name: Optional[str] = None, image_id: Optional[int] = None) -> Dict | None:
    """
    Get the details of an image in OpenNebula
    
    :param image_name: the name of the image, ``str``
    :param image_id: the id of the image, ``int``
    :return: the details of the image, ``Dict``
    """
    if image_id is None and image_name is None:
        msg(level="error", message="Either image_name or image_id must be provided")
    if image_id is not None and image_name is not None:
        msg(level="error", message="Either image_name or image_id must be provided, not both")
    if image_name is None:
        command = f"oneimage show {image_id} -j"
        stdout, _, rc = run_command(command=command)
        if rc != 0:
            msg(level="debug", message=f"Image with id {image_id} not found. Command executed: {command}")
            return None
        else:
            msg(level="debug", message=f"Image with id {image_id} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
            return loads_json(data=stdout)
    else:
        command = f"oneimage show \"{image_name}\" -j"
        stdout, _, rc = run_command(command=command)
        if rc != 0:
            msg(level="debug", message=f"Image {image_name} not found. Command executed: {command}")
            return None
        else:
            msg(level="debug", message=f"Image {image_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
            return loads_json(data=stdout)        

# def check_owner_image(username: str, image_name: str) -> bool:
#     """
#     Check if user is owner of image in OpenNebula
    
#     :param username: the name of the user, ``str``
#     :param image_name: the name of the image, ``str``
#     :return: if user is owner of image, ``bool``
#     """
#     image = oneimage_show(image_name=image_name)
#     if image is None:
#         msg(level="error", message=f"Image {image_name} not found")
#     if "IMAGE" not in image or "UNAME" not in image["IMAGE"]:
#         msg(level="error", message=f"IMAGE key not found in image {image_name} or UNAME key not found in IMAGE")
#     image_owner_name = image["IMAGE"]["UNAME"]
#     if image_owner_name is None:
#         return False
#     return image_owner_name == username

# def check_group_image(group_name: str, image_name: str) -> bool:
#     """
#     Check if group is owner of image in OpenNebula
    
#     :param group_name: the name of the group, ``str``
#     :param image_name: the name of the image, ``str``
#     :return: if group is owner of image, ``bool``
#     """
#     image = oneimage_show(image_name=image_name)
#     if image is None:
#         msg(level="error", message=f"Image {image_name} not found")
#     if "IMAGE" not in image or "GNAME" not in image["IMAGE"]:
#         msg(level="error", message=f"IMAGE key not found in image {image_name} or GNAME key not found in IMAGE")
#     image_group_name = image["IMAGE"]["GNAME"]
#     if image_group_name is None:
#         return False
#     return image_group_name == group_name

def get_image_name(image_id: int) -> str:
    """
    Get the name of an image in OpenNebula
    
    :param image_id: the id of the image, ``int``
    :return: the name of the image, ``str``
    """
    image = oneimage_show(image_id=image_id)
    if image is None:
        msg(level="error", message=f"Image with id {image_id} not found")
    if "IMAGE" not in image or "NAME" not in image["IMAGE"]:
        msg(level="error", message=f"IMAGE key not found in image id {image_id} or NAME key not found in IMAGE")
    image_name = image["IMAGE"]["NAME"]
    if image_name is None:
        msg(level="error", message=f"Could not get name of image with id {image_id}")
    return image_name

def get_image_state(image_name: str) -> str:
    """
    Get the status of an image in OpenNebula
    
    :param image_name: the name of the image, ``str``
    :return: the status of the image, ``str``
    """
    image = oneimage_show(image_name=image_name)
    if image is None:
        msg(level="error", message=f"Image {image_name} not found")
    if "IMAGE" not in image or "STATE" not in image["IMAGE"]:
        msg(level="error", message=f"Could not get state of image with name {image_name}")
    image_state = image["IMAGE"]["STATE"]
    if image_state is None:
        msg(level="error", message=f"Could not get state of image with name {image_name}")
    return image_state

def oneimage_chown(image_name: str, username: str, group_name: str) -> None:
    """
    Change the owner of an image in OpenNebula
    
    :param image_name: the name of the image, ``str``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f"oneimage chown \"{image_name}\" \"{username}\" \"{group_name}\""
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not change owner of image {image_name} to {username}:{group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Owner of image {image_name} changed to {username}:{group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

## MARKETPLACE MANAGEMENT ##
def onemarket_show(marketplace_name: str) -> Dict | None:
    """
    Get the details of a marketplace in OpenNebula
    
    :param marketplace_name: the name of the market, ``str``
    :return: the details of the marketplace, ``Dict``
    """
    command = f"onemarket show \"{marketplace_name}\" -j"
    stdout, _, rc = run_command(command=command)
    if rc != 0:
        msg(level="debug", message=f"Marketplace {marketplace_name} not found. Command executed: {command}")
        return None
    else:
        msg(level="debug", message=f"Marketplace {marketplace_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        return loads_json(data=stdout)

def get_marketplace_monitoring_interval() -> int:
    """
    Get the monitoring interval of the marketplace
    
    :return: the interval in seconds, ``int``
    """
    oned_conf_path = get_oned_conf_path()
    oned_conf = load_file(file_path=oned_conf_path)
    match = re.search(r"^\s*MONITORING_INTERVAL_MARKET\s*=\s*\"?(\d+)\"?", oned_conf, re.MULTILINE)
    if match is None:
        msg(level="error", message="Could not get marketplace monitoring interval")
    data = int(match.group(1))
    msg(level="debug", message=f"Marketplace monitoring interval is {data}")
    return data

def update_marketplace_monitoring_interval(interval: int) -> None:
    """
    Update the monitoring interval of the marketplace
    
    :param interval: the interval in seconds, ``int``
    """
    oned_conf_path = get_oned_conf_path()
    oned_conf = load_file(file_path=oned_conf_path)
    pattern = r"^\s*MONITORING_INTERVAL_MARKET\s*=\s*\"?(\d+)\"?"
    updated_conf = re.sub(pattern, f"MONITORING_INTERVAL_MARKET = {interval}", oned_conf, flags=re.MULTILINE)
    save_file(data=updated_conf, file_path=oned_conf_path)
    msg(level="debug", message=f"OpenNebula marketplace monitoring interval updated to {interval}")

def onemarket_create(
        marketplace_name: str,
        marketplace_description: str,
        marketplace_endpoint: str,
        marketplace_monitoring_interval: int
    ) -> int | None:
    """
    Add a marketplace in OpenNebula
    
    :param marketplace_name: the name of the marketplace, ``str``
    :param marketplace_description: the description of the marketplace, ``str``
    :param marketplace_endpoint: the endpoint of the marketplace, ``str``
    :param marketplace_monitoring_interval: the interval to refresh the marketplace, ``int``
    :return: the id of the marketplace, ``int``
    """
    marketplace = onemarket_show(marketplace_name=marketplace_name)
    if marketplace is None:
        marketplace_content = dedent(f"""
            NAME = "{marketplace_name}"
            DESCRIPTION = "{marketplace_description}"
            ENDPOINT = "{marketplace_endpoint}"
            MARKET_MAD = one
        """).strip()
        marketplace_content_path = save_temp_file(data=marketplace_content, file_path=f"{marketplace_name}_content")
        command = f"onemarket create {marketplace_content_path}"
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(level="error", message=f"Could not create marketplace {marketplace_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
        else:
            msg(level="debug", message=f"Marketplace {marketplace_name} created. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
            marketplace_old_monitoring_interval = get_marketplace_monitoring_interval()
            update_marketplace_monitoring_interval(interval=marketplace_monitoring_interval)
            restart_one()
            sleep(marketplace_monitoring_interval+5)
            check_one_health()
            update_marketplace_monitoring_interval(interval=marketplace_old_monitoring_interval)
            restart_one()
            check_one_health()
            return int(re.search(r"ID:\s*(\d+)", stdout).group(1))
    return None

## APPLIANCE MANAGEMENT ##
def get_appliance(appliance_name: str, marketplace_name: str) -> Dict:
    """
    Get the details of an appliance in OpenNebula
    
    :param appliance_name: the name of the appliance, ``str``
    :param marketplace_name: the name of the marketplace, ``str``
    :return: the details of the appliance, ``Dict``
    """
    command = f"onemarketapp show \"{appliance_name}\" -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not get appliance {appliance_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    else:
        msg(level="debug", message=f"OpenNebula appliance {appliance_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        appliance = loads_json(data=stdout)
        if "MARKETPLACEAPP" not in appliance or "MARKETPLACE" not in appliance["MARKETPLACEAPP"]:
            msg(level="error", message=f"MARKETPLACEAPP key not found in appliance {appliance_name} or MARKETPLACE key not found in MARKETPLACE")
        if appliance["MARKETPLACEAPP"]["MARKETPLACE"] != marketplace_name:
            msg(level="error", message=f"Appliance {appliance_name} not in {marketplace_name} marketplace")
        msg(level="debug", message=f"Appliance {appliance_name} found in {marketplace_name} marketplace")
        return appliance

def get_type_appliance(appliance_name: str, marketplace_name: str) -> str:
    """
    Get the type of an appliance in OpenNebula
    
    :param appliance_name: the name of the appliance, ``str``
    :param marketplace_name: the name of the marketplace, ``str``
    :return: the type of the appliance, ``str``
    """
    appliance = get_appliance(appliance_name=appliance_name, marketplace_name=marketplace_name)
    if "MARKETPLACEAPP" not in appliance or "TYPE" not in appliance["MARKETPLACEAPP"]:
        msg(level="error", message=f"MARKETPLACEAPP key not found in appliance {appliance_name} or TYPE key not found in MARKETPLACEAPP")
    appliance_type = appliance["MARKETPLACEAPP"]["TYPE"]
    if appliance_type == "1":
        msg(level="debug", message=f"Appliance {appliance_name} is an IMAGE")
        return "IMAGE"
    elif appliance_type == "2":
        msg(level="debug", message=f"Appliance {appliance_name} is a VM")
        return "VM"
    elif appliance_type == "3":
        msg(level="debug", message=f"Appliance {appliance_name} is a SERVICE")
        return "SERVICE"
    else:
        msg(level="error", message=f"Appliance {appliance_name} has unknown type")

# def get_appliances_oneadmin() -> dict:
#     """
#     Get the appliances of oneadmin user in OpenNebula
        
#     :return: the appliances, ``dict``
#     """
#     oneadmin_id = get_username_id(username="oneadmin")
#     res = run_command(f"onemarketapp list {oneadmin_id} -j")
#     if res["rc"] != 0:
#         return None
#     return loads_json(data=res["stdout"])

# def get_appliances_marketplace(marketplace_name: str) -> list:
#     """
#     Get the appliances from a marketplace in OpenNebula
    
#     :param marketplace_name: the name of the market, ``str``
#     :return: list of appliances, ``list``
#     """
#     oneadmin_appliances = get_appliances_oneadmin()
#     if oneadmin_appliances is None:
#         return None
#     appliances = oneadmin_appliances["MARKETPLACEAPP_POOL"]["MARKETPLACEAPP"]
#     return [appliance["NAME"] for appliance in appliances if appliance["MARKETPLACE"] == marketplace_name]
    
def onemarketapp_export(appliance_name: str, datastore_name: str) -> Tuple[List[int], List[int], int]:
    """
    Export an appliance in OpenNebula
    
    :param appliance_name: the name of the appliance, ``str``
    :param datastore_name: the name of the datastore, ``str``
    :return: the ids of the images, templates and services, ``Tuple[List[int], List[int], int]``
    """
    command = f"onemarketapp export \"{appliance_name}\" \"{appliance_name}\" --datastore \"{datastore_name}\""
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not export appliance {appliance_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Appliance {appliance_name} exported. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
    image_ids = [int(id_) for id_ in re.findall(r"ID:\s*(\d+)", re.search(r"IMAGE\s*\n((?:\s*ID:\s*\d+\s*\n?)*)", stdout).group(1))]
    template_ids = [int(id_) for id_ in re.findall(r"ID:\s*(\d+)", re.search(r"VMTEMPLATE\s*\n((?:\s*ID:\s*\d+\s*\n?)*)", stdout).group(1))]
    match = re.search(r"SERVICE_TEMPLATE\s*\n(?:\s*ID:\s*(\d+))+", stdout)
    if match:
        service_id = int(match.group(1))
        msg(level="debug", message=f"Appliance {appliance_name} exported with image ids {image_ids}, template ids {template_ids} and service id {service_id}")
    else:
        service_id = None
        msg(level="debug", message=f"Appliance {appliance_name} exported with image ids {image_ids} and template ids {template_ids}")
    return image_ids, template_ids, service_id

def onemarketapp_add(
        group_name: str,
        username: str,
        marketplace_name: str,
        appliances: List[str]
    ) -> None:
    """
    Add appliances from a marketplace in OpenNebula

    :param group_name: the name of the group, ``str``
    :param username: the name of the user, ``str``
    :param marketplace_name: the name of the marketplace, ``str``
    :param appliances: the list of appliances, ``List[str]``
    """
    for appliance_name in appliances:
        appliance_type = get_type_appliance(appliance_name=appliance_name, marketplace_name=marketplace_name)
        if appliance_type == "IMAGE": # one image and one template
            if oneimage_show(image_name=appliance_name) is None:
                datastores_names = get_datastores_names()
                datastore_name = ask_select(message=f"Select the datastore where you want to store the image {appliance_name}", choices=datastores_names)
                image_id, template_id, _ = onemarketapp_export(appliance_name=appliance_name, datastore_name=datastore_name)
                sleep(5)
                image_name = get_image_name(image_id=image_id[0])
                image_state = get_image_state(image_name=appliance_name)
                while image_state != "1":
                    sleep(10)
                    image_state = get_image_state(image_name=appliance_name)
                    if image_state == "5":
                        msg(level="error", message=f"Image {appliance_name} is in error state")
                template_name = get_template_name(template_id=template_id[0])
            oneimage_chown(image_name=appliance_name, username=username, group_name=group_name)
            onetemplate_chown(template_name=appliance_name, username=username, group_name=group_name)
        elif appliance_type == "VM": # one or more images and one template
            if onetemplate_show(template_name=appliance_name) is None:
                datastores_names = get_datastores_names()
                datastore_name = ask_select(message=f"Select the datastore where you want to store the template {appliance_name}", choices=datastores_names)
                _, template_id, _ = onemarketapp_export(appliance_name=appliance_name, datastore_name=datastore_name)
                sleep(5)
                image_ids = get_template_image_ids(template_name=appliance_name)
                for image_id in image_ids:
                    image_name = get_image_name(image_id=image_id)
                    oneimage_chown(image_name=image_name, username=username, group_name=group_name)
                    image_state = get_image_state(image_name=image_name)
                    while image_state != "1":
                        sleep(10)
                        image_state = get_image_state(image_name=image_name)
                        if image_state == "5":
                            msg(level="error", message=f"Image {image_name} is in error state")
                template_name = get_template_name(template_id=template_id[0])
                onetemplate_chown(template_name=template_name, username=username, group_name=group_name)
            else:
                image_ids = get_template_image_ids(template_name=appliance_name)
                for image_id in image_ids:
                    image_name = get_image_name(image_id=image_id)
                    oneimage_chown(image_name=image_name, username=username, group_name=group_name)
                onetemplate_chown(template_name=appliance_name, username=username, group_name=group_name)
        else:
            if oneflow_template_show(oneflow_template_name=appliance_name) is None:
                datastores_names = get_datastores_names()
                datastore_name = ask_select(message=f"Select the datastore where you want to store the service {appliance_name}", choices=datastores_names)
                _, template_ids, _ = onemarketapp_export(appliance_name=appliance_name, datastore_name=datastore_name)
                sleep(5)
                image_ids = get_oneflow_image_ids(oneflow_template_name=appliance_name)
                for image_id in image_ids:
                    image_name = get_image_name(image_id=image_id)
                    oneimage_chown(image_name=image_name, username=username, group_name=group_name)
                    image_state = get_image_state(image_name=image_name)
                    while image_state != "1":
                        sleep(10)
                        image_state = get_image_state(image_name=image_name)
                        if image_state == "5":
                            msg(level="error", message=f"Image {image_name} is in error state")
                for template_id in template_ids:
                    template_name = get_template_name(template_id=template_id)
                    onetemplate_chown(template_name=template_name, username=username, group_name=group_name)
            else:
                image_ids = get_oneflow_image_ids(oneflow_template_name=appliance_name)
                template_ids = get_oneflow_template_ids(oneflow_template_name=appliance_name)
                for image_id in image_ids:
                    image_name = get_image_name(image_id=image_id)
                    oneimage_chown(image_name=image_name, username=username, group_name=group_name)
                for template_id in template_ids:
                    template_name = get_template_name(template_id=template_id)
                    onetemplate_chown(template_name=template_name, username=username, group_name=group_name)
            oneflow_template_chown(oneflow_template_name=appliance_name, username=username, group_name=group_name)

## SERVICE MANAGEMENT ##
def restart_one() -> None:
    """
    Restart the OpenNebula daemon
    """
    command = "systemctl restart opennebula"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not restart OpenNebula daemon. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"OpenNebula daemon restarted. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

## HEALTH MANAGEMENT ##
def check_one_health() -> None:
    """
    Check OpenNebula health
    """
    command = "systemctl list-units | grep opennebula"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not check OpenNebula health. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    all_running = True
    errors = []
    for line in stdout.strip().split("\n"):
        service_status = re.search(r"(\S+)\s+loaded active (\S+)", line)
        if service_status:
            service_name, status = service_status.groups()
            if status != "running" and "timer" not in service_name:
                all_running = False
                errors.append(f"{service_name} is {status}")
    if not all_running:
        msg(level="error", message="OpenNebula healthcheck failed")
    msg(level= "debug", message="OpenNebula healthcheck passed")
