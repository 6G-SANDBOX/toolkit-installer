from time import sleep

from phases.utils.file import get_env_var
from phases.utils.interactive import ask_text, ask_password, ask_confirm, ask_select
from phases.utils.logs import msg
from phases.utils.one import add_appliances_from_marketplace, get_vm, get_oneflow, get_oneflow_custom_attrs_values, get_onemarket, add_marketplace, get_marketplace_monitoring_interval, update_marketplace_monitoring_interval, restart_one, check_one_health, get_onegate_endpoint, add_ssh_key, get_oneflow_template_networks, get_oneflow_template_custom_attrs, instantiate_oneflow_template, get_vnets_names, get_vnet_id, chown_oneflow, get_oneflow_roles, chown_vm
from phases.utils.temp import load_temp_file, save_temp_json_file

def _parse_custom_attr(attr_string: str) -> dict:
    """
    Parse a custom attribute string from the OneFlow template
    
    :param attr_string: the custom attribute string, ``str``
    :return: the parsed custom attribute, ``dict``
    """
    parts = attr_string.split("|")
    result = {
        "field_type": parts[0],
        "input_type": parts[1],
        "description": parts[2],
        "default_value": "",
    }
    if "||" in attr_string:
        default_start_index = attr_string.index("||") + 2
        result["default_value"] = attr_string[default_start_index:].strip()
    
    return result

def validate_sites_token(sites_token: str) -> str | bool:
    """
    Validate the sites token and return an error message if invalid.

    :param sites_token: the token sites, ``str``
    :return: error message if invalid, otherwise an empty string, ``str`` or ``bool``
    """
    
    if len(sites_token) < 20:
        return "The token must be at least 20 characters long"
    
    if not any(char.isupper() for char in sites_token):
        return "The token must contain at least one uppercase letter"
    
    if not any(char.islower() for char in sites_token):
        return "The token must contain at least one lowercase letter"
    
    if not any(char.isdigit() for char in sites_token):
        return "The token must contain at least one digit"
    
    special_characters = "!%()*+,-./:;<=>?@[\\]^_{}~"
    if not any(char in special_characters for char in sites_token):
        return "The token must contain at least one special character"

    return True

def validate_length(value: str, max_length: int) -> str | bool:
    """
    Validate the length of the value and return an error message if invalid.

    :param value: the value, ``str``
    :param max_length: the maximum length, ``int``
    :return: error message if invalid, otherwise an empty string, ``str`` or ``bool``
    """
    if len(value) < max_length:
        return f"The value must be at least {max_length} characters long"
    return True

