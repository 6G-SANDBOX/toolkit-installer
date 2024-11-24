from src.utils.file import get_env_var
from src.utils.interactive import ask_text, ask_password
from src.utils.logs import msg
from src.utils.one import get_group, get_group_id, create_group, get_user, get_user_id, create_user, assign_user_group

def second_phase() -> None:
    msg("info", "SECOND PHASE")
    default_sandbox_group = get_env_var("OPENNEBULA_SANDBOX_GROUP")
    sixg_sandbox_group = ask_text("Enter the name for the 6G-SANDBOX group:", default=default_sandbox_group, validate=True)
    sixg_sandbox_group_data = get_group(group_name=sixg_sandbox_group)
    if sixg_sandbox_group_data is None:
        sixg_sandbox_group_id = create_group(group_name=sixg_sandbox_group)
    else:
        sixg_sandbox_group_id = get_group_id(sixg_sandbox_group)
    default_jenkins_user = get_env_var("OPENNEBULA_JENKINS_USER")
    jenkins_user = ask_text("Enter the username for the Jenkins user:", default=default_jenkins_user, validate=True)
    jenkins_user_data = get_user(username=jenkins_user)
    if jenkins_user_data is None:
        jenkins_password = ask_password("Enter the password for the Jenkins user:", validate=True)
        jenkins_user_id = create_user(username=jenkins_user, password=jenkins_password)
    else:
        jenkins_user_id = get_user_id(jenkins_user)
    assign_user_group(user_id=jenkins_user_id, group_id=sixg_sandbox_group_id)
    
    return sixg_sandbox_group_id, jenkins_user_id