import os
import re

from src.utils.cli import run_command
from src.utils.file import load_file, loads_json
from src.utils.logs import msg

def get_groups() -> dict:
    """
    Get the list of groups in OpenNebula
    
    :return: the list of groups, ``dict``
    """
    res = run_command("onegroup list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the groups")
    return loads_json(data=res["stdout"])

def get_users() -> dict:
    """
    Get the list of users in OpenNebula
    
    :return: the list of users, ``dict``
    """
    res = run_command("oneuser list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the users")
    return loads_json(data=res["stdout"])

def get_vms() -> dict:
    """
    Get the list of VMs in OpenNebula
    
    :return: the list of VMs, ``dict``
    """
    res = run_command("onevm list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the VMs")
    return loads_json(data=res["stdout"])

def get_onedatastores() -> dict:
    """
    Get the list of datastores in OpenNebula
    
    :return: the list of datastores, ``dict``
    """
    res = run_command("onedatastore list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the datastores")
    return loads_json(data=res["stdout"])

def get_oneflows() -> dict:
    """
    Get the list of flows in OpenNebula
    
    :return: the list of flows, ``dict``
    """
    res = run_command("oneflow list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the flows")
    return loads_json(data=res["stdout"])

def get_onemarket() -> dict:
    """
    Get the list of market in OpenNebula
    
    :return: the list of market, ``dict``
    """
    res = run_command("onemarket list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the market")
    return loads_json(data=res["stdout"])

def get_onegate() -> dict:
    oned_config_path = os.path.join("/etc", "one", "oned.conf")
    oned_conf = load_file(file_path=oned_config_path, mode="rt", encoding="utf-8")
    match = re.search(r"^\s*ONEGATE_ENDPOINT\s*=\s*\"([^\"]+)\"", oned_conf, re.MULTILINE)
    if match is None:
        msg("error", "Could not find ONEGATE_ENDPOINT in oned.conf")
    onegate_endpoint = match.group(1)
    command = f"curl {onegate_endpoint}"
    res = run_command(command)
    if res["rc"] != 0:
        msg("error", f"OpenNebula CLI healthcheck failed. Command: '{command}'")

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
    get_onemarket()
    get_onegate()
    msg("info", "OpenNebula is healthy")

def create_group(group_name: str) -> int:
    """
    Create a group in OpenNebula
    
    :param group_name: the name of the group, ``str``
    :return: the ID of the group, ``int``
    """
    msg("info", f"[CREATE {group_name} GROUP]")
    groups = get_groups()
    group_id = None
    for group in groups["GROUP_POOL"]["GROUP"]:
        if group["NAME"] == group:
            group_id = int(group["ID"])
            msg("info", f"Group already present with ID {group_id}")
            break
    if not group_id:
        msg("info", "Group not found, creating group...")
        res = run_command(f"onegroup create {group_name}")
        if res["rc"] != 0:
            msg("error", "Group could not be registered")
        group_id = re.search(r"ID:\s*(\d+)", res["stdout"]).group(1)
        msg("info", f"Group registered successfully with ID {group_id}")
    return group_id

def create_user(username: str, password: str) -> int:
    """
    Create a user in OpenNebula
    
    :param username: the user name, ``str``
    :param password: the user password, ``str``
    :return: the ID of the user, ``int``
    """
    msg("info", f"[CREATE {username} USER]")
    users = get_users()
    user_id = None
    for user in users["USER_POOL"]["USER"]:
        if user["NAME"] == username:
            user_id = int(user["ID"])
            msg("info", f"User already present with ID {user_id}")
            break
    if not user_id:
        msg("info", "User not found, creating user...")
        res = run_command(f"oneuser create {username} {password}")
        if res["rc"] != 0:
            msg("error", "TUser could not be registered")
        user_id = re.search(r"ID:\s*(\d+)", res["stdout"]).group(1)
        msg("info", f"User registered successfully with ID {user_id}")
    return user_id

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