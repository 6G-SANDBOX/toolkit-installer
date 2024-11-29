from src.utils.file import get_env_var
from src.utils.interactive import ask_text, ask_password
from src.utils.logs import msg
from src.utils.one import get_group, create_group, get_username, create_user, assign_user_group
from src.utils.temp import save_temp_file

def first_phase() -> tuple:
    msg("info", "FIRST PHASE")
    default_sandbox_group = get_env_var("OPENNEBULA_SANDBOX_GROUP")
    sixg_sandbox_group = ask_text("Enter the name for the 6G-SANDBOX group:", default=default_sandbox_group, validate=True)
    sixg_sandbox_group_data = get_group(group_name=sixg_sandbox_group)
    if sixg_sandbox_group_data is None:
        _ = create_group(group_name=sixg_sandbox_group)
    default_jenkins_user = get_env_var("OPENNEBULA_JENKINS_USER")
    jenkins_user = ask_text("Enter the username for the Jenkins user:", default=default_jenkins_user, validate=True)
    jenkins_user_data = get_username(username=jenkins_user)
    if jenkins_user_data is None:
        jenkins_password = ask_password("Enter the password for the Jenkins user:", validate=True)
        save_temp_file(data=jenkins_password, file_path=jenkins_user, mode="wt", encoding="utf-8")
        _ = create_user(username=jenkins_user, password=jenkins_password)
    assign_user_group(username=jenkins_user, group_name=sixg_sandbox_group)
    
    return sixg_sandbox_group, jenkins_user