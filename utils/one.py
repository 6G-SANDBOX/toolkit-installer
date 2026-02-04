"""
OpenNebula CLI Wrapper Functions

================================================================================
                              FUNCTION INDEX
================================================================================
- OPENNEBULA MANAGEMENT (line ~93):
    check_one_health, get_oned_conf_path, onegate_endpoint, restart_one

- ACL MANAGEMENT (line ~181):
    check_group_acl, oneacl_create, oneacl_list

- DATASTORE MANAGEMENT (line ~274):
    onedatastore_list, onedatastores_names

- ONEFLOW MANAGEMENT (line ~334):
    oneflow_chown, oneflow_custom_attr_value, oneflow_id, oneflow_list,
    oneflow_role_info, oneflow_role_vm_name, oneflow_roles, oneflow_roles_vm_names,
    oneflow_show, oneflow_show_by_id, oneflow_state_by_id, oneflow_name_by_id,
    oneflow_roles_by_id, oneflow_roles_vm_names_by_id, oneflow_chown_by_id,
    oneflow_role_info_by_id, oneflow_role_vm_name_by_id,
    oneflow_custom_attr_value_by_id, oneflow_state, oneflows_names

- ONEFLOW TEMPLATE MANAGEMENT (line ~910):
    oneflow_template_chown, oneflow_template_custom_attrs, oneflow_template_ids,
    oneflow_template_image_ids, split_attr_description, oneflow_template_instantiate,
    oneflow_template_networks, oneflow_template_roles, oneflow_template_show

- GROUP MANAGEMENT (line ~1363):
    check_group_admin, onegroup_addadmin, onegroup_create, onegroup_id,
    onegroup_list, onegroup_show, onegroups_names

- HOST MANAGEMENT (line ~1551):
    onehost_available_cpu, onehost_available_mem, onehost_cpu_model,
    onehost_list, onehost_show, onehosts_avx_cpu_mem

- IMAGES MANAGEMENT (line ~1771):
    oneimage_chown, oneimage_name, oneimage_id_by_name, oneimage_delete,
    oneimage_list, oneimage_rename, oneimage_show, oneimage_state,
    oneimage_update, oneimage_version, oneimages_attribute, oneimages_names

- MARKETPLACE MANAGEMENT (line ~2101):
    get_marketplace_monitoring_interval, update_marketplace_monitoring_interval,
    onemarket_create, onemarket_endpoint, onemarket_list, onemarket_show,
    onemarkets_names

- MARKETAPP MANAGEMENT (line ~2316):
    onemarketapp_add, onemarketapp_instantiate, onemarketapp_export,
    onemarketapp_curl, onemarketapp_description, onemarketapp_name,
    onemarketapp_show, onemarketapp_type, onemarketapp_version

- TEMPLATE MANAGEMENT (line ~3184):
    onetemplate_chown, onetemplate_delete, onetemplate_id, onetemplate_image_ids,
    onetemplate_instantiate, onetemplate_name, onetemplate_list, onetemplate_rename,
    onetemplate_show, onetemplate_user_inputs, onetemplates_names

- USER MANAGEMENT (line ~3641):
    oneuser_chgrp, oneuser_create, oneuser_list, oneuser_public_ssh_keys,
    oneuser_show, oneuser_update_public_ssh_key, oneusername, oneusername_id,
    oneusernames

- VM MANAGEMENT (line ~3912):
    onevm_chown, onevm_chown_by_id, onevm_cpu_model, onevm_deploy, onevm_disk_resize,
    onevm_disk_size, onevm_id, onevm_ip, onevm_ip_by_id, onevm_list, onevm_template_id,
    onevm_terminate_hard, onevm_show, onevm_show_by_id, onevm_state, onevm_state_by_id,
    onevm_undeploy_hard, onevm_updateconf_cpu_model, onevm_user_input,
    onevm_user_input_by_id, onevm_user_template, onevm_user_template_param,
    onevms_names, onevms_running, onevms_running_with_ids

- NETWORKS MANAGEMENT (line ~4564):
    onevnet_id, onevnet_list, onevnet_show, onevnets_names

================================================================================
"""

import os
import re
from textwrap import dedent
from time import sleep
from typing import Dict, List, Optional, Tuple

from utils.cli import run_command
from utils.file import load_file, loads_json, save_file, save_json_file
from utils.logs import msg
from utils.os import TEMP_DIRECTORY, join_path
from utils.parser import gb_to_mb
from utils.questionary import (
    ask_confirm,
    ask_password,
    ask_select,
    ask_text,
)


