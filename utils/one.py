import os
import re

from time import sleep
from textwrap import dedent
from typing import Dict, List, Optional, Tuple

from utils.cli import run_command
from utils.file import load_file, loads_json, save_file
from utils.questionary import ask_password, ask_select, ask_text
from utils.logs import msg
from utils.temp import save_temp_file, save_temp_json_file

## CONFIG MANAGEMENT ##
def get_oned_conf_path() -> str:
    """
    Get the path to the oned.conf file
    
    :return: the path to the oned.conf file, ``str``
    """
    msg(level="debug", message="Getting OpenNebula oned.conf path")
    return os.path.join("/etc", "one", "oned.conf")

## ONEGATE MANAGEMENT ##
def get_onegate_endpoint() -> Dict:
    oned_conf_path = get_oned_conf_path()
    oned_conf = load_file(file_path=oned_conf_path)
    match = re.search(r"^\s*ONEGATE_ENDPOINT\s*=\s*\"([^\"]+)\"", oned_conf, re.MULTILINE)
    if match is None:
        msg(level="error", message="ONEGATE_ENDPOINT key not found in oned.conf")
    url = match.group(1)
    ip_match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", url)
    if ip_match is None:
        msg(level="error", message="IP address not found in ONEGATE_ENDPOINT key")
    return ip_match.group(1)

