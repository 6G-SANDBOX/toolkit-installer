from time import sleep

from src.utils.file import get_env_var
from src.utils.interactive import ask_text, ask_password, ask_confirm, ask_select
from src.utils.logs import msg
from src.utils.one import get_vm, get_group_id, get_onegate_endpoint, chauth_ssh_key, get_oneflow_template_custom_attrs, instantiate_oneflow_template, get_vnets_names, get_vnet_id, chown_oneflow, get_username_id, get_oneflow_roles, chown_vm
from src.utils.temp import load_temp_file, save_temp_json_file, temp_path, save_temp_file

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

def _generate_custom_attrs_values(custom_attrs: dict, jenkins_user: str, sites_token: str) -> dict:
    """
    Generate the custom attributes values from the custom attributes
    
    :param custom_attrs: the custom attributes, ``dict``
    :param jenkins_user: the Jenkins user, ``str``
    :param token_path: the sites token path, ``str``
    :return: the custom attributes values, ``dict``
    """
    params = {}
    for custom_attr_key, custom_attr_value in custom_attrs.items():
        if custom_attr_key != "oneapp_jenkins_opennebula_username" and custom_attr_key != "oneapp_jenkins_opennebula_password" and custom_attr_key != "oneapp_jenkins_sites_token" and custom_attr_key != "oneapp_jenkins_opennebula_endpoint" and custom_attr_key != "oneapp_jenkins_opennebula_endpoint" and custom_attr_key != "oneapp_jenkins_opennebula_flow_endpoint":
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
                onegate_endpoint = onegate_endpoint.split(":")[0]
                params[custom_attr_key] = f"{onegate_endpoint}:2633/RPC2"
            elif custom_attr_key == "oneapp_jenkins_opennebula_flow_endpoint":
                onegate_endpoint = get_onegate_endpoint()
                onegate_endpoint = onegate_endpoint.split(":")[0]
                params[custom_attr_key] = f"{onegate_endpoint}:2474"
            else:
                params[custom_attr_key] = sites_token
    return params

def _generate_networks_values() -> dict:
    """
    Generate the networks values
    
    :return: the networks values, ``dict``
    """
    params = []
    vnets = get_vnets_names()
    vnet = ask_select(prompt="Select the network", choices=vnets)
    vnet_id = get_vnet_id(vnet_name=vnet)
    vnet_dict = {"id": str(vnet_id)}
    public_dict = {"Public": vnet_dict}
    params.append(public_dict)
    return params

def fourth_phase(sixg_sandbox_group: str, jenkins_user: str, sites_token: str) -> None:
    msg("info", "FOURTH PHASE")
    toolkit_service = get_env_var("OPENNEBULA_TOOLKIT_SERVICE")
    custom_attrs = get_oneflow_template_custom_attrs(toolkit_service)
    params = {}
    custom_attrs_values = _generate_custom_attrs_values(custom_attrs, jenkins_user, sites_token)
    params["custom_attrs_values"] = custom_attrs_values
    networks_values = _generate_networks_values()
    params["networks_values"] = networks_values
    params_path = save_temp_json_file(data=params, file_path="toolkit_service_params.json", mode="wt", encoding="utf-8")
    # params_path = temp_path("toolkit_service_params.json")
    toolkit_service_id = instantiate_oneflow_template(toolkit_service, params_path)
    sleep(10)
    sixg_sandbox_group_id = get_group_id(group_name=sixg_sandbox_group)
    jenkins_user_id = get_username_id(username=jenkins_user)
    chown_oneflow(oneflow_id=toolkit_service_id, group_id=sixg_sandbox_group_id, user_id=jenkins_user_id)
    roles = get_oneflow_roles(oneflow_name=toolkit_service)
    for role in roles:
        while role["state"] != 1:
            sleep(10)
        if role["name"] == "jenkins":
            vm_jenkins_name = role["nodes"][0]["vm_info"]["VM"]["NAME"]
            jenkins_ssh_key = get_vm(vm_name=vm_jenkins_name)["VM"]["USER_TEMPLATE"]["CONTEXT"]["SSH_KEY"]
            ssh_key_path = save_temp_file(data=jenkins_ssh_key, file_path="jenkins_ssh_key", mode="wt", encoding="utf-8")
            chauth_ssh_key(username=jenkins_user, ssh_key_path=ssh_key_path)
        vm_id = role["nodes"][0]["vm_info"]["VM"]["ID"]
        chown_vm(vm_id=vm_id, group_id=sixg_sandbox_group_id, user_id=jenkins_user_id)