def _generate_custom_attrs_values(custom_attrs: dict, jenkins_user: str) -> dict:
    """
    Generate the custom attributes values from the custom attributes
    
    :param custom_attrs: the custom attributes, ``dict``
    :param jenkins_user: the Jenkins user, ``str``
    :return: the custom attributes values, ``dict``
    """
    params = {}
    for custom_attr_key, custom_attr_value in custom_attrs.items():
        if custom_attr_key == "oneapp_jenkins_opennebula_username":
            params[custom_attr_key] = jenkins_user
        elif custom_attr_key == "oneapp_jenkins_opennebula_password":
            params[custom_attr_key] = load_temp_file(file_path=jenkins_user, mode="rt", encoding="utf-8")
        elif custom_attr_key == "oneapp_jenkins_opennebula_endpoint":
            onegate_endpoint = get_onegate_endpoint()
            onegate_endpoint = ":".join(onegate_endpoint.split(":")[:2])
            params[custom_attr_key] = f"{onegate_endpoint}:2633/RPC2"
        elif custom_attr_key == "oneapp_jenkins_opennebula_flow_endpoint":
            onegate_endpoint = get_onegate_endpoint()
            onegate_endpoint = ":".join(onegate_endpoint.split(":")[:2])
            params[custom_attr_key] = f"{onegate_endpoint}:2474"
        elif custom_attr_key == "oneapp_jenkins_sites_token":
            parser_custom_attr = _parse_custom_attr(custom_attr_value)
            field_type = parser_custom_attr["field_type"]
            input_type = parser_custom_attr["input_type"]
            description = parser_custom_attr["description"]
            value = ask_password(prompt=description, validate=validate_sites_token)
            params[custom_attr_key] = value
        elif custom_attr_key == "oneapp_minio_root_user":
            parser_custom_attr = _parse_custom_attr(custom_attr_value)
            field_type = parser_custom_attr["field_type"]
            input_type = parser_custom_attr["input_type"]
            description = parser_custom_attr["description"]
            default_value = parser_custom_attr["default_value"]
            value = ask_text(prompt=description, default=default_value, validate=lambda v: validate_length(v, 8))
            params[custom_attr_key] = value
        elif custom_attr_key == "oneapp_minio_root_password":
            parser_custom_attr = _parse_custom_attr(custom_attr_value)
            field_type = parser_custom_attr["field_type"]
            input_type = parser_custom_attr["input_type"]
            description = parser_custom_attr["description"]
            value = ask_password(prompt=description, validate=lambda v: validate_length(v, 8))
            params[custom_attr_key] = value
        elif custom_attr_key == "oneapp_jenkins_username":
            parser_custom_attr = _parse_custom_attr(custom_attr_value)
            field_type = parser_custom_attr["field_type"]
            input_type = parser_custom_attr["input_type"]
            description = parser_custom_attr["description"]
            value = ask_text(prompt=description, default=default_value, validate=lambda v: validate_length(v, 5))
            params[custom_attr_key] = value
        elif custom_attr_key == "oneapp_jenkins_password":
            parser_custom_attr = _parse_custom_attr(custom_attr_value)
            field_type = parser_custom_attr["field_type"]
            input_type = parser_custom_attr["input_type"]
            description = parser_custom_attr["description"]
            value = ask_password(prompt=description, validate=lambda v: validate_length(v, 8))
            params[custom_attr_key] = value
        elif custom_attr_key == "oneapp_tnlcm_admin_user":
            parser_custom_attr = _parse_custom_attr(custom_attr_value)
            field_type = parser_custom_attr["field_type"]
            input_type = parser_custom_attr["input_type"]
            description = parser_custom_attr["description"]
            value = ask_text(prompt=description, default=default_value, validate=lambda v: validate_length(v, 5))
            params[custom_attr_key] = value
        elif custom_attr_key == "oneapp_tnlcm_admin_password":
            parser_custom_attr = _parse_custom_attr(custom_attr_value)
            field_type = parser_custom_attr["field_type"]
            input_type = parser_custom_attr["input_type"]
            description = parser_custom_attr["description"]
            value = ask_password(prompt=description, validate=lambda v: validate_length(v,8))
            params[custom_attr_key] = value
        else:
            parser_custom_attr = _parse_custom_attr(custom_attr_value)
            field_type = parser_custom_attr["field_type"]
            input_type = parser_custom_attr["input_type"]
            description = parser_custom_attr["description"]
            default_value = parser_custom_attr["default_value"]
            if field_type == "O":
                if input_type == "text":
                    value = ask_text(prompt=description, default=default_value)
                if input_type == "password":
                    value = ask_password(prompt=description)
                if input_type == "boolean":
                    value = ask_confirm(prompt=description, default=default_value)
                    value = "YES" if value else "NO"
                if input_type == "text64":
                    value = ask_text(prompt=description, default=default_value)
            if field_type == "M":
                if input_type == "text":
                    value = ask_text(prompt=description, default=default_value, validate=True)
                if input_type == "password":
                    value = ask_password(prompt=description, validate=True)
            params[custom_attr_key] = value
    return params

def _generate_networks_values(networks: dict) -> dict:
    """
    Generate the networks values
    
    :param networks: the networks, ``dict``
    :return: the networks values, ``dict``
    """
    params = []
    for custom_attr_key, custom_attr_value in networks.items():
        parser_custom_attr = _parse_custom_attr(custom_attr_value)
        _ = parser_custom_attr["field_type"]
        _ = parser_custom_attr["input_type"]
        description = parser_custom_attr["description"]
        default_value = parser_custom_attr["default_value"]
        default_value = default_value[:-1]
        vnets = get_vnets_names()
        vnet = ask_select(prompt=description, choices=vnets)
        vnet_id = get_vnet_id(vnet_name=vnet)
        vnet_dict = {default_value: str(vnet_id)}
        public_dict = {custom_attr_key: vnet_dict}
        params.append(public_dict)
    return params