## NETWORKS MANAGEMENT ##
def onevnet_show(vnet_name: str) -> Dict | None:
    """
    Get the details of a vnet in OpenNebula
    
    :param vnet_name: the name of the vnet, ``str``
    :return: the details of the vnet, ``Dict``
    """
    command = f"onevnet show \"{vnet_name}\" -j"
    stdout, _, rc = run_command(command=command)
    if rc != 0:
        msg(level="debug", message=f"Vnet {vnet_name} not found. Command executed: {command}")
        return None
    else:
        msg(level="debug", message=f"Vnet {vnet_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        return loads_json(data=stdout)

def onevnet_list () -> Dict:
    """
    Get the list of VNets in OpenNebula
    
    :return: the list of vnets, ``Dict``
    """
    command = "onevnet list -j"
    stdout, _, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Vnets not found. Create a vnet in OpenNebula before adding an appliance. Command executed: {command}")
    else:
        msg(level="debug", message=f"Vnets found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        return loads_json(data=stdout)

def get_vnets_names() -> List[str]:
    """
    Get the names of the vnets in OpenNebula
    
    :return: the names of the vnets, ``List[str]``
    """
    vnets = onevnet_list()
    vnets_names = []
    if "VNET_POOL" not in vnets or "VNET" not in vnets["VNET_POOL"]:
        msg(level="error", message="VNET_POOL key not found in vnets or VNET key not found in VNET_POOL")
    for vnet in vnets["VNET_POOL"]["VNET"]:
        if vnet is None:
            msg(level="error", message="Vnet is empty")
        if "NAME" not in vnet:
            msg(level="error", message="NAME key not found in vnet")
        vnets_names.append(vnet["NAME"])
    return vnets_names

def get_vnet_id(vnet_name: str) -> int:
    """
    Get the id of a vnet in OpenNebula
    
    :param vnet_name: the name of the vnet, ``str``
    :return: the id of the vnet, ``int``
    """
    vnet = onevnet_show(vnet_name=vnet_name)
    if vnet is None:
        msg(level="error", message=f"Vnet {vnet_name} not found")
    if "VNET" not in vnet or "ID" not in vnet["VNET"]:
        msg(level="error", message=f"VNET key not found in vnet {vnet_name} or ID key not found in VNET")
    vnet_id = vnet["VNET"]["ID"]
    if vnet_id is None:
        msg(level="error", message=f"Could not get id of vnet {vnet_name}")
    return vnet_id

## VM MANAGEMENT ##
def onewm_show(vm_name: str) -> Dict | None:
    """
    Get the details of a VM in OpenNebula
    
    :param vm_name: the name of the VM, ``str``
    :return: the details of the VM, ``Dict``
    """
    command = f"onevm show \"{vm_name}\" -j"
    stdout, _, rc = run_command(command=command)
    if rc != 0:
        msg(level="debug", message=f"VM {vm_name} not found. Command executed: {command}")
        return None
    else:
        msg(level="debug", message=f"VM {vm_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        return loads_json(data=stdout)

def get_vm_user_template(vm_name: str) -> Dict:
    """
    Get the user template of a VM in OpenNebula
    
    :param vm_name: the name of the VM, ``str``
    :return: the user template of the VM, ``Dict``
    """
    vm = onewm_show(vm_name=vm_name)
    if vm is None:
        msg(level="error", message=f"VM {vm_name} not found")
    if "VM" not in vm or "USER_TEMPLATE" not in vm["VM"]:
        msg(level="error", message=f"VM key not found in vm {vm_name} or USER_TEMPLATE key not found in VM")
    user_template = vm["VM"]["USER_TEMPLATE"]
    if user_template is None:
        msg(level="error", message=f"Could not get user template of VM {vm_name}")
    return user_template

def get_vm_user_template_param(vm_name: str, param: str) -> Dict:
    """
    Get the value of a user template parameter of a VM in OpenNebula
    
    :param vm_name: the name of the VM, ``str``
    :param param: the name of the parameter, ``str``
    :return: the value of the parameter, ``Dict``
    """
    user_template = get_vm_user_template(vm_name=vm_name)
    if param not in user_template:
        msg(level="error", message=f"Parameter {param} not found in user template of VM {vm_name}")
    value = user_template[param]
    if value is None:
        msg(level="error", message=f"Could not get value of parameter {param} in user template of VM {vm_name}")
    return value

def onevm_disk_resize(vm_name: str, disk_id: int, size: int) -> None:
    """
    Resize the disk of a VM in OpenNebula
    
    :param vm_name: the name of the VM, ``str``
    :param disk_id: the id of the disk, ``int``
    :param size: the new size of the disk, ``int``
    """
    command = f"onevm disk-resize \"{vm_name}\" {disk_id} {size}G"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not resize disk of VM {vm_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Disk of VM {vm_name} resized successfully. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def onevm_chown(vm_name: str, username: str, group_name: str) -> None:
    """
    Change the owner of a VM in OpenNebula
    
    :param vm_name: the name of the VM, ``str``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f"onevm chown \"{vm_name}\" \"{username}\" \"{group_name}\""
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not change owner of VM {vm_name} to {username}:{group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Owner of VM {vm_name} changed to {username}:{group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

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

def oneflow_show(oneflow_name: str) -> Dict | None:
    """
    Get the details of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the details of the service, ``Dict``
    """
    command = f"oneflow show \"{oneflow_name}\" -j"
    stdout, _, rc = run_command(command=command)
    if rc != 0:
        msg(level="debug", message=f"Service {oneflow_name} not found. Command executed: {command}")
        return None
    else:
        msg(level="debug", message=f"Service {oneflow_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        return loads_json(data=stdout)

def get_oneflow_roles(oneflow_name: str) -> List:
    """
    Get the roles of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the roles of the service, ``List``
    """
    oneflow = oneflow_show(oneflow_name=oneflow_name)
    if oneflow is None:
        msg(level="error", message=f"Service {oneflow_name} not found")
    if "DOCUMENT" not in oneflow or "TEMPLATE" not in oneflow["DOCUMENT"] or "BODY" not in oneflow["DOCUMENT"]["TEMPLATE"]:
        msg(level="error", message=f"DOCUMENT key not found in service {oneflow_name} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE")
    if "roles" not in oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(level="error", message=f"roles key not found in service {oneflow_name}")
    oneflow_roles = oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["roles"]
    if oneflow_roles is None:
        msg(level="error", message=f"Could not get roles of service {oneflow_name}")
    return oneflow_roles

def get_oneflow_roles_vm_names(oneflow_name: str) -> List[str]:
    """
    Get the names of the roles of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the names of the roles of the service, ``List[str]``
    """
    oneflow_roles = get_oneflow_roles(oneflow_name=oneflow_name)
    oneflow_roles_vm_names = []
    for role in oneflow_roles:
        if "nodes" not in role:
            msg(level="error", message="nodes key not found in role")
        for node in role["nodes"]:
            if "vm_info" not in node or "VM" not in node["vm_info"]:
                msg(level="error", message="vm_info key not found in role or VM key not found in vm_info")
            if "NAME" not in node["vm_info"]["VM"]:
                msg(level="error", message="NAME key not found in role")
            vm_name = node["vm_info"]["VM"]["NAME"]
            oneflow_roles_vm_names.append(vm_name)
    return oneflow_roles_vm_names

def get_oneflow_role(oneflow_name: str, oneflow_role: str) -> Dict:
    """
    Get the details of a role in a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :param oneflow_role: the name of the role, ``str``
    :return: the details of the role, ``Dict``
    """
    roles = get_oneflow_roles(oneflow_name=oneflow_name)
    for role in roles:
        if "name" not in role:
            msg(level="error", message="name key not found in role")
        if role["name"] == oneflow_role:
            return role
    msg(level="error", message=f"Role {oneflow_role} not found in service {oneflow_name}")

def get_oneflow_role_vm_name(oneflow_name: str, oneflow_role: str) -> str:
    """
    Get the name of a role in a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :param oneflow_role: the name of the role, ``str``
    :return: the name of the role, ``str``
    """
    role = get_oneflow_role(oneflow_name=oneflow_name, oneflow_role=oneflow_role)
    if "nodes" not in role:
        msg(level="error", message=f"nodes key not found in role {oneflow_role}")
    for node in role["nodes"]:
        if "vm_info" not in node or "VM" not in node["vm_info"]:
            msg(level="error", message="vm_info key not found in role or VM key not found in vm_info")
        if "NAME" not in node["vm_info"]["VM"]:
            msg(level="error", message="NAME key not found in role")
        return node["vm_info"]["VM"]["NAME"]

def get_oneflow_state(oneflow_name: str) -> str:
    """
    Get the state of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the state of the service, ``str``
    """
    oneflow = oneflow_show(oneflow_name=oneflow_name)
    if oneflow is None:
        msg(level="error", message=f"Service {oneflow_name} not found")
    if "DOCUMENT" not in oneflow or "TEMPLATE" not in oneflow["DOCUMENT"] or "BODY" not in oneflow["DOCUMENT"]["TEMPLATE"]:
        msg(level="error", message=f"DOCUMENT key not found in service {oneflow_name} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE")
    if "state" not in oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(level="error", message=f"state key not found in service {oneflow_name}")
    oneflow_state = oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["state"]
    if oneflow_state is None:
        msg(level="error", message=f"Could not get state of service {oneflow_name}")
    return oneflow_state

def get_oneflow_id(oneflow_name: str) -> int:
    """
    Get the id of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :return: the id of the service, ``int``
    """
    oneflow = oneflow_show(oneflow_name=oneflow_name)
    if oneflow is None:
        msg(level="error", message=f"Service {oneflow_name} not found")
    if "DOCUMENT" not in oneflow or "ID" not in oneflow["DOCUMENT"]:
        msg(level="error", message=f"DOCUMENT key not found in service {oneflow_name} or ID key not found in DOCUMENT")
    oneflow_id = oneflow["DOCUMENT"]["ID"]
    if oneflow_id is None:
        msg(level="error", message=f"Could not get id of service {oneflow_name}")
    return oneflow_id

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

def oneflow_chown(oneflow_name: str, username: str, group_name: str) -> None:
    """
    Change the owner of a service in OpenNebula
    
    :param oneflow_name: the name of the service, ``str``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f"oneflow chown \"{oneflow_name}\" \"{username}\" \"{group_name}\""
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Could not change owner of service {oneflow_name} to {username}:{group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Owner of service {oneflow_name} changed to {username}:{group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

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

def get_oneflow_template_networks(oneflow_template_name: str) -> Dict | None:
    """
    Get the networks of a service in OpenNebula
    
    :param oneflow_template_name: the name of the service, ``str``
    :return: the networks of the service, ``Dict``
    """
    oneflow_template = oneflow_template_show(oneflow_template_name=oneflow_template_name)
    if oneflow_template is None:
        msg(level="error", message=f"Service {oneflow_template_name} not found")
    if "DOCUMENT" not in oneflow_template or "TEMPLATE" not in oneflow_template["DOCUMENT"] or "BODY" not in oneflow_template["DOCUMENT"]["TEMPLATE"]:
        msg(level="error", message=f"DOCUMENT key not found in service {oneflow_template_name} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE")
    if "networks" not in oneflow_template["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(level="error", message=f"networks key not found in service {oneflow_template_name}")
    networks = oneflow_template["DOCUMENT"]["TEMPLATE"]["BODY"]["networks"]
    if networks is None:
        return None
    return networks

def split_attr_description(attr_description: str) -> Tuple[str, str, str, str]:
    """
    Split the custom attribute string from the OneFlow template
    
    :param attr_description: the custom attribute string, ``str``
    :return: the parsed custom attribute as a tuple (field_type, input_type, description, default_value), ``Tuple[str, str, str, str]
    """
    parts = attr_description.split("|")
    field_type = parts[0]
    input_type = parts[1]
    description = parts[2]
    default_value = ""
    if "||" in attr_description:
        default_start_index = attr_description.index("||") + 2
        default_value = attr_description[default_start_index:].strip()
    return field_type, input_type, description, default_value

def oneflow_template_instantiate(oneflow_template_name: str, username: str, group_name: str) -> None:
    """
    Instantiate a service in OpenNebula
    
    :param oneflow_template_id: the id of the service, ``int``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    oneflow = oneflow_show(oneflow_name=oneflow_template_name)
    if oneflow is None:
        custom_attrs = get_oneflow_template_custom_attrs(oneflow_template_name=oneflow_template_name)
        data = {}
        custom_attrs_values = {}
        if custom_attrs:
            attrs = {}
            for attr_key, attr_description in custom_attrs.items():
                field_type, input_type, description, default_value = split_attr_description(attr_description=attr_description)
                description = description + ":"
                if field_type == "O":
                    if input_type == "boolean":
                        attr_value = ask_select(
                            message=description,
                            choices=["YES", "NO"]
                        )
                        attrs[attr_key] = attr_value
                    elif input_type == "text" or input_type == "text64":
                        attr_value = ask_text(
                            message=description,
                            default=default_value
                        )
                        attrs[attr_key] = attr_value
                    elif input_type == "password":
                        attr_value = ask_password(
                            message=description,
                            default=default_value
                        )
                        attrs[attr_key] = attr_value
                    else:
                        msg(level="error", message=f"Error instantiating service {oneflow_template_name}. Input type {input_type} not supported for custom attribute {attr_key}")
                elif field_type == "M":
                    if input_type == "boolean":
                        attr_value = ask_select(
                            message=description,
                            choices=["YES", "NO"],
                            default=default_value
                        )
                        attrs[attr_key] = attr_value
                    elif input_type == "text" or input_type == "text64":
                        attr_value = ask_text(
                            message=description,
                            default=default_value,
                            validate=lambda attr_value: (
                                "Value must not be empty" if not attr_value else
                                True
                            )
                        )
                        attrs[attr_key] = attr_value
                    elif input_type == "password":
                        attr_value = ask_password(
                            message=description,
                            default=default_value,
                            validate=lambda attr_value: (
                                "Value must not be empty" if not attr_value else
                                True
                            )
                        )
                        attrs[attr_key] = attr_value
                    else:
                        msg(level="error", message=f"Error instantiating service {oneflow_template_name}. Input type {input_type} not supported for custom attribute {attr_key}")
                else:
                    msg(level="error", message=f"Error instantiating service {oneflow_template_name}. Field type {field_type} not supported for custom attribute {attr_key}")
            custom_attrs_values["custom_attrs_values"] = attrs
        networks = get_oneflow_template_networks(oneflow_template_name=oneflow_template_name)
        networks_values = {}
        networks_values_list = []
        if networks:
            nets = {}
            for network_key, network_description in networks.items():
                field_type, input_type, description, default_value = split_attr_description(attr_description=network_description)
                if field_type == "M":
                    if input_type == "network":
                        network_name = ask_select(
                            message=description,
                            choices=get_vnets_names()
                        )
                        network_id = get_vnet_id(vnet_name=network_name)
                        nets[network_key] = {"id": str(network_id)}
                        networks_values_list.append(nets)
                    else:
                        msg(level="error", message=f"Error instantiating service {oneflow_template_name}. Input type {input_type} not supported for network")
                else:
                    msg(level="error", message=f"Error instantiating service {oneflow_template_name}. Field type {field_type} not supported for network")
            networks_values["networks_values"] = networks_values_list
        if custom_attrs_values:
            data.update(custom_attrs_values)
        if networks_values:
            data.update(networks_values)
        if data:
            custom_attrs_path = save_temp_json_file(data=data, file_name=f"{oneflow_template_name}_service_custom_attrs.json")
            command = f"oneflow-template instantiate \"{oneflow_template_name}\" < \"{custom_attrs_path}\""
        else:
            command = f"oneflow-template instantiate \"{oneflow_template_name}\""
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(level="error", message=f"Could not instantiate service {oneflow_template_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
        msg(level="debug", message=f"Service {oneflow_template_name} instantiated. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
        sleep(5)
        oneflow_id = int(re.search(r"ID:\s*(\d+)", stdout).group(1))
        oneflow_state = get_oneflow_state(oneflow_name=oneflow_template_name)
        while oneflow_state != "2":
            sleep(10)
            oneflow_state = get_oneflow_state(oneflow_name=oneflow_template_name)
    else:
        oneflow_id = get_oneflow_id(oneflow_name=oneflow_template_name)
    oneflow_chown(oneflow_name=oneflow_template_name, username=username, group_name=group_name)
    oneflow_roles_vm_names = get_oneflow_roles_vm_names(oneflow_name=oneflow_template_name)
    if oneflow_roles_vm_names:
        for vm_name in oneflow_roles_vm_names:
            onevm_chown(vm_name=vm_name, username=username, group_name=group_name)
    return oneflow_id

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

def get_user_public_ssh_keys(username: str) -> List[str]:
    """
    Get the public SSH keys of an user in OpenNebula

    :param username: the name of the user, ``str``
    :return: the public SSH keys of the user, ``List[str]``
    """
    user = oneuser_show(username=username)
    if user is None:
        msg(level="error", message=f"User {username} not found")
    if "USER" not in user or "TEMPLATE" not in user["USER"]:
        msg(level="error", message=f"USER key not found in user {username} or TEMPLATE key not found in USER")
    if "SSH_PUBLIC_KEY" not in user["USER"]["TEMPLATE"]:
        return ""
    public_ssh_keys = user["USER"]["TEMPLATE"]["SSH_PUBLIC_KEY"]
    if public_ssh_keys is None:
        return ""
    return public_ssh_keys.split("\n")

def oneuser_update_public_ssh_key(username: str, public_ssh_key: str) -> None:
    """
    Update the SSH key of an user in OpenNebula
    
    :param username: the name of the user, ``str``
    :param public_ssh_key: the public SSH key, ``str``
    """
    public_ssh_keys = get_user_public_ssh_keys(username=username)
    if public_ssh_key not in public_ssh_keys:
        all_public_ssh_keys = "\n".join(public_ssh_keys)
        all_public_ssh_keys += f"\n{public_ssh_key}"
        command = f"echo \'SSH_PUBLIC_KEY=\"{all_public_ssh_keys}\"\' | oneuser update \"{username}\" --append"
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(level="error", message=f"Could not update SSH key of user {username} to {public_ssh_key}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
        msg(level="debug", message=f"SSH key of user {username} updated to {public_ssh_key}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
    else:
        msg(level="debug", message=f"User {username} already has SSH key {public_ssh_key}")

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
        marketplace_content_path = save_temp_file(data=marketplace_content, file_name=f"{marketplace_name}_marketplace_content")
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
