from utils.file import load_dotenv_file
from utils.git import git_team_access
from utils.logs import msg, setup_logger
from utils.one import check_one_health, get_onegroup_id, get_onegroups_names, get_oneflow_custom_attr_value, get_oneflow_role_vm_name, get_oneusernames, get_oneusername_id, get_onevm_user_template_param, oneacl_create, oneflow_template_instantiate, onegroup_addadmin, onegroup_create, onemarket_create, oneuser_chgrp, oneuser_create, oneuser_update_public_ssh_key, onemarketapp_add, onevm_disk_resize
from utils.os import get_dotenv_var
from utils.questionary import ask_password, ask_select, ask_text
from utils.temp import create_temp_directory, TEMP_DIRECTORY

try:

    load_dotenv_file()
    setup_logger()
    msg(level="info", message="Proceeding to install the toolkit in OpenNebula")
    msg(level="info", message="Toolkit installer is a Python script developed for the 6G-SANDBOX project, designed to facilitate the creation of new 6G-SANDBOX sites. This script automates the installation of the MinIO, Jenkins and TNLCM stack in OpenNebula using the toolkit service. The script will guide you through the installation process. Please follow the instructions carefully")

    # validation
    msg(level="info", message="As mentioned in the documentation: https://6g-sandbox.github.io/docs/toolkit-installer/installation, proceed to validate if the script is running in the OpenNebula frontend and if the user executing the script is a member of the 6g-sandbox-sites-contributors team https://github.com/orgs/6G-SANDBOX/teams/6gsandbox-sites-contributors")
    msg(level="info", message="Checking OpenNebula health")
    check_one_health()
    msg(level="info", message="OpenNebula is healthy")
    github_username = ask_text(
        message="Introduce the username that has been given access to the 6g-sandbox-sites-contributors team:",
        validate=lambda github_username: (
            "Username is required" if not github_username else
            True
        )
    )
    github_organization_name = get_dotenv_var(key="GITHUB_ORGANIZATION_NAME")
    github_team_name = get_dotenv_var(key="SITES_TEAM_NAME")
    msg(level="info", message=f"Validating if user {github_username} has access to the team {github_team_name} in the organization {github_organization_name}")
    git_team_access(github_token=get_dotenv_var(key="SITES_TOKEN"), github_organization_name=github_organization_name, github_team_name=github_team_name, github_username=github_username)
    msg(level="info", message=f"User {github_username} has access to the team {github_team_name} in the organization {github_organization_name}")

    # temporary directory
    msg(level="info", message="Creating temporary directory")
    create_temp_directory()
    msg(level="info", message=f"Temporary directory created in path: {TEMP_DIRECTORY}")

    # user
    usernames = get_oneusernames()
    msg(level="info", message="User in OpenNebula is required to manage the trial networks deployed in 6G-SANDBOX. We recommend to create a new user for this purpose")
    username = ask_select(
        message="Select an existing OpenNebula username or create a new one",
        choices=["Create new user"] + usernames
    )
    if username == "Create new user":
        username = ask_text(
            message="Introduce new OpenNebula username:",
            default="",
            validate=lambda username: (
                "Username must be at least 8 characters long" if len(username) < 8 else
                "Username already exists" if username in usernames else
                True
            )
        )
        password = ask_password(
            message=f"Introduce the password for user {username}:",
            validate=lambda password: 
                "Password must be at least 8 characters long" if len(password) < 8 else
                True
        )
        username_id = oneuser_create(username=username, password=password)
        msg(level="info", message=f"User {username} created successfully")
    else:
        username_id = get_oneusername_id(username=username)
        msg(level="info", message=f"User {username} already exists")
    
    # group
    groups_names = get_onegroups_names()
    msg(level="info", message="Group in OpenNebula is required to manage the trial networks deployed in 6G-SANDBOX. We recommend to create a new group for this purpose")
    group_name = ask_select(
        message="Select an existing OpenNebula group name or create a new one",
        choices=["Create new group"] + groups_names
    )
    if group_name == "Create new group":
        group_name = ask_text(
            message="Introduce new OpenNebula group name:",
            default="",
            validate=lambda group_name: (
                "Group name must be at least 8 characters long" if len(group_name) < 8 else
                "Group name already exists" if group_name in groups_names else
                True
            )
        )
        group_id = onegroup_create(group_name=group_name)
        msg(level="info", message=f"Group {group_name} created successfully")
    else:
        group_id = get_onegroup_id(group_name=group_name)
        msg(level="info", message=f"Group {group_name} already exists")
    
    # permissions
    oneuser_chgrp(username=username, group_name=group_name)
    msg(level="info", message=f"User {username} added to group {group_name}")
    onegroup_addadmin(username=username, group_name=group_name)
    msg(level="info", message=f"User {username} added to group {group_name} as admin")
    oneacl_create(group_id=group_id, resources="NET+CLUSTER/*", rights="USE+MANAGE+ADMIN+CREATE *")
    msg(level="info", message=f"Permissions for user {username} in group {group_name} created successfully")

    # marketplaces
    marketplace_monitoring_interval = get_dotenv_var(key="MARKETPLACE_MONITORING_INTERVAL")
    _ = onemarket_create(
        marketplace_name=get_dotenv_var(key="OPENNEBULA_PUBLIC_MARKETPLACE_NAME"),
        marketplace_description=get_dotenv_var(key="OPENNEBULA_PUBLIC_MARKETPLACE_DESCRIPTION"),
        marketplace_endpoint=get_dotenv_var(key="OPENNEBULA_PUBLIC_MARKETPLACE_ENDPOINT"),
        marketplace_monitoring_interval=marketplace_monitoring_interval
    )
    msg(level="info", message=f"Marketplace {get_dotenv_var(key="OPENNEBULA_PUBLIC_MARKETPLACE_NAME")} created successfully")
    _ = onemarket_create(
        marketplace_name=get_dotenv_var(key="OPENNEBULA_SANDBOX_MARKETPLACE_NAME"),
        marketplace_description=get_dotenv_var(key="OPENNEBULA_SANDBOX_MARKETPLACE_DESCRIPTION"),
        marketplace_endpoint=get_dotenv_var(key="OPENNEBULA_SANDBOX_MARKETPLACE_ENDPOINT"),
        marketplace_monitoring_interval=marketplace_monitoring_interval
    )
    msg(level="info", message=f"Marketplace {get_dotenv_var(key="OPENNEBULA_SANDBOX_MARKETPLACE_NAME")} created successfully")
    onemarketapp_add(
        group_name=group_name,
        username=username,
        marketplace_name=get_dotenv_var(key="OPENNEBULA_SANDBOX_MARKETPLACE_NAME"),
        appliances=[get_dotenv_var(key="MARKETAPP_TOOLKIT_SERVICE")]
    )
    msg(level="info", message=f"Appliance {get_dotenv_var(key="MARKETAPP_TOOLKIT_SERVICE")} added")
    
    # toolkit service
    msg(level="info", message=f"Proceeding to instantiate the service {get_dotenv_var(key="MARKETAPP_TOOLKIT_SERVICE")} in OpenNebula. The service automates the deployment of the MinIO, Jenkins and TNLCM virtual machines in OpenNebula")
    _ = oneflow_template_instantiate(oneflow_template_name=get_dotenv_var(key="MARKETAPP_TOOLKIT_SERVICE"), username=username, group_name=group_name)
    msg(level="info", message=f"Service {get_dotenv_var(key="MARKETAPP_TOOLKIT_SERVICE")} instantiated successfully")
    msg(level="info", message=f"Adding Jenkins public SSH key to user {username}. The public SSH key generated by the Jenkins virtual machine needs to be added to the user {username} in order to deploy trial networks. The public SSH key is stored in the user template of the Jenkins virtual machine")
    jenkins_vm = get_oneflow_role_vm_name(oneflow_name=get_dotenv_var(key="MARKETAPP_TOOLKIT_SERVICE"), oneflow_role=get_dotenv_var(key="TOOLKIT_SERVICE_JENKINS_ROLE"))
    jenkins_ssh_key = get_onevm_user_template_param(vm_name=jenkins_vm, param=get_dotenv_var(key="TOOLKIT_SERVICE_JENKINS_SSH_KEY_PARAM"))
    sites_ansible_token = get_oneflow_custom_attr_value(oneflow_name=get_dotenv_var(key="MARKETAPP_TOOLKIT_SERVICE"), attr_key=get_dotenv_var(key="TOOLKIT_SERVICE_SITES_ANSIBLE_TOKEN"))
    oneuser_update_public_ssh_key(username=username, public_ssh_key=jenkins_ssh_key)
    msg(level="info", message=f"Public SSH key added to user {username}")
    msg(level="info", message=f"Resizing MinIO disk {get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_DISK_ID")} to {get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_DISK_SIZE")} GB")
    minio_vm = get_oneflow_role_vm_name(oneflow_name=get_dotenv_var(key="MARKETAPP_TOOLKIT_SERVICE"), oneflow_role=get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_ROLE"))
    onevm_disk_resize(vm_name=minio_vm, disk_id=get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_DISK_ID"), size=int(get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_DISK_SIZE")))
    msg(level="info", message=f"Disk {get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_DISK_ID")} resized to {get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_DISK_SIZE")} GB")
    # sites

    # msg(level="info", message="Toolkit installation process completed successfully")

except KeyboardInterrupt:
    print("Operation interrupted by user")
    exit(1)

except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)