def second_phase(sixg_sandbox_group: str, jenkins_user: str) -> tuple:
    msg("info", "SECOND PHASE")
    sixg_sandbox_marketplace_name = get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_NAME")
    sixg_sandbox_marketplace_description = get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_DESCRIPTION")
    sixg_sandbox_marketplace_endpoint = get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_ENDPOINT")
    toolkit_service = get_env_var("OPENNEBULA_TOOLKIT_SERVICE")
    marketplace_interval = int(get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_INTERVAL"))
    force_fast_marketplace_monitoring = get_env_var("FORCE_FAST_MARKETPLACE_MONITORING")
    sixg_sandbox_marketplace = get_onemarket(marketplace_name=sixg_sandbox_marketplace_name)
    if sixg_sandbox_marketplace is None:
        _ = add_marketplace(sixg_sandbox_marketplace_name, sixg_sandbox_marketplace_description, sixg_sandbox_marketplace_endpoint)
        if force_fast_marketplace_monitoring == "false":
            sleep(600)
        else:
            old_interval = get_marketplace_monitoring_interval()
            update_marketplace_monitoring_interval(interval=marketplace_interval)
            restart_one()
            sleep(marketplace_interval+5)
            check_one_health()
            update_marketplace_monitoring_interval(interval=old_interval)
            restart_one()
            check_one_health()
    sites_token = None
    vm_tnlcm_name = None
    if get_oneflow(oneflow_name=toolkit_service) is None:
        add_appliances_from_marketplace(sixg_sandbox_group=sixg_sandbox_group, jenkins_user=jenkins_user, marketplace_name=sixg_sandbox_marketplace_name, appliances=[toolkit_service])
        params = {}
        custom_attrs = get_oneflow_template_custom_attrs(oneflow_template_name=toolkit_service)
        custom_attrs_values = _generate_custom_attrs_values(custom_attrs, jenkins_user)
        sites_token = custom_attrs_values["oneapp_jenkins_sites_token"]
        params["custom_attrs_values"] = custom_attrs_values
        networks = get_oneflow_template_networks(oneflow_template_name=toolkit_service)
        networks_values = _generate_networks_values(networks)
        params["networks_values"] = networks_values
        params_path = save_temp_json_file(data=params, file_path="toolkit_service_params.json", mode="wt", encoding="utf-8")
        toolkit_service_id = instantiate_oneflow_template(toolkit_service, params_path)
        sleep(10)
        chown_oneflow(oneflow_id=toolkit_service_id, username=jenkins_user, group_name=sixg_sandbox_group)
        roles = get_oneflow_roles(oneflow_name=toolkit_service)
        roles_len = len(roles)
        cont = 0
        while cont < roles_len:
            role = roles[cont]
            state = role["state"]
            while state != 2:
                roles = get_oneflow_roles(oneflow_name=toolkit_service)
                state = roles[cont]["state"]
                sleep(10)
            if role["name"] == "jenkins":
                vm_jenkins_name = role["nodes"][0]["vm_info"]["VM"]["NAME"]
                jenkins_ssh_key = get_vm(vm_name=vm_jenkins_name)["VM"]["USER_TEMPLATE"]["SSH_KEY"]
                add_ssh_key(username=jenkins_user, jenkins_ssh_key=jenkins_ssh_key)
            if role["name"] == "tnlcm":
                vm_tnlcm_name = role["nodes"][0]["vm_info"]["VM"]["NAME"]
            vm_id = role["nodes"][0]["vm_info"]["VM"]["ID"]
            chown_vm(vm_id=vm_id, username=jenkins_user, group_name=sixg_sandbox_group)
            cont += 1
    else:
        roles = get_oneflow_roles(oneflow_name=toolkit_service)
        for role in roles:
            if role["name"] == "tnlcm":
                vm_tnlcm_name = role["nodes"][0]["vm_info"]["VM"]["NAME"]
        sites_token = get_oneflow_custom_attrs_values(toolkit_service)["oneapp_jenkins_sites_token"]
    return sites_token, vm_tnlcm_name