from time import sleep

from phases.utils.file import get_env_var
from phases.utils.interactive import ask_text, ask_password, ask_confirm, ask_select
from phases.utils.logs import msg
from phases.utils.one import add_appliances_from_marketplace, get_onemarket, add_marketplace, get_marketplace_monitoring_interval, update_marketplace_monitoring_interval, restart_one, check_one_health, get_vm, get_onegate_endpoint, add_ssh_key, get_oneflow_template_networks, get_oneflow_template_custom_attrs, instantiate_oneflow_template, get_vnets_names, get_vnet_id, chown_oneflow, get_oneflow_roles, chown_vm
from phases.utils.temp import load_temp_file, save_temp_json_file, temp_path, save_temp_file

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

def _generate_custom_attrs_values(custom_attrs: dict, jenkins_user: str) -> dict:
    """
    Generate the custom attributes values from the custom attributes
    
    :param custom_attrs: the custom attributes, ``dict``
    :param jenkins_user: the Jenkins user, ``str``
    :return: the custom attributes values, ``dict``
    """
    params = {}
    for custom_attr_key, custom_attr_value in custom_attrs.items():
        if custom_attr_key != "oneapp_jenkins_opennebula_username" and custom_attr_key != "oneapp_jenkins_opennebula_password" and custom_attr_key != "oneapp_jenkins_opennebula_endpoint" and custom_attr_key != "oneapp_jenkins_opennebula_endpoint" and custom_attr_key != "oneapp_jenkins_opennebula_flow_endpoint":
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
                if input_type == "text64":
                    value = ask_text(prompt=description, default=default_value)
            if field_type == "M":
                if input_type == "text":
                    value = ask_text(prompt=description, default=default_value, validate=True)
                if input_type == "password":
                    value = ask_password(prompt=description, validate=True)
            params[custom_attr_key] = value
        else:
            if custom_attr_key == "oneapp_jenkins_opennebula_username":
                params[custom_attr_key] = jenkins_user
            elif custom_attr_key == "oneapp_jenkins_opennebula_password":
                params[custom_attr_key] = load_temp_file(file_path=jenkins_user, mode="rt", encoding="utf-8")
            elif custom_attr_key == "oneapp_jenkins_opennebula_endpoint":
                onegate_endpoint = get_onegate_endpoint()
                onegate_endpoint = ":".join(onegate_endpoint.split(":")[:2])
                params[custom_attr_key] = f"{onegate_endpoint}:2633/RPC2"
            else:
                onegate_endpoint = get_onegate_endpoint()
                onegate_endpoint = ":".join(onegate_endpoint.split(":")[:2])
                params[custom_attr_key] = f"{onegate_endpoint}:2474"
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
    sixg_sandbox_marketplace = get_onemarket(marketplace_name=sixg_sandbox_marketplace_name)
    if sixg_sandbox_marketplace is None:
        _ = add_marketplace(sixg_sandbox_marketplace_name, sixg_sandbox_marketplace_description, sixg_sandbox_marketplace_endpoint)
        force_fast_marketplace_monitoring = get_env_var("FORCE_FAST_MARKETPLACE_MONITORING")
        if force_fast_marketplace_monitoring == "false":
            sleep(600)
        else:
            marketplace_interval = int(get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_INTERVAL"))
            old_interval = get_marketplace_monitoring_interval()
            update_marketplace_monitoring_interval(interval=marketplace_interval)
            restart_one()
            sleep(marketplace_interval+5)
            check_one_health()
            update_marketplace_monitoring_interval(interval=old_interval)
            restart_one()
            check_one_health()
    appliances = []
    toolkit_service = get_env_var("OPENNEBULA_TOOLKIT_SERVICE")
    appliances.append(toolkit_service)
    add_appliances_from_marketplace(sixg_sandbox_group=sixg_sandbox_group, jenkins_user=jenkins_user, marketplace_name=sixg_sandbox_marketplace_name, appliances=appliances)
    params = {}
    custom_attrs = get_oneflow_template_custom_attrs(toolkit_service)
    custom_attrs_values = _generate_custom_attrs_values(custom_attrs, jenkins_user)
    sites_token = custom_attrs_values["oneapp_jenkins_sites_token"]
    params["custom_attrs_values"] = custom_attrs_values
    networks = get_oneflow_template_networks(toolkit_service)
    networks_values = _generate_networks_values(networks)
    params["networks_values"] = networks_values
    params_path = save_temp_json_file(data=params, file_path="toolkit_service_params.json", mode="wt", encoding="utf-8")
    toolkit_service_id = instantiate_oneflow_template(toolkit_service, params_path)
    sleep(10)
    chown_oneflow(oneflow_id=toolkit_service_id, username=jenkins_user, group_name=sixg_sandbox_group)
    roles = get_oneflow_roles(oneflow_name=toolkit_service)
    vm_tnlcm_name = None
    for role in roles:
        while role["state"] != 1:
            sleep(10)
        if role["name"] == "jenkins":
            vm_jenkins_name = role["nodes"][0]["vm_info"]["VM"]["NAME"]
            jenkins_ssh_key = get_vm(vm_name=vm_jenkins_name)["VM"]["USER_TEMPLATE"]["SSH_KEY"]
            add_ssh_key(username=jenkins_user, ssh_key_path=jenkins_ssh_key)
        if role["name"] == "tnlcm":
            vm_tnlcm_name = role["nodes"][0]["vm_info"]["VM"]["NAME"]
        vm_id = role["nodes"][0]["vm_info"]["VM"]["ID"]
        chown_vm(vm_id=vm_id, username=jenkins_user, group_name=sixg_sandbox_group)
    return sites_token, vm_tnlcm_name