# ##############################################################################
# ##                         OPENNEBULA MANAGEMENT                            ##
# ##############################################################################
def check_one_health() -> None:
    """
    Check OpenNebula health
    """
    command = "systemctl list-units | grep opennebula"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not check OpenNebula health. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
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
        msg(
            level="error",
            message=f"OpenNebula healthcheck failed. Following services are not running: {', '.join(errors)}",
        )
    msg(
        level="debug",
        message="OpenNebula healthcheck passed. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def get_oned_conf_path() -> str:
    """
    Get the path to the oned.conf file

    :return: the path to the oned.conf file, ``str``
    """
    return os.path.join("/etc", "one", "oned.conf")


def onegate_endpoint() -> str:
    """
    Get the endpoint of the OneGate service in OpenNebula

    :return: the endpoint of the OneGate service, ``str``
    """
    oned_conf_path = get_oned_conf_path()
    oned_conf = load_file(file_path=oned_conf_path)
    match = re.search(
        r"^\s*ONEGATE_ENDPOINT\s*=\s*\"([^\"]+)\"",
        oned_conf,
        re.MULTILINE,
    )
    if match is None:
        msg(
            level="error",
            message=f"ONEGATE_ENDPOINT key not found in the OpenNebula configuration file {oned_conf}",
        )
    url = match.group(1)
    ip_match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", url)
    if ip_match is None:
        msg(
            level="error",
            message=f"ONEGATE_ENDPOINT key in the OpenNebula configuration file {oned_conf} does not contain an IP address defined",
        )
    return ip_match.group(1)


def restart_one() -> None:
    """
    Restart the OpenNebula daemon
    """
    command = "systemctl restart opennebula"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not restart OpenNebula daemon. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"OpenNebula daemon restarted. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


# ##############################################################################
# ##                            ACL MANAGEMENT                                ##
# ##############################################################################


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
        msg(
            level="error",
            message="ACL_POOL key not found in acls or ACL key not found in ACL_POOL",
        )
    acl_pool = acls["ACL_POOL"]["ACL"]
    if acl_pool is None:
        return False
    for acl in acl_pool:
        if acl is None:
            msg(level="error", message="ACL is empty")
        if "STRING" not in acl:
            msg(
                level="error",
                message="STRING key not found in acl",
            )
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
    if check_group_acl(
        group_id=group_id,
        resources=resources,
        rights=rights,
    ):
        msg(
            level="debug",
            message=f"Group with id {group_id} already has ACL. Resources: {resources}. Rights: {rights}",
        )
    else:
        command = f'oneacl create "@{group_id} {resources} {rights}"'
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(
                level="error",
                message=f"Could not add ACL to group with id {group_id}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
            )
        msg(
            level="debug",
            message=f"ACL added to group with id {group_id}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return int(re.search(r"ID:\s*(\d+)", stdout).group(1))


def oneacl_list() -> Dict | None:
    """
    Get the list of ACLs in OpenNebula

    :return: the list of ACLs, ``Dict``
    """
    command = "oneacl list -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"Could not get OpenNebula ACLs. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"OpenNebula ACLs found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


# ##############################################################################
# ##                         DATASTORE MANAGEMENT                             ##
# ##############################################################################


def onedatastore_list() -> Dict:
    """
    Get the list of datastores in OpenNebula

    :return: the list of datastores, ``Dict``
    """
    command = "onedatastore list -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"OpenNebula datastores not found. Create a datastore in OpenNebula before adding an appliance. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    else:
        msg(
            level="debug",
            message=f"OpenNebula datastores found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onedatastores_names() -> List[str]:
    """
    Get the names of the datastores in OpenNebula

    :return: the names of the datastores, ``List[str]``
    """
    datastores = onedatastore_list()
    datastores_names = []
    if (
        "DATASTORE_POOL" not in datastores
        or "DATASTORE" not in datastores["DATASTORE_POOL"]
    ):
        msg(
            level="error",
            message="DATASTORE_POOL key not found in datastores or DATASTORE key not found in DATASTORE_POOL",
        )
    datastore_pool = datastores["DATASTORE_POOL"]["DATASTORE"]
    if datastore_pool is None:
        msg(
            level="error",
            message="OpenNebula datastores not found. Create a datastore in OpenNebula before adding an appliance",
        )
    for datastore in datastore_pool:
        if datastore is None:
            msg(level="error", message="Datastore is empty")
        if "NAME" not in datastore:
            msg(
                level="error",
                message="NAME key not found in datastore",
            )
        datastores_names.append(datastore["NAME"])
    return datastores_names


# ##############################################################################
# ##                          ONEFLOW MANAGEMENT                              ##
# ##############################################################################


def oneflow_chown(oneflow_name: str, username: str, group_name: str) -> None:
    """
    Change the owner of a service in OpenNebula

    :param oneflow_name: the name of the service, ``str``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f'oneflow chown "{oneflow_name}" "{username}" "{group_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not change owner of service {oneflow_name} to {username}:{group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Owner of service {oneflow_name} changed to {username}:{group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def oneflow_custom_attr_value(oneflow_name: str, attr_key: str) -> str:
    """
    Get the value of a custom attribute of a service in OpenNebula

    :param oneflow_name: the name of the service, ``str``
    :param attr_key: the key of the custom attribute, ``str``
    :return: the value of the custom attribute, ``str``
    """
    oneflow = oneflow_show(oneflow_name=oneflow_name)
    if oneflow is None:
        msg(
            level="error",
            message=f"Service {oneflow_name} not found",
        )
    if (
        "DOCUMENT" not in oneflow
        or "TEMPLATE" not in oneflow["DOCUMENT"]
        or "BODY" not in oneflow["DOCUMENT"]["TEMPLATE"]
    ):
        msg(
            level="error",
            message=f"DOCUMENT key not found in service {oneflow_name} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE",
        )
    if "custom_attrs_values" not in oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(
            level="error",
            message=f"custom_attrs_values key not found in service {oneflow_name}",
        )
    custom_attrs_values = oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["custom_attrs_values"]
    if attr_key not in custom_attrs_values:
        msg(
            level="error",
            message=f"Custom attribute {attr_key} not found in service {oneflow_name}",
        )
    attr_value = custom_attrs_values[attr_key]
    if attr_value is None:
        msg(
            level="error",
            message=f"Could not get value of custom attribute {attr_key} in service {oneflow_name}",
        )
    return attr_value


def oneflow_id(oneflow_name: str) -> int:
    """
    Get the id of a service in OpenNebula

    :param oneflow_name: the name of the service, ``str``
    :return: the id of the service, ``int``
    """
    oneflow = oneflow_show(oneflow_name=oneflow_name)
    if oneflow is None:
        msg(
            level="error",
            message=f"Service {oneflow_name} not found",
        )
    if "DOCUMENT" not in oneflow or "ID" not in oneflow["DOCUMENT"]:
        msg(
            level="error",
            message=f"DOCUMENT key not found in service {oneflow_name} or ID key not found in DOCUMENT",
        )
    id = oneflow["DOCUMENT"]["ID"]
    if id is None:
        msg(
            level="error",
            message=f"Could not get id of service {oneflow_name}",
        )
    return id


def oneflow_list() -> List | None:
    """
    Get the list of services in OpenNebula

    :return: the list of services, ``List``
    """
    command = "oneflow list -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"OpenNebula services not found. Create a service in OpenNebula before adding an appliance. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"OpenNebula services found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def oneflow_role_info(oneflow_name: str, oneflow_role: str) -> Dict:
    """
    Get the details of a role in a service in OpenNebula

    :param oneflow_name: the name of the service, ``str``
    :param oneflow_role: the name of the role, ``str``
    :return: the details of the role, ``Dict``
    """
    roles = oneflow_roles(oneflow_name=oneflow_name)
    for role in roles:
        if "name" not in role:
            msg(
                level="error",
                message="name key not found in role",
            )
        if role["name"] == oneflow_role:
            return role
    msg(
        level="error",
        message=f"Role {oneflow_role} not found in service {oneflow_name}",
    )


def oneflow_role_vm_name(oneflow_name: str, oneflow_role: str) -> str:
    """
    Get the name of a role in a service in OpenNebula

    :param oneflow_name: the name of the service, ``str``
    :param oneflow_role: the name of the role, ``str``
    :return: the name of the role, ``str``
    """
    role = oneflow_role_info(oneflow_name=oneflow_name, oneflow_role=oneflow_role)
    if "nodes" not in role:
        msg(
            level="error",
            message=f"nodes key not found in role {oneflow_role}",
        )
    for node in role["nodes"]:
        if "vm_info" not in node or "VM" not in node["vm_info"]:
            msg(
                level="error",
                message=f"vm_info key not found in role {oneflow_role} or VM key not found in vm_info",
            )
        if "NAME" not in node["vm_info"]["VM"]:
            msg(
                level="error",
                message=f"NAME key not found in role {oneflow_role}",
            )
        return node["vm_info"]["VM"]["NAME"]


def oneflow_roles(oneflow_name: str) -> List:
    """
    Get the roles of a service in OpenNebula

    :param oneflow_name: the name of the service, ``str``
    :return: the roles of the service, ``List``
    """
    oneflow = oneflow_show(oneflow_name=oneflow_name)
    if oneflow is None:
        msg(
            level="error",
            message=f"Service {oneflow_name} not found",
        )
    if (
        "DOCUMENT" not in oneflow
        or "TEMPLATE" not in oneflow["DOCUMENT"]
        or "BODY" not in oneflow["DOCUMENT"]["TEMPLATE"]
    ):
        msg(
            level="error",
            message=f"DOCUMENT key not found in service {oneflow_name} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE",
        )
    if "roles" not in oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(
            level="error",
            message=f"roles key not found in service {oneflow_name}",
        )
    roles = oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["roles"]
    if roles is None:
        msg(
            level="error",
            message=f"Could not get roles of service {oneflow_name}",
        )
    return roles


def oneflow_roles_vm_names(oneflow_name: str) -> List[str]:
    """
    Get the names of the roles of a service in OpenNebula

    :param oneflow_name: the name of the service, ``str``
    :return: the names of the roles of the service, ``List[str]``
    """
    roles = oneflow_roles(oneflow_name=oneflow_name)
    roles_vm_names = []
    for role in roles:
        if "nodes" not in role:
            msg(
                level="error",
                message="nodes key not found in role",
            )
        for node in role["nodes"]:
            if "vm_info" not in node or "VM" not in node["vm_info"]:
                msg(
                    level="error",
                    message="vm_info key not found in role or VM key not found in vm_info",
                )
            if "NAME" not in node["vm_info"]["VM"]:
                msg(
                    level="error",
                    message="NAME key not found in role",
                )
            vm_name = node["vm_info"]["VM"]["NAME"]
            roles_vm_names.append(vm_name)
    return roles_vm_names


def oneflow_show(oneflow_name: str) -> Dict | None:
    """
    Get the details of a service in OpenNebula

    :param oneflow_name: the name of the service, ``str``
    :return: the details of the service, ``Dict``
    """
    command = f'oneflow show "{oneflow_name}" -j'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"Service {oneflow_name} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"Service {oneflow_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def oneflow_show_by_id(oneflow_id: int) -> Dict | None:
    """
    Get the details of a service in OpenNebula by ID

    :param oneflow_id: the ID of the service, ``int``
    :return: the details of the service, ``Dict``
    """
    command = f'oneflow show {oneflow_id} -j'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"Service with ID {oneflow_id} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"Service with ID {oneflow_id} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def oneflow_state_by_id(oneflow_id: int) -> int:
    """
    Get the state of a service in OpenNebula by ID

    :param oneflow_id: the ID of the service, ``int``
    :return: the state of the service, ``int``
    """
    oneflow = oneflow_show_by_id(oneflow_id=oneflow_id)
    if oneflow is None:
        msg(
            level="error",
            message=f"Service with ID {oneflow_id} not found",
        )
    if (
        "DOCUMENT" not in oneflow
        or "TEMPLATE" not in oneflow["DOCUMENT"]
        or "BODY" not in oneflow["DOCUMENT"]["TEMPLATE"]
    ):
        msg(
            level="error",
            message=f"DOCUMENT key not found in service ID {oneflow_id} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE",
        )
    if "state" not in oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(
            level="error",
            message=f"state key not found in service ID {oneflow_id}",
        )
    state = oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["state"]
    if state is None:
        msg(
            level="error",
            message=f"Could not get state of service ID {oneflow_id}",
        )
    return state


def oneflow_name_by_id(oneflow_id: int) -> str:
    """
    Get the name of a service in OpenNebula by ID

    :param oneflow_id: the ID of the service, ``int``
    :return: the name of the service, ``str``
    """
    oneflow = oneflow_show_by_id(oneflow_id=oneflow_id)
    if oneflow is None:
        msg(
            level="error",
            message=f"Service with ID {oneflow_id} not found",
        )
    if "DOCUMENT" not in oneflow or "NAME" not in oneflow["DOCUMENT"]:
        msg(
            level="error",
            message=f"DOCUMENT key not found in service ID {oneflow_id} or NAME key not found in DOCUMENT",
        )
    return oneflow["DOCUMENT"]["NAME"]


def oneflow_roles_by_id(oneflow_id: int) -> List:
    """
    Get the roles of a service in OpenNebula by ID

    :param oneflow_id: the ID of the service, ``int``
    :return: the roles of the service, ``List``
    """
    oneflow = oneflow_show_by_id(oneflow_id=oneflow_id)
    if oneflow is None:
        msg(
            level="error",
            message=f"Service with ID {oneflow_id} not found",
        )
    if (
        "DOCUMENT" not in oneflow
        or "TEMPLATE" not in oneflow["DOCUMENT"]
        or "BODY" not in oneflow["DOCUMENT"]["TEMPLATE"]
    ):
        msg(
            level="error",
            message=f"DOCUMENT key not found in service ID {oneflow_id} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE",
        )
    if "roles" not in oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(
            level="error",
            message=f"roles key not found in service ID {oneflow_id}",
        )
    roles = oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["roles"]
    if roles is None:
        msg(
            level="error",
            message=f"Could not get roles of service ID {oneflow_id}",
        )
    return roles


def oneflow_roles_vm_names_by_id(oneflow_id: int) -> List[str]:
    """
    Get the names of the VMs in the roles of a service in OpenNebula by ID

    :param oneflow_id: the ID of the service, ``int``
    :return: the names of the VMs in the roles of the service, ``List[str]``
    """
    roles = oneflow_roles_by_id(oneflow_id=oneflow_id)
    roles_vm_names = []
    for role in roles:
        if "nodes" not in role:
            msg(
                level="error",
                message="nodes key not found in role",
            )
        for node in role["nodes"]:
            if "vm_info" not in node or "VM" not in node["vm_info"]:
                msg(
                    level="error",
                    message="vm_info key not found in role or VM key not found in vm_info",
                )
            if "NAME" not in node["vm_info"]["VM"]:
                msg(
                    level="error",
                    message="NAME key not found in role",
                )
            vm_name = node["vm_info"]["VM"]["NAME"]
            roles_vm_names.append(vm_name)
    return roles_vm_names


def oneflow_chown_by_id(oneflow_id: int, username: str, group_name: str) -> None:
    """
    Change the owner of a service in OpenNebula by ID

    :param oneflow_id: the ID of the service, ``int``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f'oneflow chown {oneflow_id} "{username}" "{group_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not change owner of service ID {oneflow_id} to {username}:{group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Owner of service ID {oneflow_id} changed to {username}:{group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def oneflow_role_info_by_id(oneflow_id: int, oneflow_role: str) -> Dict:
    """
    Get the details of a role in a service in OpenNebula by ID

    :param oneflow_id: the ID of the service, ``int``
    :param oneflow_role: the name of the role, ``str``
    :return: the details of the role, ``Dict``
    """
    roles = oneflow_roles_by_id(oneflow_id=oneflow_id)
    for role in roles:
        if "name" not in role:
            msg(
                level="error",
                message="name key not found in role",
            )
        if role["name"] == oneflow_role:
            return role
    msg(
        level="error",
        message=f"Role {oneflow_role} not found in service ID {oneflow_id}",
    )


def oneflow_role_vm_name_by_id(oneflow_id: int, oneflow_role: str) -> str:
    """
    Get the name of a role in a service in OpenNebula by ID

    :param oneflow_id: the ID of the service, ``int``
    :param oneflow_role: the name of the role, ``str``
    :return: the name of the role, ``str``
    """
    role = oneflow_role_info_by_id(oneflow_id=oneflow_id, oneflow_role=oneflow_role)
    if "nodes" not in role:
        msg(
            level="error",
            message=f"nodes key not found in role {oneflow_role}",
        )
    for node in role["nodes"]:
        if "vm_info" not in node or "VM" not in node["vm_info"]:
            msg(
                level="error",
                message=f"vm_info key not found in role {oneflow_role} or VM key not found in vm_info",
            )
        if "NAME" not in node["vm_info"]["VM"]:
            msg(
                level="error",
                message=f"NAME key not found in role {oneflow_role}",
            )
        return node["vm_info"]["VM"]["NAME"]


def oneflow_custom_attr_value_by_id(oneflow_id: int, attr_key: str) -> str:
    """
    Get the value of a custom attribute of a service in OpenNebula by ID

    :param oneflow_id: the ID of the service, ``int``
    :param attr_key: the key of the custom attribute, ``str``
    :return: the value of the custom attribute, ``str``
    """
    oneflow = oneflow_show_by_id(oneflow_id=oneflow_id)
    if oneflow is None:
        msg(
            level="error",
            message=f"Service with ID {oneflow_id} not found",
        )
    if (
        "DOCUMENT" not in oneflow
        or "TEMPLATE" not in oneflow["DOCUMENT"]
        or "BODY" not in oneflow["DOCUMENT"]["TEMPLATE"]
    ):
        msg(
            level="error",
            message=f"DOCUMENT key not found in service ID {oneflow_id} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE",
        )
    if "custom_attrs_values" not in oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(
            level="error",
            message=f"custom_attrs_values key not found in service ID {oneflow_id}",
        )
    custom_attrs_values = oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["custom_attrs_values"]
    if attr_key not in custom_attrs_values:
        msg(
            level="error",
            message=f"Custom attribute {attr_key} not found in service ID {oneflow_id}",
        )
    attr_value = custom_attrs_values[attr_key]
    if attr_value is None:
        msg(
            level="error",
            message=f"Could not get value of custom attribute {attr_key} in service ID {oneflow_id}",
        )
    return attr_value


def oneflow_state(oneflow_name: str) -> int:
    """
    Get the state of a service in OpenNebula

    :param oneflow_name: the name of the service, ``str``
    :return: the state of the service, ``int``
    """
    oneflow = oneflow_show(oneflow_name=oneflow_name)
    if oneflow is None:
        msg(
            level="error",
            message=f"Service {oneflow_name} not found",
        )
    if (
        "DOCUMENT" not in oneflow
        or "TEMPLATE" not in oneflow["DOCUMENT"]
        or "BODY" not in oneflow["DOCUMENT"]["TEMPLATE"]
    ):
        msg(
            level="error",
            message=f"DOCUMENT key not found in service {oneflow_name} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE",
        )
    if "state" not in oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(
            level="error",
            message=f"state key not found in service {oneflow_name}",
        )
    state = oneflow["DOCUMENT"]["TEMPLATE"]["BODY"]["state"]
    if state is None:
        msg(
            level="error",
            message=f"Could not get state of service {oneflow_name}",
        )
    return state


def oneflows_names() -> List[str]:
    """
    Get the names of the services in OpenNebula

    :return: the names of the services, ``List[str]``
    """
    oneflows = oneflow_list()
    oneflows_names = []
    if oneflows:
        for oneflow in oneflows:
            if "NAME" not in oneflow:
                msg(
                    level="error",
                    message="NAME key not found in service",
                )
            oneflows_names.append(oneflow["NAME"])
    return oneflows_names


# ##############################################################################
# ##                     ONEFLOW TEMPLATE MANAGEMENT                          ##
# ##############################################################################


def oneflow_template_chown(
    oneflow_template_name: str,
    username: str,
    group_name: str,
) -> None:
    """
    Change the owner of a service in OpenNebula

    :param oneflow_template_name: the name of the service, ``str``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = (
        f'oneflow-template chown "{oneflow_template_name}" "{username}" "{group_name}"'
    )
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not change owner of service {oneflow_template_name} to {username}:{group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Owner of service {oneflow_template_name} changed to {username}:{group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def oneflow_template_custom_attrs(
    oneflow_template_name: str,
) -> Dict | None:
    """
    Get the custom_attrs key of a service in OpenNebula

    :param oneflow_template_name: the name of the service, ``str``
    :return: the custom_attrs key of the service, ``Dict``
    """
    oneflow_template = oneflow_template_show(
        oneflow_template_name=oneflow_template_name
    )
    if oneflow_template is None:
        msg(
            level="error",
            message=f"Service {oneflow_template_name} not found",
        )
    if (
        "DOCUMENT" not in oneflow_template
        or "TEMPLATE" not in oneflow_template["DOCUMENT"]
        or "BODY" not in oneflow_template["DOCUMENT"]["TEMPLATE"]
    ):
        msg(
            level="error",
            message=f"DOCUMENT key not found in service {oneflow_template_name} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE",
        )
    if "custom_attrs" not in oneflow_template["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(
            level="error",
            message=f"custom_attrs key not found in service {oneflow_template_name}",
        )
    custom_attrs = oneflow_template["DOCUMENT"]["TEMPLATE"]["BODY"]["custom_attrs"]
    if custom_attrs is None:
        return None
    return custom_attrs


def oneflow_template_ids(
    oneflow_template_name: str,
) -> List[int]:
    """
    Get the template ids of a service in OpenNebula

    :param oneflow_template_name: the name of the service, ``str``
    :return: the template ids of the service, ``List[int]``
    """
    roles = oneflow_template_roles(oneflow_template_name=oneflow_template_name)
    template_ids = []
    for role in roles:
        if "vm_template" not in role:
            msg(
                level="error",
                message="vm_template key not found in role",
            )
        template_ids.append(int(role["vm_template"]))
    return template_ids


def oneflow_template_image_ids(
    oneflow_template_name: str,
) -> List[int]:
    """
    Get the image ids of a service in OpenNebula

    :param oneflow_template_name: the name of the service, ``str``
    :return: the image ids of the service, ``List[int]``
    """
    template_ids = oneflow_template_ids(oneflow_template_name=oneflow_template_name)
    image_ids = []
    for template_id in template_ids:
        image_ids.extend(onetemplate_image_ids(template_id=template_id))
    return image_ids


def split_attr_description(
    attr_description: str,
) -> Tuple[str, str, str, str]:
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
    return (
        field_type,
        input_type,
        description,
        default_value,
    )


def oneflow_template_instantiate(
    oneflow_template_name: str, username: str, group_name: str
) -> Tuple[str, int]:
    """
    Instantiate a service in OpenNebula

    :param oneflow_template_name: the name of the service, ``str``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    :return: tuple with the name and ID of the instantiated service, ``Tuple[str, int]``
    """
    # refer: https://docs.opennebula.io/6.10/management_and_operations/references/template.html#template-user-inputs
    custom_attrs = oneflow_template_custom_attrs(
        oneflow_template_name=oneflow_template_name
    )
    data = {}
    custom_attrs_values = {}
    if custom_attrs:
        attrs = {}
        for (
            attr_key,
            attr_description,
        ) in custom_attrs.items():
            (
                field_type,
                input_type,
                description,
                default_value,
            ) = split_attr_description(attr_description=attr_description)
            description = description + ":"
            if field_type == "O":
                if input_type == "boolean":
                    attr_value = ask_select(
                        message=description,
                        choices=["YES", "NO"],
                    )
                    attrs[attr_key] = attr_value
                elif input_type == "text" or input_type == "text64":
                    attr_value = ask_text(
                        message=description,
                        default=default_value,
                    )
                    attrs[attr_key] = attr_value
                elif input_type == "password":
                    attr_value = ask_password(
                        message=description,
                        default=default_value,
                    )
                    attrs[attr_key] = attr_value
                else:
                    msg(
                        level="error",
                        message=f"Error instantiating service {oneflow_template_name}. Input type {input_type} not supported for custom attribute {attr_key}",
                    )
            elif field_type == "M":
                if input_type == "boolean":
                    attr_value = ask_select(
                        message=description,
                        choices=["YES", "NO"],
                        default=default_value,
                    )
                    attrs[attr_key] = attr_value
                elif input_type == "text" or input_type == "text64":
                    attr_value = ask_text(
                        message=description,
                        default=default_value,
                        validate=lambda attr_value: (
                            "Value must not be empty" if not attr_value else True
                        ),
                    )
                    attrs[attr_key] = attr_value
                elif input_type == "password":
                    attr_value = ask_password(
                        message=description,
                        default=default_value,
                        validate=lambda attr_value: (
                            "Value must not be empty" if not attr_value else True
                        ),
                    )
                    attrs[attr_key] = attr_value
                else:
                    msg(
                        level="error",
                        message=f"Error instantiating service {oneflow_template_name}. Input type {input_type} not supported for custom attribute {attr_key}",
                    )
            else:
                msg(
                    level="error",
                    message=f"Error instantiating service {oneflow_template_name}. Field type {field_type} not supported for custom attribute {attr_key}",
                )
        custom_attrs_values["custom_attrs_values"] = attrs
    networks = oneflow_template_networks(oneflow_template_name=oneflow_template_name)
    networks_values = {}
    networks_values_list = []
    if networks:
        nets = {}
        for (
            network_key,
            network_description,
        ) in networks.items():
            (
                field_type,
                input_type,
                description,
                default_value,
            ) = split_attr_description(attr_description=network_description)
            if field_type == "M":
                if input_type == "network":
                    vnet_name = ask_select(
                        message=description,
                        choices=onevnets_names(),
                    )
                    vnet_id = onevnet_id(vnet_name=vnet_name)
                    nets[network_key] = {"id": str(vnet_id)}
                    networks_values_list.append(nets)
                else:
                    msg(
                        level="error",
                        message=f"Error instantiating service {oneflow_template_name}. Input type {input_type} not supported for network",
                    )
            else:
                msg(
                    level="error",
                    message=f"Error instantiating service {oneflow_template_name}. Field type {field_type} not supported for network",
                )
        networks_values["networks_values"] = networks_values_list
    if custom_attrs_values:
        data.update(custom_attrs_values)
    if networks_values:
        data.update(networks_values)
    if data:
        custom_attrs_path = join_path(
            TEMP_DIRECTORY, f"{oneflow_template_name}_service_custom_attrs.json"
        )
        save_json_file(data=data, file_path=custom_attrs_path)
        command = f'oneflow-template instantiate "{oneflow_template_name}" < "{custom_attrs_path}"'
    else:
        command = f'oneflow-template instantiate "{oneflow_template_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not instantiate service {oneflow_template_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Service {oneflow_template_name} instantiated. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )
    sleep(5)
    # Capture the service ID from the instantiate command output
    service_id_match = re.search(r"ID:\s*(\d+)", stdout)
    if not service_id_match:
        msg(
            level="error",
            message=f"Could not get service ID from instantiate output: {stdout}",
        )
    service_id = int(service_id_match.group(1))
    service_name = oneflow_name_by_id(oneflow_id=service_id)
    
    state = oneflow_state_by_id(oneflow_id=service_id)
    msg(
        level="info",
        message=f"Instantiating service {service_name} (ID: {service_id}) in OpenNebula... It takes a few minutes",
    )
    while state != 2:
        sleep(20)
        state = oneflow_state_by_id(oneflow_id=service_id)
    
    # Use ID-based functions to avoid conflicts with services of the same name
    roles_vm_names = oneflow_roles_vm_names_by_id(oneflow_id=service_id)
    if roles_vm_names:
        for vm_name in roles_vm_names:
            onevm_chown(
                vm_name=vm_name,
                username=username,
                group_name=group_name,
            )
    oneflow_template_chown(
        oneflow_template_name=oneflow_template_name,
        username=username,
        group_name=group_name,
    )
    oneflow_chown_by_id(
        oneflow_id=service_id,
        username=username,
        group_name=group_name,
    )
    image_ids = oneflow_template_image_ids(oneflow_template_name=oneflow_template_name)
    template_ids = oneflow_template_ids(oneflow_template_name=oneflow_template_name)
    for template_id in template_ids:
        template_name = onetemplate_name(template_id=template_id)
        onetemplate_chown(
            template_name=template_name,
            username=username,
            group_name=group_name,
        )
    for image_id in image_ids:
        image_name = oneimage_name(image_id=image_id)
        oneimage_chown(
            image_name=image_name,
            username=username,
            group_name=group_name,
        )
    return service_name, service_id


def oneflow_template_networks(
    oneflow_template_name: str,
) -> Dict | None:
    """
    Get the networks of a service in OpenNebula

    :param oneflow_template_name: the name of the service, ``str``
    :return: the networks of the service, ``Dict``
    """
    oneflow_template = oneflow_template_show(
        oneflow_template_name=oneflow_template_name
    )
    if oneflow_template is None:
        msg(
            level="error",
            message=f"Service {oneflow_template_name} not found",
        )
    if (
        "DOCUMENT" not in oneflow_template
        or "TEMPLATE" not in oneflow_template["DOCUMENT"]
        or "BODY" not in oneflow_template["DOCUMENT"]["TEMPLATE"]
    ):
        msg(
            level="error",
            message=f"DOCUMENT key not found in service {oneflow_template_name} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE",
        )
    if "networks" not in oneflow_template["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(
            level="error",
            message=f"networks key not found in service {oneflow_template_name}",
        )
    networks = oneflow_template["DOCUMENT"]["TEMPLATE"]["BODY"]["networks"]
    if networks is None:
        return None
    return networks


def oneflow_template_roles(
    oneflow_template_name: str,
) -> List[Dict]:
    """
    Get the roles of a service in OpenNebula

    :param oneflow_template_name: the name of the service, ``str``
    :return: the roles of the service, ``List[Dict]``
    """
    oneflow_template = oneflow_template_show(
        oneflow_template_name=oneflow_template_name
    )
    if oneflow_template is None:
        msg(
            level="error",
            message=f"Service {oneflow_template_name} not found",
        )
    if (
        "DOCUMENT" not in oneflow_template
        or "TEMPLATE" not in oneflow_template["DOCUMENT"]
        or "BODY" not in oneflow_template["DOCUMENT"]["TEMPLATE"]
    ):
        msg(
            level="error",
            message=f"DOCUMENT key not found in service {oneflow_template_name} or TEMPLATE key not found in DOCUMENT or BODY key not found in TEMPLATE",
        )
    if "roles" not in oneflow_template["DOCUMENT"]["TEMPLATE"]["BODY"]:
        msg(
            level="error",
            message=f"roles key not found in service {oneflow_template_name}",
        )
    roles = oneflow_template["DOCUMENT"]["TEMPLATE"]["BODY"]["roles"]
    if roles is None:
        msg(
            level="error",
            message=f"Could not get roles of service {oneflow_template_name}",
        )
    return roles


def oneflow_template_show(
    oneflow_template_name: str,
) -> Dict | None:
    """
    Get the details of a service in OpenNebula

    :param oneflow_template_name: the name of the service, ``str``
    :return: the details of the service, ``Dict``
    """
    command = f'oneflow-template show "{oneflow_template_name}" -j'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"Service {oneflow_template_name} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"Service {oneflow_template_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


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


# ##############################################################################
# ##                           GROUP MANAGEMENT                               ##
# ##############################################################################


def check_group_admin(username: str, group_name: str) -> bool:
    """
    Check if user is admin of group in OpenNebula

    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    :return: if user is admin of group, ``bool``
    """
    group = onegroup_show(group_name=group_name)
    if group is None:
        msg(
            level="error",
            message=f"Group {group_name} not found",
        )
    if "GROUP" not in group or "ADMINS" not in group["GROUP"]:
        msg(
            level="error",
            message=f"GROUP key not found in group {group_name} or ADMINS key not found in GROUP",
        )
    if "ID" not in group["GROUP"]["ADMINS"]:
        return False
    elif isinstance(group["GROUP"]["ADMINS"]["ID"], str):
        user = oneusername(user_id=int(group["GROUP"]["ADMINS"]["ID"]))
        return user == username
    elif isinstance(group["GROUP"]["ADMINS"]["ID"], List):
        for user_id in group["GROUP"]["ADMINS"]["ID"]:
            user = oneusername(user_id=int(user_id))
            if user == username:
                return True
    else:
        msg(
            level="error",
            message=f"ADMINS key not found in group {group_name}",
        )
    return False


def onegroup_addadmin(username: str, group_name: str) -> None:
    """
    Assign user as admin to group in OpenNebula

    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    if check_group_admin(username=username, group_name=group_name):
        msg(
            level="debug",
            message=f"User {username} is already admin of group {group_name}",
        )
    else:
        command = f'onegroup addadmin "{group_name}" "{username}"'
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(
                level="error",
                message=f"Could not assign user {username} as admin to group {group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
            )
        msg(
            level="debug",
            message=f"User {username} assigned as admin to group {group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )


def onegroup_create(group_name: str) -> int:
    """
    Create a group in OpenNebula

    :param group_name: the name of the group, ``str``
    :return: the id of the group, ``int``
    """
    command = f'onegroup create "{group_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not create group {group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Group {group_name} created. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )
    return re.search(r"ID:\s*(\d+)", stdout).group(1)


def onegroup_id(group_name: str) -> int:
    """
    Get the id of a group in OpenNebula

    :param group_name: the name of the group, ``str``
    :return: the id of the group, ``int``
    """
    group = onegroup_show(group_name=group_name)
    if group is None:
        msg(
            level="error",
            message=f"Group {group_name} not found",
        )
    if "GROUP" not in group or "ID" not in group["GROUP"]:
        msg(
            level="error",
            message=f"GROUP key not found in group {group_name} or ID key not found in GROUP",
        )
    group_id = group["GROUP"]["ID"]
    if group_id is None:
        msg(
            level="error",
            message=f"Could not get id of group {group_name}",
        )
    return int(group_id)


def onegroup_list() -> Dict | None:
    """
    Get the list of groups in OpenNebula

    :return: the list of groups, ``Dict``
    """
    command = "onegroup list -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"OpenNebula groups not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"OpenNebula groups found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onegroup_show(group_name: str) -> Dict | None:
    """
    Get the details of a group in OpenNebula

    :param group_name: the name of the group, ``str``
    :return: the details of the group, ``Dict``
    """
    command = f'onegroup show "{group_name}" -j'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"Group {group_name} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"Group {group_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onegroups_names() -> List[str]:
    """
    Get the list of groups names in OpenNebula

    :return: the list of groups names, ``List[str]``
    """
    groups = onegroup_list()
    groups_names = []
    if groups is None:
        return []
    if "GROUP_POOL" not in groups or "GROUP" not in groups["GROUP_POOL"]:
        msg(
            level="error",
            message="GROUP_POOL key not found in groups or GROUP key not found in GROUP_POOL",
        )
    for group in groups["GROUP_POOL"]["GROUP"]:
        if group is None:
            msg(level="error", message="Group is empty")
        if "NAME" not in group:
            msg(
                level="error",
                message=f"NAME key not found in group {group}",
            )
        groups_names.append(group["NAME"])
    return groups_names


# ##############################################################################
# ##                            HOST MANAGEMENT                               ##
# ##############################################################################


def onehost_available_cpu(host_name: str) -> float:
    """
    Get the available percentage of CPU of a host in OpenNebula

    :param host_name: the name of the host, ``str``
    :return: the available percentage of CPU of the host, ``float``
    """
    host = onehost_show(host_name=host_name)
    if host is None:
        msg(
            level="error",
            message=f"Host {host_name} not found",
        )
    if "HOST" not in host or "HOST_SHARE" not in host["HOST"]:
        msg(
            level="error",
            message=f"HOST key not found in host {host_name} or HOST_SHARE key not found in HOST",
        )
    if (
        "CPU_USAGE" not in host["HOST"]["HOST_SHARE"]
        or "TOTAL_CPU" not in host["HOST"]["HOST_SHARE"]
    ):
        msg(
            level="error",
            message=f"CPU_USAGE key not found in host {host_name} or TOTAL_CPU key not found in HOST",
        )
    cpu_usage = int(host["HOST"]["HOST_SHARE"]["CPU_USAGE"])
    total_cpu = int(host["HOST"]["HOST_SHARE"]["TOTAL_CPU"])
    if cpu_usage is None or total_cpu is None:
        msg(
            level="error",
            message=f"Could not get CPU usage of host {host_name}",
        )
    return round((total_cpu - cpu_usage) / total_cpu * 100, 2)


def onehost_available_mem(host_name: str) -> float:
    """
    Get the available percentage of memory of a host in OpenNebula

    :param host_name: the name of the host, ``str``
    :return: the available percentage of memory of the host, ``float``
    """
    host = onehost_show(host_name=host_name)
    if host is None:
        msg(
            level="error",
            message=f"Host {host_name} not found",
        )
    if "HOST" not in host or "HOST_SHARE" not in host["HOST"]:
        msg(
            level="error",
            message=f"HOST key not found in host {host_name} or HOST_SHARE key not found in HOST",
        )
    if (
        "MEM_USAGE" not in host["HOST"]["HOST_SHARE"]
        or "TOTAL_MEM" not in host["HOST"]["HOST_SHARE"]
    ):
        msg(
            level="error",
            message=f"MEM_USAGE key not found in host {host_name} or TOTAL_MEM key not found in HOST",
        )
    mem_usage = int(host["HOST"]["HOST_SHARE"]["MEM_USAGE"])
    total_mem = int(host["HOST"]["HOST_SHARE"]["TOTAL_MEM"])
    if mem_usage is None or total_mem is None:
        msg(
            level="error",
            message=f"Could not get memory usage of host {host_name}",
        )
    return round((total_mem - mem_usage) / total_mem * 100, 2)


def onehost_cpu_model(host_name: str) -> str:
    """
    Get the CPU model of a host in OpenNebula

    :param host_name: the name of the host, ``str``
    :return: the CPU model of the host, ``str``
    """
    host = onehost_show(host_name=host_name)
    if host is None:
        msg(
            level="error",
            message=f"Host {host_name} not found",
        )
    if "HOST" not in host or "TEMPLATE" not in host["HOST"]:
        msg(
            level="error",
            message=f"HOST key not found in host {host_name} or TEMPLATE key not found in HOST",
        )
    if "KVM_CPU_MODEL" not in host["HOST"]["TEMPLATE"]:
        msg(
            level="error",
            message=f"KVM_CPU_MODEL key not found in host {host_name}",
        )
    cpu_model = host["HOST"]["TEMPLATE"]["KVM_CPU_MODEL"]
    if cpu_model is None:
        msg(
            level="error",
            message=f"Could not get CPU model of host {host_name}",
        )
    return cpu_model


def onehost_list() -> Dict | None:
    """
    Get the list of hosts in OpenNebula

    :return: the list of hosts, ``Dict``
    """
    command = "onehost list -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"OpenNebula hosts not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"OpenNebula hosts found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onehost_show(host_name: str) -> Dict | None:
    """
    Get the details of a host in OpenNebula

    :param host_name: the name of the host, ``str``
    :return: the details of the host, ``Dict``
    """
    command = f'onehost show "{host_name}" -j'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"Host {host_name} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"Host {host_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onehosts_avx_cpu_mem(
    min_percentage_cpu_available_host: int, min_percentage_mem_available_host: int
) -> List[str]:
    """
    Get the list of hosts with AVX support in OpenNebula

    :param min_percentage_cpu_available_host: the minimum percentage of CPU available in the host, ``int``
    :param min_percentage_mem_available_host: the minimum percentage of memory available in the host, ``int``
    :return: the list of hosts with AVX support, ``List[str]``
    """
    hosts = onehost_list()
    hosts_with_avx = []
    if "HOST_POOL" not in hosts or "HOST" not in hosts["HOST_POOL"]:
        msg(
            level="error",
            message="HOST_POOL key not found in hosts or HOST key not found in HOST_POOL",
        )
    hosts_pool = hosts["HOST_POOL"]["HOST"]
    if not hosts_pool:
        msg(level="error", message="Hosts list is empty")
    elif isinstance(hosts_pool, Dict):
        if (
            "NAME" not in hosts_pool
            or "TEMPLATE" not in hosts_pool
            or "KVM_CPU_FEATURES" not in hosts_pool["TEMPLATE"]
        ):
            msg(
                level="error",
                message="TEMPLATE key not found in host or NAME key not found in host or KVM_CPU_FEATURES key not found in TEMPLATE",
            )
        host_name = hosts_pool["NAME"]
        kvm_cpu_features = hosts_pool["TEMPLATE"]["KVM_CPU_FEATURES"]
        if (
            onehost_available_cpu(host_name=host_name)
            >= min_percentage_cpu_available_host
            and onehost_available_mem(host_name=host_name)
            >= min_percentage_mem_available_host
            and "avx" in kvm_cpu_features
        ):
            hosts_with_avx.append(host_name)
    elif isinstance(hosts_pool, List):
        for host in hosts_pool:
            if (
                "NAME" not in host
                or "TEMPLATE" not in host
                or "KVM_CPU_FEATURES" not in host["TEMPLATE"]
            ):
                msg(
                    level="error",
                    message="TEMPLATE key not found in host or NAME key not found in host or KVM_CPU_FEATURES key not found in TEMPLATE",
                )
            host_name = host["NAME"]
            kvm_cpu_features = host["TEMPLATE"]["KVM_CPU_FEATURES"]
            if (
                onehost_available_cpu(host_name=host_name)
                >= min_percentage_cpu_available_host
                and onehost_available_mem(host_name=host_name)
                >= min_percentage_mem_available_host
                and "avx" in kvm_cpu_features
            ):
                hosts_with_avx.append(host_name)
    else:
        msg(level="error", message="Hosts not found")
    return hosts_with_avx


# ##############################################################################
# ##                          IMAGES MANAGEMENT                               ##
# ##############################################################################


def oneimage_chown(image_name: str, username: str, group_name: str) -> None:
    """
    Change the owner of an image in OpenNebula

    :param image_name: the name of the image, ``str``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f'oneimage chown "{image_name}" "{username}" "{group_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not change owner of image {image_name} to {username}:{group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Owner of image {image_name} changed to {username}:{group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def oneimage_name(image_id: int) -> str:
    """
    Get the name of an image in OpenNebula

    :param image_id: the id of the image, ``int``
    :return: the name of the image, ``str``
    """
    image = oneimage_show(image_id=image_id)
    if image is None:
        msg(
            level="error",
            message=f"Image with id {image_id} not found",
        )
    if "IMAGE" not in image or "NAME" not in image["IMAGE"]:
        msg(
            level="error",
            message=f"IMAGE key not found in image id {image_id} or NAME key not found in IMAGE",
        )
    image_name = image["IMAGE"]["NAME"]
    if image_name is None:
        msg(
            level="error",
            message=f"Could not get name of image with id {image_id}",
        )
    return image_name


def oneimage_id_by_name(image_name: str) -> Optional[int]:
    """
    Get the ID of an image in OpenNebula by its name

    :param image_name: the name of the image, ``str``
    :return: the ID of the image, ``Optional[int]``
    """
    image = oneimage_show(image_name=image_name)
    if image is None:
        return None
    if "IMAGE" not in image or "ID" not in image["IMAGE"]:
        return None
    return int(image["IMAGE"]["ID"])


def oneimage_delete(image_name: str) -> None:
    """
    Remove an image in OpenNebula

    :param image_name: the name of the image, ``str``
    """
    command = f'oneimage delete "{image_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not remove image {image_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Image {image_name} removed. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def oneimage_list() -> Dict | None:
    """
    Get the list of images in OpenNebula

    :return: the list of images, ``Dict``
    """
    command = "oneimage list -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"OpenNebula images not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"OpenNebula images found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        stdout = loads_json(data=stdout)
        if "IMAGE_POOL" in stdout and "IMAGE" not in stdout["IMAGE_POOL"]:
            return None
        return stdout


def oneimage_rename(old_name: str, new_name: str) -> None:
    """
    Rename an image in OpenNebula

    :param old_name: the old name of the image, ``str``
    :param new_name: the new name of the image, ``str``
    """
    command = f'oneimage rename "{old_name}" "{new_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not rename image {old_name} to {new_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Image {old_name} renamed to {new_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def oneimage_show(
    image_name: Optional[str] = None,
    image_id: Optional[int] = None,
) -> Dict | None:
    """
    Get the details of an image in OpenNebula

    :param image_name: the name of the image, ``str``
    :param image_id: the id of the image, ``int``
    :return: the details of the image, ``Dict``
    """
    if image_id is None and image_name is None:
        msg(
            level="error",
            message="Either image_name or image_id must be provided",
        )
    if image_id is not None and image_name is not None:
        msg(
            level="error",
            message="Either image_name or image_id must be provided, not both",
        )
    if image_name is None:
        command = f"oneimage show {image_id} -j"
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(
                level="debug",
                message=f"Image with id {image_id} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
            )
            return None
        else:
            msg(
                level="debug",
                message=f"Image with id {image_id} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
            )
            return loads_json(data=stdout)
    else:
        command = f'oneimage show "{image_name}" -j'
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(
                level="debug",
                message=f"Image {image_name} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
            )
            return None
        else:
            msg(
                level="debug",
                message=f"Image {image_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
            )
            return loads_json(data=stdout)


def oneimage_state(image_name: str) -> str:
    """
    Get the status of an image in OpenNebula

    :param image_name: the name of the image, ``str``
    :return: the status of the image, ``str``
    """
    image = oneimage_show(image_name=image_name)
    if image is None:
        msg(
            level="error",
            message=f"Image {image_name} not found",
        )
    if "IMAGE" not in image or "STATE" not in image["IMAGE"]:
        msg(
            level="error",
            message=f"Could not get state of image with name {image_name}",
        )
    image_state = image["IMAGE"]["STATE"]
    if image_state is None:
        msg(
            level="error",
            message=f"Could not get state of image with name {image_name}",
        )
    return image_state


def oneimage_update(
    image_name: str,
    file_path: str,
) -> None:
    """
    Update an image in OpenNebula

    :param image_name: the name of the image, ``str``
    :param file_path: the path to the file with params, ``str``
    """
    command = f'oneimage update "{image_name}" --append {file_path}'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not update image {image_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Image {image_name} updated. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def oneimage_version(image_name: str) -> str:
    """
    Get the version of an image in OpenNebula

    :param image_name: the name of the image, ``str``
    :return: the version of the image, ``str``
    """
    image = oneimage_show(image_name=image_name)
    if image is None:
        msg(
            level="error",
            message=f"Image {image_name} not found",
        )
    if "IMAGE" not in image or "TEMPLATE" not in image["IMAGE"]:
        msg(
            level="error",
            message=f"Could not get version of image with name {image_name}",
        )
    if (
        "ONE_6GSB_MARKETPLACE_APPLIANCE_VERSION" not in image["IMAGE"]["TEMPLATE"]
        or "ONE_6GSB_MARKETPLACE_APPLIANCE_SOFTWARE_VERSION"
        not in image["IMAGE"]["TEMPLATE"]
    ):
        msg(
            level="error",
            message=f"Could not get version of image with name {image_name}",
        )
    image_version = f"{image['IMAGE']['TEMPLATE']['ONE_6GSB_MARKETPLACE_APPLIANCE_VERSION']}-{image['IMAGE']['TEMPLATE']['ONE_6GSB_MARKETPLACE_APPLIANCE_SOFTWARE_VERSION']}"
    if image_version is None:
        msg(
            level="error",
            message=f"Could not get version of image with name {image_name}",
        )
    return image_version


def oneimages_attribute(attribute: str, value: str) -> List[str]:
    """
    Check if an attribute is available in image in OpenNebula

    :param attribute: the attribute to check, ``str``
    :param value: the value of the attribute, ``str``
    :return: the names of the images with the attribute, ``List[str]``
    """
    images = oneimage_list()
    images_names = []
    if not images:
        return images_names
    if "IMAGE_POOL" not in images or "IMAGE" not in images["IMAGE_POOL"]:
        msg(
            level="error",
            message="IMAGE_POOL key not found in images or IMAGE key not found in IMAGE_POOL",
        )
    for image in images["IMAGE_POOL"]["IMAGE"]:
        if image is None:
            msg(level="error", message="Image is empty")
        if "NAME" not in image or "TEMPLATE" not in image:
            msg(
                level="error",
                message=f"NAME key not found in image {image} or TEMPLATE key not found in image",
            )
        if attribute in image["TEMPLATE"]:
            if image["TEMPLATE"][attribute] == value:
                image_name = image["NAME"]
                images_names.append(image_name)
    return images_names


def oneimages_names() -> List[str]:
    """
    Get the names of the images in OpenNebula

    :return: the names of the images, ``List[str]``
    """
    images = oneimage_list()
    images_names = []
    if images is None:
        return []
    if "IMAGE_POOL" not in images or "IMAGE" not in images["IMAGE_POOL"]:
        msg(
            level="error",
            message="IMAGE_POOL key not found in images or IMAGE key not found in IMAGE_POOL",
        )
    for image in images["IMAGE_POOL"]["IMAGE"]:
        if image is None:
            msg(level="error", message="Image is empty")
        if "NAME" not in image:
            msg(
                level="error",
                message=f"NAME key not found in image {image}",
            )
        images_names.append(image["NAME"])
    return images_names


# ##############################################################################
# ##                       MARKETPLACE MANAGEMENT                             ##
# ##############################################################################


def get_marketplace_monitoring_interval() -> int:
    """
    Get the monitoring interval of the marketplace

    :return: the interval in seconds, ``int``
    """
    oned_conf_path = get_oned_conf_path()
    oned_conf = load_file(file_path=oned_conf_path)
    match = re.search(
        r"^\s*MONITORING_INTERVAL_MARKET\s*=\s*\"?(\d+)\"?",
        oned_conf,
        re.MULTILINE,
    )
    if match is None:
        msg(
            level="error",
            message="Could not get marketplace monitoring interval",
        )
    data = int(match.group(1))
    msg(
        level="debug",
        message=f"Marketplace monitoring interval is {data}",
    )
    return data


def update_marketplace_monitoring_interval(
    interval: int,
) -> None:
    """
    Update the monitoring interval of the marketplace

    :param interval: the interval in seconds, ``int``
    """
    oned_conf_path = get_oned_conf_path()
    oned_conf = load_file(file_path=oned_conf_path)
    pattern = r"^\s*MONITORING_INTERVAL_MARKET\s*=\s*\"?(\d+)\"?"
    updated_conf = re.sub(
        pattern,
        f"MONITORING_INTERVAL_MARKET = {interval}",
        oned_conf,
        flags=re.MULTILINE,
    )
    save_file(data=updated_conf, file_path=oned_conf_path)
    msg(
        level="debug",
        message=f"OpenNebula marketplace monitoring interval updated to {interval}",
    )


def onemarket_create(
    marketplace_name: str,
    marketplace_description: str,
    marketplace_endpoint: str,
    marketplace_monitoring_interval: int,
) -> int | None:
    """
    Add a marketplace in OpenNebula

    :param marketplace_name: the name of the marketplace, ``str``
    :param marketplace_description: the description of the marketplace, ``str``
    :param marketplace_endpoint: the endpoint of the marketplace, ``str``
    :param marketplace_monitoring_interval: the interval to refresh the marketplace, ``int``
    :return: the id of the marketplace, ``int``
    """
    marketplace_content = dedent(f"""
        NAME = "{marketplace_name}"
        DESCRIPTION = "{marketplace_description}"
        ENDPOINT = "{marketplace_endpoint}"
        MARKET_MAD = one
    """).strip()
    marketplace_content_path = join_path(
        TEMP_DIRECTORY, f"{marketplace_name}_marketplace_content"
    )
    save_file(
        data=marketplace_content,
        file_path=marketplace_content_path,
    )
    command = f"onemarket create {marketplace_content_path}"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not create marketplace {marketplace_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    else:
        msg(
            level="debug",
            message=f"Marketplace {marketplace_name} created. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        marketplace_old_monitoring_interval = get_marketplace_monitoring_interval()
        update_marketplace_monitoring_interval(interval=marketplace_monitoring_interval)
        restart_one()
        sleep(marketplace_monitoring_interval + 5)
        check_one_health()
        update_marketplace_monitoring_interval(
            interval=marketplace_old_monitoring_interval
        )
        restart_one()
        check_one_health()
        return int(re.search(r"ID:\s*(\d+)", stdout).group(1))
    return None


def onemarket_endpoint(marketplace_name: str) -> str:
    """
    Get the URL of a marketplace in OpenNebula

    :param marketplace_name: the name of the market, ``str``
    :return: the URL of the marketplace, ``str``
    """
    marketplace = onemarket_show(marketplace_name=marketplace_name)
    if marketplace is None:
        msg(
            level="error",
            message=f"Marketplace {marketplace_name} not found",
        )
    if (
        "MARKETPLACE" not in marketplace
        or "TEMPLATE" not in marketplace["MARKETPLACE"]
        or "ENDPOINT" not in marketplace["MARKETPLACE"]["TEMPLATE"]
    ):
        msg(
            level="error",
            message=f"MARKETPLACE key not found in marketplace {marketplace_name} or TEMPLATE key not found in MARKETPLACE or ENDPOINT key not found in TEMPLATE",
        )
    marketplace_endpoint = marketplace["MARKETPLACE"]["TEMPLATE"]["ENDPOINT"]
    if marketplace_endpoint is None:
        msg(
            level="error",
            message=f"Could not get URL of marketplace {marketplace_name}",
        )
    return marketplace_endpoint


def onemarket_list() -> Dict | None:
    """
    Get the list of marketplaces in OpenNebula

    :return: the list of marketplaces, ``Dict``
    """
    command = "onemarket list -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"OpenNebula marketplaces not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"OpenNebula marketplaces found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onemarket_show(marketplace_name: str) -> Dict | None:
    """
    Get the details of a marketplace in OpenNebula

    :param marketplace_name: the name of the market, ``str``
    :return: the details of the marketplace, ``Dict``
    """
    command = f'onemarket show "{marketplace_name}" -j'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"Marketplace {marketplace_name} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"Marketplace {marketplace_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onemarkets_names() -> List[str]:
    """
    Get the list of marketplaces names in OpenNebula

    :return: the list of marketplaces names, ``List[str]``
    """
    marketplaces = onemarket_list()
    marketplaces_names = []
    if marketplaces is None:
        return []
    if (
        "MARKETPLACE_POOL" not in marketplaces
        or "MARKETPLACE" not in marketplaces["MARKETPLACE_POOL"]
    ):
        msg(
            level="error",
            message="MARKETPLACE_POOL key not found in marketplaces or MARKETPLACE key not found in MARKETPLACE_POOL",
        )
    for marketplace in marketplaces["MARKETPLACE_POOL"]["MARKETPLACE"]:
        if marketplace is None:
            msg(level="error", message="Marketplace is empty")
        if "NAME" not in marketplace:
            msg(
                level="error",
                message=f"NAME key not found in marketplace {marketplace}",
            )
        marketplaces_names.append(marketplace["NAME"])
    return marketplaces_names


# ##############################################################################
# ##                        MARKETAPP MANAGEMENT                              ##
# ##############################################################################


def onemarketapp_add(
    group_name: str,
    username: str,
    marketplace_name: str,
    appliance_url: str,
) -> Tuple[bool, str, Optional[int], Optional[int]]:
    """
    Add appliances from a marketplace in OpenNebula

    :param group_name: the name of the group, ``str``
    :param username: the name of the user, ``str``
    :param marketplace_name: the name of the marketplace, ``str``
    :param appliance_url: the URL of the appliance, ``str``
    :return: a tuple with a boolean indicating if the appliance is added, the name of the appliance,
             the template_id (or None), and the image_id (or None), ``Tuple[bool, str, Optional[int], Optional[int]]``
    """
    is_added = False
    returned_template_id = None
    returned_image_id = None
    appliance_name = onemarketapp_name(appliance_url=appliance_url)
    appliance_description = onemarketapp_description(appliance_url=appliance_url)
    appliance_software_version, appliance_version = onemarketapp_version(
        appliance_url=appliance_url
    )
    version = f"{appliance_version}-{appliance_software_version}"
    version_attribute_template = dedent(f"""
        ONE_6GSB_MARKETPLACE_APPLIANCE_NAME="{appliance_name}"
        ONE_6GSB_MARKETPLACE_APPLIANCE_VERSION="{appliance_version}"
        ONE_6GSB_MARKETPLACE_APPLIANCE_SOFTWARE_VERSION="{appliance_software_version}"
    """).strip()
    version_attribute_template_path = join_path(
        TEMP_DIRECTORY, "version_attribute_template"
    )
    save_file(
        data=version_attribute_template,
        file_path=version_attribute_template_path,
    )
    appliance_type = onemarketapp_type(
        appliance_name=appliance_name,
        marketplace_name=marketplace_name,
    )
    if appliance_type == "IMAGE":  # one image and one template
        image_name = oneimages_attribute(
            attribute="ONE_6GSB_MARKETPLACE_APPLIANCE_NAME", value=appliance_name
        )
        if not image_name:
            add_appliance = ask_confirm(
                message=(
                    f"No image has been found with the attribute ONE_6GSB_MARKETPLACE_APPLIANCE_NAME={appliance_name}. Do you want to add {appliance_name} appliance? \n{appliance_description}"
                ),
                default=False,
            )
            if add_appliance:
                datastores_names = onedatastores_names()
                datastore_name = ask_select(
                    message=f"Select the datastore where you want to store the image {appliance_name}:",
                    choices=datastores_names,
                )
                image_id, template_id, _ = onemarketapp_export(
                    appliance_name=appliance_name,
                    appliance_new_name=f"{appliance_name} {version}",
                    datastore_name=datastore_name,
                )
                appliance_name = f"{appliance_name} {version}"
                sleep(5)
                image_name = oneimage_name(image_id=image_id[0])
                image_state = oneimage_state(image_name=image_name)
                msg(
                    level="info", message=f"Wait for the image {image_name} to be ready"
                )
                while image_state != "1":
                    sleep(10)
                    image_state = oneimage_state(image_name=image_name)
                    if image_state == "5":
                        msg(
                            level="error",
                            message=f"Image {image_name} is in error state",
                        )
                oneimage_update(
                    image_name=image_name, file_path=version_attribute_template_path
                )
                onetemplate_chown(
                    template_name=appliance_name,
                    username=username,
                    group_name=group_name,
                )
                oneimage_chown(
                    image_name=appliance_name,
                    username=username,
                    group_name=group_name,
                )
                is_added = True
        else:
            msg(
                level="info",
                message=f"Image {appliance_name} already exists. Check if new version are available",
            )
            image_name = image_name[0]
            old_version = oneimage_version(image_name=image_name)
            if old_version != version:
                add_appliance = ask_confirm(
                    message=(
                        f"New version of {appliance_name} appliance is available. Do you want to update the appliance? \n{appliance_description}"
                    ),
                    default=False,
                )
                if add_appliance:
                    datastores_names = onedatastores_names()
                    datastore_name = ask_select(
                        message=f"Select the datastore where you want to store the image {appliance_name}:",
                        choices=datastores_names,
                    )
                    image_id, template_id, _ = onemarketapp_export(
                        appliance_name=appliance_name,
                        appliance_new_name=f"{appliance_name} {version}",
                        datastore_name=datastore_name,
                    )
                    appliance_name = f"{appliance_name} {version}"
                    sleep(5)
                    image_name = oneimage_name(image_id=image_id[0])
                    image_state = oneimage_state(image_name=image_name)
                    msg(
                        level="info",
                        message=f"Wait for the image {image_name} to be ready",
                    )
                    while image_state != "1":
                        sleep(10)
                        image_state = oneimage_state(image_name=image_name)
                        if image_state == "5":
                            msg(
                                level="error",
                                message=f"Image {image_name} is in error state",
                            )
                    oneimage_update(
                        image_name=image_name, file_path=version_attribute_template_path
                    )
                    onetemplate_chown(
                        template_name=appliance_name,
                        username=username,
                        group_name=group_name,
                    )
                    oneimage_chown(
                        image_name=appliance_name,
                        username=username,
                        group_name=group_name,
                    )
                else:
                    appliance_name = f"{appliance_name} {old_version}"
                    onetemplate_chown(
                        template_name=image_name,
                        username=username,
                        group_name=group_name,
                    )
                    oneimage_chown(
                        image_name=image_name,
                        username=username,
                        group_name=group_name,
                    )
            else:
                appliance_name = f"{appliance_name} {old_version}"
                onetemplate_chown(
                    template_name=image_name,
                    username=username,
                    group_name=group_name,
                )
                oneimage_chown(
                    image_name=image_name,
                    username=username,
                    group_name=group_name,
                )
            is_added = True
    elif appliance_type == "VM":  # one or more images and one template
        images_names = oneimages_attribute(
            attribute="ONE_6GSB_MARKETPLACE_APPLIANCE_NAME", value=appliance_name
        )
        if not images_names:
            add_appliance = ask_confirm(
                message=(
                    f"No image has been found with the attribute ONE_6GSB_MARKETPLACE_APPLIANCE_NAME={appliance_name}. Do you want to add {appliance_name} appliance? \n{appliance_description}"
                ),
                default=False,
            )
            if add_appliance:
                datastores_names = onedatastores_names()
                datastore_name = ask_select(
                    message=f"Select the datastore where you want to store the image {appliance_name}:",
                    choices=datastores_names,
                )
                onemarketapp_export(
                    appliance_name=appliance_name,
                    appliance_new_name=f"{appliance_name} {version}",
                    datastore_name=datastore_name,
                )
                sleep(5)
                appliance_name = f"{appliance_name} {version}"
                onetemplate_chown(
                    template_name=appliance_name,
                    username=username,
                    group_name=group_name,
                )
                image_ids = onetemplate_image_ids(template_name=appliance_name)
                for image_id in image_ids:
                    image_name = oneimage_name(image_id=image_id)
                    image_state = oneimage_state(image_name=image_name)
                    msg(
                        level="info",
                        message=f"Wait for the image {image_name} to be ready",
                    )
                    while image_state != "1":
                        sleep(10)
                        image_state = oneimage_state(image_name=image_name)
                        if image_state == "5":
                            msg(
                                level="error",
                                message=f"Image {image_name} is in error state",
                            )
                    oneimage_update(
                        image_name=image_name,
                        file_path=version_attribute_template_path,
                    )
                    oneimage_chown(
                        image_name=image_name,
                        username=username,
                        group_name=group_name,
                    )
                is_added = True
        else:
            msg(
                level="info",
                message=f"Image {appliance_name} already exists. Check if new version are available",
            )
            image_name = images_names[0]
            old_version = oneimage_version(image_name=image_name)
            if old_version != version:
                add_appliance = ask_confirm(
                    message=(
                        f"New version of {appliance_name} appliance is available. Do you want to update the appliance? \n{appliance_description}"
                    ),
                    default=False,
                )
                if add_appliance:
                    datastores_names = onedatastores_names()
                    datastore_name = ask_select(
                        message=f"Select the datastore where you want to store the image {appliance_name}:",
                        choices=datastores_names,
                    )
                    onemarketapp_export(
                        appliance_name=appliance_name,
                        appliance_new_name=f"{appliance_name} {version}",
                        datastore_name=datastore_name,
                    )
                    sleep(5)
                    appliance_name = f"{appliance_name} {version}"
                    onetemplate_chown(
                        template_name=appliance_name,
                        username=username,
                        group_name=group_name,
                    )
                    image_ids = onetemplate_image_ids(template_name=appliance_name)
                    for image_id in image_ids:
                        image_name = oneimage_name(image_id=image_id)
                        image_state = oneimage_state(image_name=image_name)
                        msg(
                            level="info",
                            message=f"Wait for the image {image_name} to be ready",
                        )
                        while image_state != "1":
                            sleep(10)
                            image_state = oneimage_state(image_name=image_name)
                            if image_state == "5":
                                msg(
                                    level="error",
                                    message=f"Image {image_name} is in error state",
                                )
                        oneimage_update(
                            image_name=image_name,
                            file_path=version_attribute_template_path,
                        )
                        oneimage_chown(
                            image_name=image_name,
                            username=username,
                            group_name=group_name,
                        )
                else:
                    appliance_name = f"{appliance_name} {old_version}"
                    onetemplate_chown(
                        template_name=image_name,
                        username=username,
                        group_name=group_name,
                    )
                    for image_name in images_names:
                        oneimage_chown(
                            image_name=image_name,
                            username=username,
                            group_name=group_name,
                        )
            else:
                appliance_name = f"{appliance_name} {old_version}"
                onetemplate_chown(
                    template_name=image_name,
                    username=username,
                    group_name=group_name,
                )
                for image_name in images_names:
                    oneimage_chown(
                        image_name=image_name,
                        username=username,
                        group_name=group_name,
                    )
            is_added = True
    else:
        images_names = oneimages_attribute(
            attribute="ONE_6GSB_MARKETPLACE_APPLIANCE_NAME", value=appliance_name
        )
        if not images_names:
            add_appliance = ask_confirm(
                message=(
                    f"No image has been found with the attribute ONE_6GSB_MARKETPLACE_APPLIANCE_NAME={appliance_name}. Do you want to add {appliance_name} appliance? \n{appliance_description}"
                ),
                default=False,
            )
            if add_appliance:
                datastores_names = onedatastores_names()
                datastore_name = ask_select(
                    message=f"Select the datastore where you want to store the image {appliance_name}:",
                    choices=datastores_names,
                )
                _, template_ids, _ = onemarketapp_export(
                    appliance_name=appliance_name,
                    appliance_new_name=f"{appliance_name} {version}",
                    datastore_name=datastore_name,
                )
                sleep(5)
                appliance_name = f"{appliance_name} {version}"
                image_ids = oneflow_template_image_ids(
                    oneflow_template_name=appliance_name
                )
                for template_id in template_ids:
                    template_name = onetemplate_name(template_id=template_id)
                    onetemplate_chown(
                        template_name=template_name,
                        username=username,
                        group_name=group_name,
                    )
                for image_id in image_ids:
                    image_name = oneimage_name(image_id=image_id)
                    image_state = oneimage_state(image_name=image_name)
                    msg(
                        level="info",
                        message=f"Wait for the image {image_name} to be ready",
                    )
                    while image_state != "1":
                        sleep(10)
                        image_state = oneimage_state(image_name=image_name)
                        if image_state == "5":
                            msg(
                                level="error",
                                message=f"Image {image_name} is in error state",
                            )
                    oneimage_update(
                        image_name=image_name,
                        file_path=version_attribute_template_path,
                    )
                    oneimage_chown(
                        image_name=image_name,
                        username=username,
                        group_name=group_name,
                    )
                is_added = True
        else:
            msg(
                level="info",
                message=f"Image {appliance_name} already exists. Check if new version are available",
            )
            image_name = images_names[0]
            old_version = oneimage_version(image_name=image_name)
            if old_version != version:
                add_appliance = ask_confirm(
                    message=(
                        f"New version of {appliance_name} appliance is available. Do you want to update the appliance? \n{appliance_description}"
                    ),
                    default=False,
                )
                if add_appliance:
                    datastores_names = onedatastores_names()
                    datastore_name = ask_select(
                        message=f"Select the datastore where you want to store the image {appliance_name}:",
                        choices=datastores_names,
                    )
                    onemarketapp_export(
                        appliance_name=appliance_name,
                        appliance_new_name=f"{appliance_name} {version}",
                        datastore_name=datastore_name,
                    )
                    sleep(5)
                    appliance_name = f"{appliance_name} {version}"
                    image_ids = oneflow_template_image_ids(
                        oneflow_template_name=appliance_name
                    )
                    template_ids = oneflow_template_ids(
                        oneflow_template_name=appliance_name
                    )
                    for template_id in template_ids:
                        template_name = onetemplate_name(template_id=template_id)
                        onetemplate_chown(
                            template_name=template_name,
                            username=username,
                            group_name=group_name,
                        )
                    for image_id in image_ids:
                        image_name = oneimage_name(image_id=image_id)
                        image_state = oneimage_state(image_name=image_name)
                        msg(
                            level="info",
                            message=f"Wait for the image {image_name} to be ready",
                        )
                        while image_state != "1":
                            sleep(10)
                            image_state = oneimage_state(image_name=image_name)
                            if image_state == "5":
                                msg(
                                    level="error",
                                    message=f"Image {image_name} is in error state",
                                )
                        oneimage_update(
                            image_name=image_name,
                            file_path=version_attribute_template_path,
                        )
                        oneimage_chown(
                            image_name=image_name,
                            username=username,
                            group_name=group_name,
                        )
                else:
                    appliance_name = f"{appliance_name} {old_version}"
                    image_ids = oneflow_template_image_ids(
                        oneflow_template_name=appliance_name
                    )
                    template_ids = oneflow_template_ids(
                        oneflow_template_name=appliance_name
                    )
                    oneflow_template_chown(
                        oneflow_template_name=appliance_name,
                        username=username,
                        group_name=group_name,
                    )
                    for template_id in template_ids:
                        onetemplate_chown(
                            template_name=onetemplate_name(template_id=template_id),
                            username=username,
                            group_name=group_name,
                        )
                    for image_id in image_ids:
                        oneimage_chown(
                            image_name=oneimage_name(image_id=image_id),
                            username=username,
                            group_name=group_name,
                        )
            else:
                appliance_name = f"{appliance_name} {old_version}"
                image_ids = oneflow_template_image_ids(
                    oneflow_template_name=appliance_name
                )
                template_ids = oneflow_template_ids(
                    oneflow_template_name=appliance_name
                )
                oneflow_template_chown(
                    oneflow_template_name=appliance_name,
                    username=username,
                    group_name=group_name,
                )
                for template_id in template_ids:
                    onetemplate_chown(
                        template_name=onetemplate_name(template_id=template_id),
                        username=username,
                        group_name=group_name,
                    )
                for image_id in image_ids:
                    oneimage_chown(
                        image_name=oneimage_name(image_id=image_id),
                        username=username,
                        group_name=group_name,
                    )
            is_added = True
    
    # If appliance was added, try to get the template_id and first image_id
    if is_added and appliance_type == "IMAGE":
        try:
            returned_template_id = onetemplate_id(template_name=appliance_name)
            returned_image_id = oneimage_id_by_name(image_name=appliance_name)
        except Exception:
            pass  # Keep None values if we can't get the IDs
    
    return is_added, appliance_name, returned_template_id, returned_image_id


def onemarketapp_instantiate(
    appliance_url: str, group_name: str, marketplace_name: str, username: str
) -> Tuple[bool, str, Optional[int], Optional[int]]:
    """
    Ask if user has instantiated an appliance in OpenNebula

    :param appliance_url: the URL of the appliance, ``str``
    :param group_name: the name of the group, ``str``
    :param marketplace_name: the name of the marketplace, ``str``
    :param username: the name of the user, ``str``
    :return: tuple with the status, name, optional service ID, and optional VM ID (for IMAGE type), ``Tuple[bool, str, Optional[int], Optional[int]]``
    """
    is_instantiated = False
    appliance_target_name = None
    service_id = None
    vm_id = None
    appliance_name = onemarketapp_name(appliance_url=appliance_url)
    appliance_type = onemarketapp_type(
        appliance_name=appliance_name,
        marketplace_name=marketplace_name,
    )
    instantiate_appliance = ask_confirm(
        message=f"Do yo have {appliance_name} instantiated in OpenNebula?",
        default=False,
    )
    if instantiate_appliance:
        if appliance_type == "IMAGE" or appliance_type == "VM":
            # Get running VMs with their IDs to avoid name conflicts
            vms_running_with_ids = onevms_running_with_ids()
            vm_name = ask_select(
                message=f"Since you have an instance of {appliance_name} in OpenNebula, can you select the name of the virtual machine? ",
                choices=list(vms_running_with_ids.keys()),
            )
            vm_id = vms_running_with_ids[vm_name]
            # Use ID-based functions from here to avoid conflicts with VMs of the same name
            if onevm_state_by_id(vm_id=vm_id) != "3":  # 3 means running
                msg(
                    level="error",
                    message=f"Virtual machine {vm_name} (ID: {vm_id}) is not in RUNNING state",
                )
            onevm_chown_by_id(
                vm_id=vm_id,
                username=username,
                group_name=group_name,
            )
            template_id = onevm_template_id(vm_name=vm_name)
            template_name = onetemplate_name(template_id=template_id)
            onetemplate_chown(
                template_name=template_name, username=username, group_name=group_name
            )
            image_ids = onetemplate_image_ids(template_name=template_name)
            for image_id in image_ids:
                image_name = oneimage_name(image_id=image_id)
                oneimage_chown(
                    image_name=image_name, username=username, group_name=group_name
                )
            appliance_target_name = vm_name
        else:
            service_name = ask_select(
                message=f"Since you have an instance of {appliance_name} in OpenNebula, can you select the name of the service instantiated?",
                choices=oneflows_names(),
            )
            service_id = oneflow_id(oneflow_name=service_name)
            # Use ID-based functions from here to avoid conflicts with services of the same name
            if oneflow_state_by_id(oneflow_id=service_id) != 2:  # 2 means running
                msg(
                    level="error",
                    message=f"Service {service_name} (ID: {service_id}) is not in RUNNING state",
                )
            roles_vm_names = oneflow_roles_vm_names_by_id(oneflow_id=service_id)
            if roles_vm_names:
                for vm_name in roles_vm_names:
                    onevm_chown(
                        vm_name=vm_name,
                        username=username,
                        group_name=group_name,
                    )
            oneflow_template_chown(
                oneflow_template_name=service_name,
                username=username,
                group_name=group_name,
            )
            oneflow_chown_by_id(
                oneflow_id=service_id,
                username=username,
                group_name=group_name,
            )
            image_ids = oneflow_template_image_ids(oneflow_template_name=service_name)
            template_ids = oneflow_template_ids(oneflow_template_name=service_name)
            for template_id in template_ids:
                template_name = onetemplate_name(template_id=template_id)
                onetemplate_chown(
                    template_name=template_name,
                    username=username,
                    group_name=group_name,
                )
            for image_id in image_ids:
                image_name = oneimage_name(image_id=image_id)
                oneimage_chown(
                    image_name=image_name,
                    username=username,
                    group_name=group_name,
                )
            appliance_target_name = service_name
        _, _, _, _ = onemarketapp_add(appliance_url=appliance_url, group_name=group_name, username=username, marketplace_name=marketplace_name)
        is_instantiated = True
    else:
        is_added, appliance_name, _, _ = onemarketapp_add(
            group_name=group_name,
            username=username,
            marketplace_name=marketplace_name,
            appliance_url=appliance_url,
        )
        if is_added:
            instantiate_appliance = ask_confirm(
                message=f"Do you want to instantiate the appliance {appliance_name} in OpenNebula?",
                default=False,
            )
            if instantiate_appliance:
                if appliance_type == "IMAGE" or appliance_type == "VM":
                    onetemplate_instantiate(
                        template_name=appliance_name,
                        username=username,
                        group_name=group_name,
                    )
                    appliance_target_name = appliance_name
                    # Get VM ID for IMAGE type appliances to avoid name conflicts later
                    vm_id = onevm_id(vm_name=appliance_name)
                else:
                    # oneflow_template_instantiate returns the actual service name and ID
                    appliance_target_name, service_id = oneflow_template_instantiate(
                        oneflow_template_name=appliance_name,
                        group_name=group_name,
                        username=username,
                    )
                is_instantiated = True
            else:
                appliance_target_name = appliance_name
        else:
            appliance_target_name = appliance_name
    return is_instantiated, appliance_target_name, service_id, vm_id


def onemarketapp_export(
    appliance_name: str, appliance_new_name: str, datastore_name: str
) -> Tuple[List[int], List[int], int]:
    """
    Export an appliance in OpenNebula

    :param appliance_name: the name of the appliance, ``str``
    :param appliance_new_name: the new name of the appliance, ``str``
    :param datastore_name: the name of the datastore, ``str``
    :return: the ids of the images, templates and services, ``Tuple[List[int], List[int], int]``
    """
    command = f'onemarketapp export "{appliance_name}" "{appliance_new_name}" --datastore "{datastore_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not export appliance {appliance_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Appliance {appliance_name} exported. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )
    image_ids = [
        int(id_)
        for id_ in re.findall(
            r"ID:\s*(\d+)",
            re.search(
                r"IMAGE\s*\n((?:\s*ID:\s*\d+\s*\n?)*)",
                stdout,
            ).group(1),
        )
    ]
    template_ids = [
        int(id_)
        for id_ in re.findall(
            r"ID:\s*(\d+)",
            re.search(
                r"VMTEMPLATE\s*\n((?:\s*ID:\s*\d+\s*\n?)*)",
                stdout,
            ).group(1),
        )
    ]
    match = re.search(r"SERVICE_TEMPLATE\s*\n(?:\s*ID:\s*(\d+))+", stdout)
    if match:
        service_id = int(match.group(1))
        msg(
            level="debug",
            message=f"Appliance {appliance_name} exported with image ids {image_ids}, template ids {template_ids} and service id {service_id}",
        )
    else:
        service_id = None
        msg(
            level="debug",
            message=f"Appliance {appliance_name} exported with image ids {image_ids} and template ids {template_ids}",
        )
    return image_ids, template_ids, service_id


def onemarketapp_curl(appliance_url: str) -> Dict:
    """
    Get the data of an appliance using the url in OpenNebula

    :param appliance_url: the url of the appliance, ``str``
    :return: the data of the appliance, ``Dict``
    """
    command = (
        f'curl -s -w "%{{http_code}}" -H "Accept: application/json" {appliance_url}'
    )
    stdout, stderr, rc = run_command(command=command)
    data, status_code = stdout[:-3].strip(), stdout[-3:]
    if status_code != "200":
        msg(
            level="error",
            message=f"Could not get appliance data from url {appliance_url}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    return loads_json(data=data)


def onemarketapp_description(appliance_url: str) -> str:
    """
    Get the description of an appliance using the url in OpenNebula

    :param appliance_url: the url of the appliance, ``str``
    :return: the description of the appliance, ``str``
    """
    appliance = onemarketapp_curl(appliance_url=appliance_url)
    if "description" not in appliance:
        msg(
            level="error",
            message=f"Could not get description of appliance from url {appliance_url}",
        )
    appliance_description = appliance["description"]
    if appliance_description is None:
        msg(
            level="error",
            message=f"Could not get description of appliance from url {appliance_url}",
        )
    return appliance_description


def onemarketapp_name(appliance_url: str) -> str:
    """
    Get the name of an appliance using the url in OpenNebula

    :param appliance_url: the url of the appliance, ``str``
    :return: the name of the appliance, ``str``
    """
    appliance = onemarketapp_curl(appliance_url=appliance_url)
    if "name" not in appliance:
        msg(
            level="error",
            message=f"Could not get name of appliance from url {appliance_url}",
        )
    appliance_name = appliance["name"]
    if appliance_name is None:
        msg(
            level="error",
            message=f"Could not get name of appliance from url {appliance_url}",
        )
    return appliance_name


def onemarketapp_show(appliance_name: str, marketplace_name: str) -> Dict:
    """
    Get the details of an appliance in OpenNebula

    :param appliance_name: the name of the appliance, ``str``
    :param marketplace_name: the name of the marketplace, ``str``
    :return: the details of the appliance, ``Dict``
    """
    command = f'onemarketapp show "{appliance_name}" -j'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"OpenNebula appliance {appliance_name} not found in marketplace {marketplace_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    else:
        msg(
            level="debug",
            message=f"OpenNebula appliance {appliance_name} found in marketplace {marketplace_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        appliance = loads_json(data=stdout)
        if (
            "MARKETPLACEAPP" not in appliance
            or "MARKETPLACE" not in appliance["MARKETPLACEAPP"]
        ):
            msg(
                level="error",
                message=f"MARKETPLACEAPP key not found in appliance {appliance_name} or MARKETPLACE key not found in MARKETPLACE",
            )
        if appliance["MARKETPLACEAPP"]["MARKETPLACE"] != marketplace_name:
            msg(
                level="error",
                message=f"Appliance {appliance_name} not in {marketplace_name} marketplace",
            )
        msg(
            level="debug",
            message=f"Appliance {appliance_name} found in {marketplace_name} marketplace",
        )
        return appliance


def onemarketapp_type(appliance_name: str, marketplace_name: str) -> str:
    """
    Get the type of an appliance in OpenNebula

    :param appliance_name: the name of the appliance, ``str``
    :param marketplace_name: the name of the marketplace, ``str``
    :return: the type of the appliance, ``str``
    """
    appliance = onemarketapp_show(
        appliance_name=appliance_name,
        marketplace_name=marketplace_name,
    )
    if "MARKETPLACEAPP" not in appliance or "TYPE" not in appliance["MARKETPLACEAPP"]:
        msg(
            level="error",
            message=f"MARKETPLACEAPP key not found in appliance {appliance_name} or TYPE key not found in MARKETPLACEAPP",
        )
    appliance_type = appliance["MARKETPLACEAPP"]["TYPE"]
    if appliance_type == "1":
        msg(
            level="debug",
            message=f"Appliance {appliance_name} is an IMAGE",
        )
        return "IMAGE"
    elif appliance_type == "2":
        msg(
            level="debug",
            message=f"Appliance {appliance_name} is a VM",
        )
        return "VM"
    elif appliance_type == "3":
        msg(
            level="debug",
            message=f"Appliance {appliance_name} is a SERVICE",
        )
        return "SERVICE"
    else:
        msg(
            level="error",
            message=f"Appliance {appliance_name} has unknown type",
        )


def onemarketapp_version(appliance_url: str) -> Tuple[str, str]:
    """
    Get the version of an appliance using the url in OpenNebula

    :param appliance_url: the url of the appliance, ``str``
    :return: the version and software version of the appliance, ``Tuple[str, str]``
    """
    appliance = onemarketapp_curl(appliance_url=appliance_url)

    if "version" not in appliance or appliance["version"] is None:
        msg(
            level="error",
            message=f"Could not get version of appliance from url {appliance_url}",
        )
        return "", ""

    appliance_version_full = appliance["version"]
    parts = appliance_version_full.split("-", 1)

    appliance_software_version = parts[0] if len(parts) > 0 else ""
    appliance_version = parts[1] if len(parts) > 1 else ""

    return appliance_software_version, appliance_version


# ##############################################################################
# ##                         TEMPLATE MANAGEMENT                              ##
# ##############################################################################


def onetemplate_chown(template_name: str, username: str, group_name: str) -> None:
    """
    Change the owner of a template in OpenNebula

    :param template_name: the name of the template, ``str``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f'onetemplate chown "{template_name}" "{username}" "{group_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not change owner of template {template_name} to {username}:{group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Owner of template {template_name} changed to {username}:{group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def onetemplate_delete(template_name: str) -> None:
    """
    Remove a template in OpenNebula

    :param template_name: the name of the template, ``str``
    """
    command = f'onetemplate delete "{template_name}" --recursive'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not remove template {template_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Template {template_name} removed. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def onetemplate_id(template_name: str) -> int:
    """
    Get the id of a template in OpenNebula

    :param template_name: the name of the template, ``str``
    :return: the id of the template, ``int``
    """
    template = onetemplate_show(template_name=template_name)
    if template is None:
        msg(
            level="error",
            message=f"Template {template_name} not found",
        )
    if "VMTEMPLATE" not in template or "ID" not in template["VMTEMPLATE"]:
        msg(
            level="error",
            message=f"VMTEMPLATE key not found in template {template_name} or ID key not found in VMTEMPLATE",
        )
    template_id = int(template["VMTEMPLATE"]["ID"])
    if template_id is None:
        msg(
            level="error",
            message=f"Could not get id of template {template_name}",
        )
    return template_id


def onetemplate_image_ids(
    template_name: Optional[str] = None,
    template_id: Optional[int] = None,
) -> List[int]:
    """
    Get the image id of a template in OpenNebula

    :param template_name: the name of the template, ``str``
    :param template_id: the id of the template, ``int``
    :return: the list of image ids, ``List[int]``
    """
    if template_id is None and template_name is None:
        msg(
            level="error",
            message="Either template_name or template_id must be provided",
        )
    if template_id is not None and template_name is not None:
        msg(
            level="error",
            message="Either template_name or template_id must be provided, not both",
        )
    if template_id is None:
        template = onetemplate_show(template_name=template_name)
        if template is None:
            msg(
                level="error",
                message=f"Template {template_name} not found",
            )
        if (
            "VMTEMPLATE" not in template
            or "TEMPLATE" not in template["VMTEMPLATE"]
            or "DISK" not in template["VMTEMPLATE"]["TEMPLATE"]
        ):
            msg(
                level="error",
                message=f"VMTEMPLATE key not found in template {template_name} or TEMPLATE key not found in VMTEMPLATE or DISK key not found in TEMPLATE",
            )
        template_image_ids = template["VMTEMPLATE"]["TEMPLATE"]["DISK"]
        image_ids = []
        if template_image_ids is None:
            msg(
                level="error",
                message=f"Could not get image id of template {template_name}",
            )
        elif isinstance(template_image_ids, Dict):
            if "IMAGE_ID" not in template_image_ids:
                msg(
                    level="error",
                    message="IMAGE_ID key not found in DISK",
                )
            image_ids.append(int(template_image_ids["IMAGE_ID"]))
        elif isinstance(template_image_ids, List):
            for disk in template_image_ids:
                if "IMAGE_ID" not in disk:
                    msg(
                        level="error",
                        message="IMAGE_ID key not found in DISK",
                    )
                image_ids.append(int(disk["IMAGE_ID"]))
        else:
            msg(
                level="error",
                message="Invalid type of DISK",
            )
        return image_ids
    else:
        template = onetemplate_show(template_id=template_id)
        if template is None:
            msg(
                level="error",
                message=f"Template with id {template_id} not found",
            )
        if (
            "VMTEMPLATE" not in template
            or "TEMPLATE" not in template["VMTEMPLATE"]
            or "DISK" not in template["VMTEMPLATE"]["TEMPLATE"]
        ):
            msg(
                level="error",
                message=f"VMTEMPLATE key not found in template id {template_id} or TEMPLATE key not found in VMTEMPLATE or DISK key not found in TEMPLATE",
            )
        template_image_ids = template["VMTEMPLATE"]["TEMPLATE"]["DISK"]
        image_ids = []
        if template_image_ids is None:
            msg(
                level="error",
                message=f"Could not get image id of template with id {template_id}",
            )
        elif isinstance(template_image_ids, Dict):
            if "IMAGE_ID" not in template_image_ids:
                msg(
                    level="error",
                    message="IMAGE_ID key not found in DISK",
                )
            image_ids.append(int(template_image_ids["IMAGE_ID"]))
        elif isinstance(template_image_ids, List):
            for disk in template_image_ids:
                if "IMAGE_ID" not in disk:
                    msg(
                        level="error",
                        message="IMAGE_ID key not found in DISK",
                    )
                image_ids.append(int(disk["IMAGE_ID"]))
        else:
            msg(
                level="error",
                message="Invalid type of DISK",
            )
        return image_ids


def onetemplate_instantiate(template_name: str, username: str, group_name: str) -> None:
    """
    Instantiate a template in OpenNebula

    :param template_name: the name of the template, ``str``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    user_inputs = onetemplate_user_inputs(template_name=template_name)
    if user_inputs:
        attrs = {}
        for attr_key, attr_description in user_inputs.items():
            (
                field_type,
                input_type,
                description,
                default_value,
            ) = split_attr_description(attr_description=attr_description)
            description = description + ":"
            if field_type == "O":
                if input_type == "boolean":
                    attr_value = ask_select(
                        message=description,
                        choices=["YES", "NO"],
                    )
                    attrs[attr_key] = attr_value
                elif input_type == "text" or input_type == "text64":
                    attr_value = ask_text(
                        message=description,
                        default=default_value,
                    )
                    attrs[attr_key] = attr_value
                elif input_type == "password":
                    attr_value = ask_password(
                        message=description,
                        default=default_value,
                    )
                    attrs[attr_key] = attr_value
                else:
                    msg(
                        level="error",
                        message=f"Error instantiating template {template_name}. Invalid input type {input_type}",
                    )
            elif field_type == "M":
                if input_type == "boolean":
                    attr_value = ask_select(
                        message=description,
                        choices=["YES", "NO"],
                        default=default_value,
                    )
                    attrs[attr_key] = attr_value
                elif input_type == "text" or input_type == "text64":
                    attr_value = ask_text(
                        message=description,
                        default=default_value,
                        validate=lambda attr_value: (
                            "Value must not be empty" if not attr_value else True
                        ),
                    )
                    attrs[attr_key] = attr_value
                elif input_type == "password":
                    attr_value = ask_password(
                        message=description,
                        default=default_value,
                        validate=lambda attr_value: (
                            "Value must not be empty" if not attr_value else True
                        ),
                    )
                    attrs[attr_key] = attr_value
                else:
                    msg(
                        level="error",
                        message=f"Error instantiating template {template_name}. Invalid input type {input_type}",
                    )
            else:
                msg(
                    level="error",
                    message=f"Error instantiating template {template_name}. Invalid field type {field_type}",
                )
        user_inputs = ",".join([f'"{key}={value}"' for key, value in attrs.items()])
        command = f'onetemplate instantiate "{template_name}" --name "{template_name}" --user-inputs {user_inputs}'
    else:
        command = f'onetemplate instantiate "{template_name}" --name "{template_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not instantiate template {template_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Template {template_name} instantiated. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )
    onevm_chown(vm_name=template_name, username=username, group_name=group_name)


def onetemplate_name(template_id: int) -> str:
    """
    Get the name of a template in OpenNebula

    :param template_id: the id of the template, ``int``
    :return: the name of the template, ``str``
    """
    template = onetemplate_show(template_id=template_id)
    if template is None:
        msg(
            level="error",
            message=f"Template with id {template_id} not found",
        )
    if "VMTEMPLATE" not in template or "NAME" not in template["VMTEMPLATE"]:
        msg(
            level="error",
            message=f"VMTEMPLATE key not found in template id {template_id} or NAME key not found in VMTEMPLATE",
        )
    template_name = template["VMTEMPLATE"]["NAME"]
    if template_name is None:
        msg(
            level="error",
            message=f"Could not get name of template with id {template_id}",
        )
    return template_name


def onetemplate_list() -> Dict | None:
    """
    Get the list of templates in OpenNebula

    :return: the list of templates, ``Dict``
    """
    command = "onetemplate list -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"OpenNebula templates not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"OpenNebula templates found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onetemplate_rename(old_name: str, new_name: str) -> None:
    """
    Rename a template in OpenNebula

    :param old_name: the old name of the template, ``str``
    :param new_name: the new name of the template, ``str``
    """
    command = f'onetemplate rename "{old_name}" "{new_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not rename template {old_name} to {new_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Template {old_name} renamed to {new_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def onetemplate_show(
    template_name: Optional[str] = None,
    template_id: Optional[int] = None,
) -> Dict | None:
    """
    Get the details of a template in OpenNebula

    :param template_name: the name of the template, ``str``
    :param template_id: the id of the template, ``int``
    :return: the details of the template, ``Dict``
    """
    if template_id is None and template_name is None:
        msg(
            level="error",
            message="Either template_name or template_id must be provided",
        )
    if template_id is not None and template_name is not None:
        msg(
            level="error",
            message="Either template_name or template_id must be provided, not both",
        )
    if template_name is None:
        command = f"onetemplate show {template_id} -j"
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(
                level="debug",
                message=f"Template with id {template_id} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
            )
            return None
        else:
            msg(
                level="debug",
                message=f"Template with id {template_id} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
            )
            return loads_json(data=stdout)
    else:
        command = f'onetemplate show "{template_name}" -j'
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(
                level="debug",
                message=f"Template {template_name} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
            )
            return None
        else:
            msg(
                level="debug",
                message=f"Template {template_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
            )
            return loads_json(data=stdout)


def onetemplate_user_inputs(template_name: str) -> Dict | None:
    """
    Get the custom_attrs keys of a template in OpenNebula

    :param template_name: the name of the template, ``str``
    :return: the custom_attrs keys of the template, ``Dict``
    """
    onetemplate = onetemplate_show(template_name=template_name)
    if onetemplate is None:
        msg(
            level="error",
            message=f"Template {template_name} not found",
        )
    if "VMTEMPLATE" not in onetemplate or "TEMPLATE" not in onetemplate["VMTEMPLATE"]:
        msg(
            level="error",
            message=f"VMTEMPLATE key not found in template {template_name} or TEMPLATE key not found in VMTEMPLATE",
        )
    if "USER_INPUTS" not in onetemplate["VMTEMPLATE"]["TEMPLATE"]:
        msg(
            level="error",
            message="USER_INPUTS key not found in TEMPLATE",
        )
    return onetemplate["VMTEMPLATE"]["TEMPLATE"]["USER_INPUTS"]


def onetemplates_names() -> List[str]:
    """
    Get the list of templates names in OpenNebula

    :return: the list of templates names, ``List[str]``
    """
    templates = onetemplate_list()
    templates_names = []
    if templates is None:
        return []
    if (
        "VMTEMPLATE_POOL" not in templates
        or "VMTEMPLATE" not in templates["VMTEMPLATE_POOL"]
    ):
        msg(
            level="error",
            message="VMTEMPLATE_POOL key not found in templates or VMTEMPLATE key not found in VMTEMPLATE_POOL",
        )
    for template in templates["VMTEMPLATE_POOL"]["VMTEMPLATE"]:
        if template is None:
            msg(level="error", message="Template is empty")
        if "NAME" not in template:
            msg(
                level="error",
                message=f"NAME key not found in template {template}",
            )
        templates_names.append(template["NAME"])
    return templates_names


# ##############################################################################
# ##                            USER MANAGEMENT                               ##
# ##############################################################################


def oneuser_chgrp(username: str, group_name: str) -> None:
    """
    Assign user to group in OpenNebula

    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f'oneuser chgrp "{username}" "{group_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not assign user {username} to group {group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"User {username} assigned to group {group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def oneuser_create(username: str, password: str) -> int:
    """
    Create an user in OpenNebula

    :param username: the name of the user, ``str``
    :param password: the password of the user, ``str``
    :return: the id of the user, ``int``
    """
    command = f'oneuser create "{username}" "{password}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not create user {username} with password {password}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"User {username} created with password {password}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )
    return re.search(r"ID:\s*(\d+)", stdout).group(1)


def oneuser_list() -> Dict | None:
    """
    Get the list of users in OpenNebula

    :return: the list of users, ``Dict``
    """
    command = "oneuser list -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"OpenNebula users not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"OpenNebula users found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def oneuser_public_ssh_keys(username: str) -> List[str]:
    """
    Get the public SSH keys of an user in OpenNebula

    :param username: the name of the user, ``str``
    :return: the public SSH keys of the user, ``List[str]``
    """
    user = oneuser_show(username=username)
    if user is None:
        msg(
            level="error",
            message=f"User {username} not found",
        )
    if "USER" not in user or "TEMPLATE" not in user["USER"]:
        msg(
            level="error",
            message=f"USER key not found in user {username} or TEMPLATE key not found in USER",
        )
    if "SSH_PUBLIC_KEY" not in user["USER"]["TEMPLATE"]:
        return ""
    public_ssh_keys = user["USER"]["TEMPLATE"]["SSH_PUBLIC_KEY"]
    if public_ssh_keys is None:
        return ""
    return public_ssh_keys.split("\n")


def oneuser_show(
    username: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Dict | None:
    """
    Get the details of an user in OpenNebula

    :param username: the name of the user, ``str``
    :param user_id: the id of the user, ``int``
    :return: the details of the user, ``Dict``
    """
    if username is None and user_id is None:
        msg(
            level="error",
            message="Either username or user_id must be provided",
        )
    if username is not None and user_id is not None:
        msg(
            level="error",
            message="Either username or user_id must be provided, not both",
        )
    if username is None:
        command = f"oneuser show {user_id} -j"
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(
                level="debug",
                message=f"User with id {user_id} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
            )
            return None
        else:
            msg(
                level="debug",
                message=f"User with id {user_id} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
            )
            return loads_json(data=stdout)
    else:
        command = f'oneuser show "{username}" -j'
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(
                level="debug",
                message=f"User {username} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
            )
            return None
        else:
            msg(
                level="debug",
                message=f"User {username} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
            )
            return loads_json(data=stdout)


def oneuser_update_public_ssh_key(username: str, public_ssh_key: str) -> None:
    """
    Update the SSH key of an user in OpenNebula

    :param username: the name of the user, ``str``
    :param public_ssh_key: the public SSH key, ``str``
    """
    public_ssh_keys = oneuser_public_ssh_keys(username=username)
    if public_ssh_key not in public_ssh_keys:
        all_public_ssh_keys = "\n".join(public_ssh_keys)
        all_public_ssh_keys += f"\n{public_ssh_key}"
        command = f'echo \'SSH_PUBLIC_KEY="{all_public_ssh_keys}"\' | oneuser update "{username}" --append'
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(
                level="error",
                message=f"Could not update SSH key of user {username} to {public_ssh_key}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
            )
        msg(
            level="debug",
            message=f"SSH key of user {username} updated to {public_ssh_key}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
    else:
        msg(
            level="debug",
            message=f"User {username} already has SSH key {public_ssh_key}",
        )


def oneusername(user_id: int) -> str:
    """
    Get the name of an user in OpenNebula

    :param user_id: the id of the user, ``int``
    :return: the name of the user, ``str``
    """
    user = oneuser_show(user_id=user_id)
    if user is None:
        msg(
            level="error",
            message=f"User with id {user_id} not found",
        )
    if "USER" not in user or "NAME" not in user["USER"]:
        msg(
            level="error",
            message=f"USER key not found in user id {user_id} or NAME key not found in USER",
        )
    username = user["USER"]["NAME"]
    if username is None:
        msg(
            level="error",
            message=f"Could not get name of user with id {user_id}",
        )
    return username


def oneusername_id(username: str) -> int:
    """
    Get the id of an user in OpenNebula

    :param username: the name of the user, ``str``
    :return: the id of the user, ``int``
    """
    user = oneuser_show(username=username)
    if user is None:
        msg(
            level="error",
            message=f"User {username} not found",
        )
    if "USER" not in user or "ID" not in user["USER"]:
        msg(
            level="error",
            message=f"USER key not found in user {username} or ID key not found in USER",
        )
    username_id = user["USER"]["ID"]
    if username_id is None:
        msg(
            level="error",
            message=f"Could not get id of user {username}",
        )
    return int(username_id)


def oneusernames() -> List[str]:
    """
    Get the list of usernames in OpenNebula

    :return: the list of usernames, ``List[str]``
    """
    users = oneuser_list()
    usernames = []
    if users is None:
        return []
    if "USER_POOL" not in users or "USER" not in users["USER_POOL"]:
        msg(
            level="error",
            message="USER_POOL key not found in users or USER key not found in USER_POOL",
        )
    user_pool = users["USER_POOL"]["USER"]
    if user_pool is None:
        return []
    for user in user_pool:
        if user is None:
            msg(level="error", message="User is empty")
        if "NAME" not in user:
            msg(
                level="error",
                message="NAME key not found in user",
            )
        usernames.append(user["NAME"])
    return usernames


# ##############################################################################
# ##                             VM MANAGEMENT                                ##
# ##############################################################################


def onevm_chown(vm_name: str, username: str, group_name: str) -> None:
    """
    Change the owner of a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f'onevm chown "{vm_name}" "{username}" "{group_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not change owner of VM {vm_name} to {username}:{group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Owner of VM {vm_name} changed to {username}:{group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def onevm_chown_by_id(vm_id: int, username: str, group_name: str) -> None:
    """
    Change the owner of a VM in OpenNebula by VM ID

    :param vm_id: the ID of the VM, ``int``
    :param username: the name of the user, ``str``
    :param group_name: the name of the group, ``str``
    """
    command = f'onevm chown {vm_id} "{username}" "{group_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not change owner of VM ID {vm_id} to {username}:{group_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Owner of VM ID {vm_id} changed to {username}:{group_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def onevm_cpu_model(vm_name: str) -> str:
    """
    Get the CPU model of a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :return: the CPU model of the VM, ``str``
    """
    vm = onevm_show(vm_name=vm_name)
    if vm is None:
        msg(
            level="error",
            message=f"VM {vm_name} not found",
        )
    if (
        "VM" not in vm
        or "TEMPLATE" not in vm["VM"]
        or "CPU_MODEL" not in vm["VM"]["TEMPLATE"]
        or "MODEL" not in vm["VM"]["TEMPLATE"]["CPU_MODEL"]
    ):
        msg(
            level="error",
            message=f"VM key not found in vm {vm_name} or TEMPLATE key not found in VM or CPU_MODEL key not found in TEMPLATE or MODEL key not found in CPU_MODEL",
        )
    cpu_model = vm["VM"]["TEMPLATE"]["CPU_MODEL"]["MODEL"]
    if cpu_model is None:
        msg(
            level="error",
            message=f"Could not get CPU model of VM {vm_name}",
        )
    return cpu_model


def onevm_deploy(vm_name: str, host_name: str) -> None:
    """
    Deploy a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :param host_name: the name of the host, ``str``
    """
    command = f'onevm deploy "{vm_name}" "{host_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not deploy VM {vm_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"VM {vm_name} deployed. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )
    state = onevm_state(vm_name=vm_name)
    while state != "3":
        sleep(5)
        state = onevm_state(vm_name=vm_name)


def onevm_disk_resize(vm_name: str, disk_id: int, size: int) -> None:
    """
    Resize the disk of a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :param disk_id: the id of the disk, ``int``
    :param size: the new size of the disk in GB, ``int``
    """
    size_mb = gb_to_mb(gb=size)
    disk_size = onevm_disk_size(vm_name=vm_name, disk_id=disk_id)
    if disk_size > size_mb:
        msg(
            level="error",
            message=f"Disk {disk_id} of VM {vm_name} has a size of {disk_size}M which is greater than or equal to the new size {size_mb}M to be upgraded",
        )
    elif disk_size == size_mb:
        msg(
            level="debug",
            message=f"Disk {disk_id} of VM {vm_name} has a size of {disk_size}M which is equal to the new size {size_mb}M to be upgraded",
        )
    else:
        command = f'onevm disk-resize "{vm_name}" {disk_id} {size_mb}M'
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(
                level="error",
                message=f"Could not resize disk of VM {vm_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
            )
        msg(
            level="debug",
            message=f"Disk of VM {vm_name} resized successfully to {size_mb}M. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )


def onevm_disk_size(vm_name: str, disk_id: int) -> int:
    """
    Get the size of a disk of a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :param disk_id: the id of the disk, ``int``
    :return: the size of the disk, ``int``
    """
    vm = onevm_show(vm_name=vm_name)
    if vm is None:
        msg(level="error", message=f"VM {vm_name} not found")
    if (
        "VM" not in vm
        or "TEMPLATE" not in vm["VM"]
        or "DISK" not in vm["VM"]["TEMPLATE"]
    ):
        msg(
            level="error",
            message=f"VM key not found in vm {vm_name} or TEMPLATE key not found in VM or DISK key not found in TEMPLATE",
        )
    disks = vm["VM"]["TEMPLATE"]["DISK"]
    for disk in disks:
        if disk["DISK_ID"] == disk_id:
            return int(disk["SIZE"])
    msg(
        level="error",
        message=f"Disk {disk_id} not found in VM {vm_name}",
    )


def onevm_id(vm_name: str) -> int:
    """
    Get the ID of a VM in OpenNebula by name

    :param vm_name: the name of the VM, ``str``
    :return: the ID of the VM, ``int``
    """
    vm = onevm_show(vm_name=vm_name)
    if vm is None:
        msg(level="error", message=f"VM {vm_name} not found")
    if "VM" not in vm or "ID" not in vm["VM"]:
        msg(
            level="error",
            message=f"VM key not found in vm {vm_name} or ID key not found in VM",
        )
    vm_id = int(vm["VM"]["ID"])
    if vm_id is None:
        msg(level="error", message=f"Could not get ID of VM {vm_name}")
    return vm_id


def onevm_ip(vm_name: str) -> str:
    """
    Get the IP of a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :return: the IP of the VM, ``str``
    """
    vm = onevm_show(vm_name=vm_name)
    if vm is None:
        msg(level="error", message=f"VM {vm_name} not found")
    if "VM" not in vm or "TEMPLATE" not in vm["VM"]:
        msg(
            level="error",
            message=f"VM key not found in vm {vm_name} or TEMPLATE key not found in VM",
        )
    if "NIC" not in vm["VM"]["TEMPLATE"]:
        msg(
            level="error",
            message="NIC key not found in TEMPLATE",
        )
    nics = vm["VM"]["TEMPLATE"]["NIC"]
    for nic in nics:
        if "IP" in nic:
            return nic["IP"]
    msg(
        level="error",
        message=f"IP not found in VM {vm_name}",
    )


def onevm_list() -> Dict | None:
    """
    Get the list of VMs in OpenNebula

    :return: the list of VMs, ``Dict``
    """
    command = "onevm list -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"OpenNebula VMs not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"OpenNebula VMs found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onevm_template_id(vm_name: str) -> str:
    """
    Get the id of a template of a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :return: the id of the template, ``str``
    """
    vm = onevm_show(vm_name=vm_name)
    if vm is None:
        msg(level="error", message=f"VM {vm_name} not found")
    if "VM" not in vm or "TEMPLATE" not in vm["VM"]:
        msg(
            level="error",
            message=f"VM key not found in vm {vm_name} or TEMPLATE key not found in VM",
        )
    if "TEMPLATE_ID" not in vm["VM"]["TEMPLATE"]:
        msg(
            level="error",
            message="TEMPLATE_ID key not found in TEMPLATE",
        )
    template_id = vm["VM"]["TEMPLATE"]["TEMPLATE_ID"]
    if template_id is None:
        msg(
            level="error",
            message=f"Could not get template id of VM {vm_name}",
        )
    return template_id


def onevm_terminate_hard(vm_name: str) -> None:
    """
    Remove a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    """
    command = f'onevm terminate "{vm_name}" --hard'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not remove VM {vm_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"VM {vm_name} removed. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )
    onevm_data = onevm_show(vm_name=vm_name)
    while onevm_data is not None:
        sleep(5)
        onevm_data = onevm_show(vm_name=vm_name)


def onevm_show(vm_name: str) -> Dict | None:
    """
    Get the details of a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :return: the details of the VM, ``Dict``
    """
    command = f'onevm show "{vm_name}" -j'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"VM {vm_name} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"VM {vm_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onevm_show_by_id(vm_id: int) -> Dict | None:
    """
    Get the details of a VM in OpenNebula by VM ID

    :param vm_id: the ID of the VM, ``int``
    :return: the details of the VM, ``Dict``
    """
    command = f"onevm show {vm_id} -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"VM ID {vm_id} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"VM ID {vm_id} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onevm_ip_by_id(vm_id: int) -> str:
    """
    Get the IP of a VM in OpenNebula by VM ID

    :param vm_id: the ID of the VM, ``int``
    :return: the IP of the VM, ``str``
    """
    vm = onevm_show_by_id(vm_id=vm_id)
    if vm is None:
        msg(level="error", message=f"VM ID {vm_id} not found")
    if "VM" not in vm or "TEMPLATE" not in vm["VM"]:
        msg(
            level="error",
            message=f"VM key not found in VM ID {vm_id} or TEMPLATE key not found in VM",
        )
    if "NIC" not in vm["VM"]["TEMPLATE"]:
        msg(
            level="error",
            message=f"NIC key not found in TEMPLATE for VM ID {vm_id}",
        )
    nics = vm["VM"]["TEMPLATE"]["NIC"]
    for nic in nics:
        if "IP" in nic:
            return nic["IP"]
    msg(
        level="error",
        message=f"IP not found in VM ID {vm_id}",
    )


def onevm_state(vm_name: str) -> str:
    """
    Get the state of a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :return: the state of the VM, ``str``
    """
    vm = onevm_show(vm_name=vm_name)
    if vm is None:
        msg(level="error", message=f"VM {vm_name} not found")
    if "VM" not in vm or "STATE" not in vm["VM"]:
        msg(
            level="error",
            message=f"VM key not found in vm {vm_name} or STATE key not found in VM",
        )
    vm_state = vm["VM"]["STATE"]
    if vm_state is None:
        msg(level="error", message=f"Could not get state of VM {vm_name}")
    return vm_state


def onevm_state_by_id(vm_id: int) -> str:
    """
    Get the state of a VM in OpenNebula by VM ID

    :param vm_id: the ID of the VM, ``int``
    :return: the state of the VM, ``str``
    """
    vm = onevm_show_by_id(vm_id=vm_id)
    if vm is None:
        msg(level="error", message=f"VM ID {vm_id} not found")
    if "VM" not in vm or "STATE" not in vm["VM"]:
        msg(
            level="error",
            message=f"VM key not found in VM ID {vm_id} or STATE key not found in VM",
        )
    vm_state = vm["VM"]["STATE"]
    if vm_state is None:
        msg(level="error", message=f"Could not get state of VM ID {vm_id}")
    return vm_state


def onevm_undeploy_hard(vm_name: str) -> None:
    """
    Undeploy a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    """
    command = f'onevm undeploy "{vm_name}" --hard'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not undeploy VM {vm_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"VM {vm_name} undeployed. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )
    state = onevm_state(vm_name=vm_name)
    while state != "9":
        sleep(5)
        state = onevm_state(vm_name=vm_name)


def onevm_updateconf_cpu_model(vm_name: str, cpu_model: str) -> None:
    """
    Update the configuration of a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :param file_path: the path of the file, ``str``
    """
    command = f'echo \'CPU_MODEL=[MODEL="{cpu_model}"]\' | onevm updateconf "{vm_name}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Could not update configuration of VM {vm_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Configuration of VM {vm_name} updated. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def onevm_user_input(vm_name, user_input: str) -> str:
    """
    Get the value of a user input in a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :param user_input: the name of the user input, ``str``
    :return: the value of the user input, ``str``
    """
    vm = onevm_show(vm_name=vm_name)
    if vm is None:
        msg(
            level="error",
            message=f"VM {vm_name} not found",
        )
    if "VM" not in vm or "USER_TEMPLATE" not in vm["VM"]:
        msg(
            level="error",
            message=f"VM key not found in VM {vm_name} or USER_TEMPLATE key not found in VM",
        )
    if user_input not in vm["VM"]["USER_TEMPLATE"]:
        msg(
            level="error",
            message=f"User input {user_input} not found in VM {vm_name}",
        )
    return vm["VM"]["USER_TEMPLATE"][user_input]


def onevm_user_input_by_id(vm_id: int, user_input: str) -> str:
    """
    Get the value of a user input in a VM in OpenNebula by VM ID

    :param vm_id: the ID of the VM, ``int``
    :param user_input: the name of the user input, ``str``
    :return: the value of the user input, ``str``
    """
    vm = onevm_show_by_id(vm_id=vm_id)
    if vm is None:
        msg(
            level="error",
            message=f"VM ID {vm_id} not found",
        )
    if "VM" not in vm or "USER_TEMPLATE" not in vm["VM"]:
        msg(
            level="error",
            message=f"VM key not found in VM ID {vm_id} or USER_TEMPLATE key not found in VM",
        )
    if user_input not in vm["VM"]["USER_TEMPLATE"]:
        msg(
            level="error",
            message=f"User input {user_input} not found in VM ID {vm_id}",
        )
    return vm["VM"]["USER_TEMPLATE"][user_input]


def onevm_user_template(vm_name: str) -> Dict:
    """
    Get the user template of a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :return: the user template of the VM, ``Dict``
    """
    vm = onevm_show(vm_name=vm_name)
    if vm is None:
        msg(level="error", message=f"VM {vm_name} not found")
    if "VM" not in vm or "USER_TEMPLATE" not in vm["VM"]:
        msg(
            level="error",
            message=f"VM key not found in vm {vm_name} or USER_TEMPLATE key not found in VM",
        )
    user_template = vm["VM"]["USER_TEMPLATE"]
    if user_template is None:
        msg(
            level="error",
            message=f"Could not get user template of VM {vm_name}",
        )
    return user_template


def onevm_user_template_param(vm_name: str, param: str) -> Dict:
    """
    Get the value of a user template parameter of a VM in OpenNebula

    :param vm_name: the name of the VM, ``str``
    :param param: the name of the parameter, ``str``
    :return: the value of the parameter, ``Dict``
    """
    user_template = onevm_user_template(vm_name=vm_name)
    if param not in user_template:
        msg(
            level="error",
            message=f"Parameter {param} not found in user template of VM {vm_name}",
        )
    value = user_template[param]
    if value is None:
        msg(
            level="error",
            message=f"Could not get value of parameter {param} in user template of VM {vm_name}",
        )
    return value


def onevms_names() -> List[str]:
    """
    Get the names of the VMs in OpenNebula

    :return: the names of the VMs, ``List[str]``
    """
    vms = onevm_list()
    vms_names = []
    if vms is None:
        return []
    if "VM_POOL" not in vms or "VM" not in vms["VM_POOL"]:
        msg(
            level="error",
            message="VM_POOL key not found in vms or VM key not found in VM_POOL",
        )
    for vm in vms["VM_POOL"]["VM"]:
        if vm is None:
            msg(level="error", message="VM is empty")
        if "NAME" not in vm:
            msg(
                level="error",
                message="NAME key not found in vm",
            )
        vms_names.append(vm["NAME"])
    return vms_names


def onevms_running() -> List[str]:
    """
    Get the names of the running VMs in OpenNebula

    :return: the names of the running VMs, ``List[str]``
    """
    vms = onevm_list()
    vms_names = []
    if vms is None:
        return []
    if "VM_POOL" not in vms or "VM" not in vms["VM_POOL"]:
        msg(
            level="error",
            message="VM_POOL key not found in vms or VM key not found in VM_POOL",
        )
    for vm in vms["VM_POOL"]["VM"]:
        if vm is None:
            msg(level="error", message="VM is empty")
        if "NAME" not in vm:
            msg(
                level="error",
                message="NAME key not found in vm",
            )
        if "STATE" not in vm:
            msg(
                level="error",
                message="STATE key not found in vm",
            )
        if vm["STATE"] == "3":
            vms_names.append(vm["NAME"])
    return vms_names


def onevms_running_with_ids() -> Dict[str, int]:
    """
    Get the names and IDs of the running VMs in OpenNebula

    :return: a dictionary with VM names as keys and VM IDs as values, ``Dict[str, int]``
    """
    vms = onevm_list()
    vms_dict = {}
    if vms is None:
        return {}
    if "VM_POOL" not in vms or "VM" not in vms["VM_POOL"]:
        msg(
            level="error",
            message="VM_POOL key not found in vms or VM key not found in VM_POOL",
        )
    for vm in vms["VM_POOL"]["VM"]:
        if vm is None:
            msg(level="error", message="VM is empty")
        if "NAME" not in vm:
            msg(
                level="error",
                message="NAME key not found in vm",
            )
        if "ID" not in vm:
            msg(
                level="error",
                message="ID key not found in vm",
            )
        if "STATE" not in vm:
            msg(
                level="error",
                message="STATE key not found in vm",
            )
        if vm["STATE"] == "3":
            vms_dict[vm["NAME"]] = int(vm["ID"])
    return vms_dict


# ##############################################################################
# ##                         NETWORKS MANAGEMENT                              ##
# ##############################################################################


def onevnet_id(vnet_name: str) -> int:
    """
    Get the id of a vnet in OpenNebula

    :param vnet_name: the name of the vnet, ``str``
    :return: the id of the vnet, ``int``
    """
    vnet = onevnet_show(vnet_name=vnet_name)
    if vnet is None:
        msg(
            level="error",
            message=f"Vnet {vnet_name} not found",
        )
    if "VNET" not in vnet or "ID" not in vnet["VNET"]:
        msg(
            level="error",
            message=f"VNET key not found in vnet {vnet_name} or ID key not found in VNET",
        )
    vnet_id = vnet["VNET"]["ID"]
    if vnet_id is None:
        msg(
            level="error",
            message=f"Could not get id of vnet {vnet_name}",
        )
    return vnet_id


def onevnet_list() -> Dict:
    """
    Get the list of VNets in OpenNebula

    :return: the list of vnets, ``Dict``
    """
    command = "onevnet list -j"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Vnets not found. Create a vnet in OpenNebula before adding an appliance. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    else:
        msg(
            level="debug",
            message=f"Vnets found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onevnet_show(vnet_name: str) -> Dict | None:
    """
    Get the details of a vnet in OpenNebula

    :param vnet_name: the name of the vnet, ``str``
    :return: the details of the vnet, ``Dict``
    """
    command = f'onevnet show "{vnet_name}" -j'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="debug",
            message=f"Vnet {vnet_name} not found. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
        return None
    else:
        msg(
            level="debug",
            message=f"Vnet {vnet_name} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
        return loads_json(data=stdout)


def onevnets_names() -> List[str]:
    """
    Get the names of the vnets in OpenNebula

    :return: the names of the vnets, ``List[str]``
    """
    vnets = onevnet_list()
    vnets_names = []
    if "VNET_POOL" not in vnets or "VNET" not in vnets["VNET_POOL"]:
        msg(
            level="error",
            message="VNET_POOL key not found in vnets or VNET key not found in VNET_POOL",
        )
    for vnet in vnets["VNET_POOL"]["VNET"]:
        if vnet is None:
            msg(level="error", message="Vnet is empty")
        if "NAME" not in vnet:
            msg(
                level="error",
                message="NAME key not found in vnet",
            )
        vnets_names.append(vnet["NAME"])
    return vnets_names
