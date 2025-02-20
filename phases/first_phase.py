from phases.utils.file import get_env_var
from phases.utils.interactive import ask_text, ask_password
from phases.utils.logs import msg
from phases.utils.one import get_group, create_group, get_username, create_user, assign_user_group, add_admin_user_group, add_acl
from phases.utils.string import validate_length
from phases.utils.temp import save_temp_file

def first_phase() -> tuple:
    msg("info", "FIRST PHASE")
    default_user = get_env_var("OPENNEBULA_SANDBOX_USER")
    exist_user = get_username(username=default_user)
    if exist_user is None:
        username = ask_text(
            "Enter the username for the OpenNebula user:",
            default=default_user,
            validate=lambda v: validate_length(v, 5)
        )
        username_data = get_username(username=username)
        if username_data is None:
            jenkins_password = ask_password(
                "Enter the password for the OpenNebula user:",
                validate=lambda v: validate_length(v, 5)
            )
            save_temp_file(
                data=jenkins_password,
                file_path=username,
                mode="wt",
                encoding="utf-8"
            )
            _ = create_user(username=username, password=jenkins_password)
    else:
        username = default_user
    
    default_group = get_env_var("OPENNEBULA_SANDBOX_GROUP")
    exist_group = get_group(group_name=default_group)
    if exist_group is None:
        group_name = ask_text(
            "Enter the name for the OpenNebula group:",
            default=default_group,
            validate=True
        )
        group_name_data = get_group(group_name=group_name)
        if group_name_data is None:
            group_id = create_group(group_name=group_name)
            assign_user_group(username=username, group_name=group_name)
            add_admin_user_group(username=username, group_name=group_name)
            add_acl(group_id=group_id, resources="CLUSTER+NET")
    else:
        group_name = default_group
    
    return group_name, username
