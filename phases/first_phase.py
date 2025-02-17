from phases.utils.file import get_env_var
from phases.utils.interactive import ask_text, ask_password
from phases.utils.logs import msg
from phases.utils.one import get_group, create_group, get_username, create_user, assign_user_group
from phases.utils.string import validate_length
from phases.utils.temp import save_temp_file

def first_phase() -> tuple:
    msg("info", "FIRST PHASE")
    default_sandbox_group = get_env_var("OPENNEBULA_SANDBOX_GROUP")
    exist_group = get_group(group_name=default_sandbox_group)
    if exist_group is None:
        sixg_sandbox_group = ask_text("Enter the name for the 6G-SANDBOX group:", default=default_sandbox_group, validate=True)
        sixg_sandbox_group_data = get_group(group_name=sixg_sandbox_group)
        if sixg_sandbox_group_data is None:
            _ = create_group(group_name=sixg_sandbox_group)
    else:
        sixg_sandbox_group = default_sandbox_group
    default_jenkins_user = get_env_var("OPENNEBULA_JENKINS_USER")
    exist_user = get_username(username=default_jenkins_user)
    if exist_user is None:
        jenkins_user = ask_text("Enter the username for the Jenkins user:", default=default_jenkins_user, validate=lambda v: validate_length(v, 5))
        jenkins_user_data = get_username(username=jenkins_user)
        if jenkins_user_data is None:
            jenkins_password = ask_password("Enter the password for the Jenkins user:", validate=lambda v: validate_length(v, 5))
            save_temp_file(data=jenkins_password, file_path=jenkins_user, mode="wt", encoding="utf-8")
            _ = create_user(username=jenkins_user, password=jenkins_password)
    else:
        jenkins_user = default_jenkins_user
    assign_user_group(username=jenkins_user, group_name=sixg_sandbox_group)
    return sixg_sandbox_group, jenkins_user