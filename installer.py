from utils.file import load_dotenv_file, get_pyproject_toml_version
from utils.git import git_team_access, git_validate_token
from utils.logs import msg, setup_logger
from utils.one import (
    check_one_health, get_onegroup_id, get_onegroups_names, 
    get_oneflow_custom_attr_value, get_oneflow_role_vm_name, 
    get_oneusernames, get_oneusername_id, get_onevm_user_template_param, 
    oneacl_create, oneflow_template_instantiate, onegroup_addadmin, 
    onegroup_create, onemarket_create, oneuser_chgrp, oneuser_create, 
    oneuser_update_public_ssh_key, onemarketapp_add, onevm_disk_resize
)
from utils.os import get_dotenv_var
from utils.parser import decode_base64
from utils.questionary import ask_password, ask_select, ask_text
from utils.temp import create_temp_directory, save_temp_directory, TEMP_DIRECTORY

try:

    load_dotenv_file()
    setup_logger()
    msg(
        level="info",
        message="Proceeding to install the toolkit in OpenNebula"
    )

    # dotenv variables
    marketplace_monitoring_interval = get_dotenv_var(key="MARKETPLACE_MONITORING_INTERVAL")
    opennebula_public_marketplace_name = get_dotenv_var(key="OPENNEBULA_PUBLIC_MARKETPLACE_NAME")
    opennebula_public_marketplace_description = get_dotenv_var(key="OPENNEBULA_PUBLIC_MARKETPLACE_DESCRIPTION")
    opennebula_public_marketplace_endpoint = get_dotenv_var(key="OPENNEBULA_PUBLIC_MARKETPLACE_ENDPOINT")
    opennebula_sandbox_marketplace_name = get_dotenv_var(key="OPENNEBULA_SANDBOX_MARKETPLACE_NAME")
    opennebula_sandbox_marketplace_description = get_dotenv_var(key="OPENNEBULA_SANDBOX_MARKETPLACE_DESCRIPTION")
    opennebula_sandbox_marketplace_endpoint = get_dotenv_var(key="OPENNEBULA_SANDBOX_MARKETPLACE_ENDPOINT")
    marketapp_toolkit_service = get_dotenv_var(key="MARKETAPP_TOOLKIT_SERVICE")
    toolkit_service_sites_ansible_token = get_dotenv_var(key="TOOLKIT_SERVICE_SITES_ANSIBLE_TOKEN")
    toolkit_service_minio_role = get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_ROLE")
    toolkit_service_jenkins_role = get_dotenv_var(key="TOOLKIT_SERVICE_JENKINS_ROLE")
    toolkit_service_jenkins_ssh_key_param = get_dotenv_var(key="TOOLKIT_SERVICE_JENKINS_SSH_KEY_PARAM")
    toolkit_service_minio_disk_id = get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_DISK_ID")
    toolkit_service_minio_disk_size = get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_DISK_SIZE")
    github_organization_name = get_dotenv_var(key="GITHUB_ORGANIZATION_NAME")
    github_sites_team_name = get_dotenv_var(key="GITHUB_SITES_TEAM_NAME")
    github_members_token_encode = get_dotenv_var(key="GITHUB_MEMBERS_TOKEN")
    github_members_token = decode_base64(encoded_data=github_members_token_encode)
    sites_https_url = get_dotenv_var(key="SITES_HTTPS_URL")
    sites_repository_name = get_dotenv_var(key="SITES_REPOSITORY_NAME")

    # pyproject metadata
    toolkit_installer_version = get_pyproject_toml_version()

    # message
    msg(
        level="info",
        message=(
            "Toolkit installer is a Python script developed for the 6G-SANDBOX project, designed to facilitate the creation of new 6G-SANDBOX sites. "
            "This script automates the installation of the MinIO, Jenkins and TNLCM stack in OpenNebula using the toolkit service. "
            "The script will guide you through the installation process. "
            f"Please read the official documentation https://6g-sandbox.github.io/docs/{toolkit_installer_version}/toolkit-installer/installation and follow the instructions carefully. "
            "It is very important to complete all the requirements indicated in the documentation before running this script "
        )
    )

    # temporary directory
    msg(level="info", message="Creating temporary directory")
    create_temp_directory()
    msg(level="info", message=f"Temporary directory created in path: {TEMP_DIRECTORY}")
    
    # validation
    msg(
        level="info",
        message=(
            "Proceed to validate: \n "
            "1) if the script is running in the OpenNebula frontend \n "
            f"2) if the user executing the script is a member of the {github_sites_team_name} which is a team defined in the {github_organization_name} organization: https://github.com/orgs/{github_organization_name}/teams/{github_sites_team_name} \n "
            f"3) if the user executing the script has a token with access to the {sites_repository_name} which is a repository defined in the {github_organization_name} organization: https://github.com/{github_organization_name}/{sites_repository_name} "
        )
    )
    msg(level="info", message="Checking OpenNebula health")
    check_one_health()
    msg(level="info", message="OpenNebula is healthy")
    github_username = ask_text(
        message=f"Introduce the username that has been given access to the team {github_sites_team_name} in the organization {github_organization_name}:",
        validate=lambda github_username: (
            "Username is required" if not github_username else
            True
        )
    )
    msg(
        level="info",
        message=f"Validating if user {github_username} has access to the team {github_sites_team_name} in the organization {github_organization_name}"
    )
    git_team_access(
        github_token=github_members_token,
        github_organization_name=github_organization_name,
        github_team_name=github_sites_team_name,
        github_username=github_username
    )
    msg(
        level="info",
        message=f"User {github_username} has access to the team {github_sites_team_name} in the organization {github_organization_name}"
    )
    sites_github_token = ask_text(
        message=f"Introduce the personal access token of the user {github_username} with access to the {sites_repository_name} repository:",
        validate=lambda sites_github_token: (
            "Token is required" if not sites_github_token else
            True
        )
    )
    msg(
        level="info",
        message=f"Validating if the personal access token of the user {github_username} with access to the {sites_repository_name} repository is correct"
    )
    sites_path = save_temp_directory(path=sites_repository_name)
    git_validate_token(https_url=sites_https_url, path=sites_path, token=sites_github_token)
    msg(level="info", message="Token validated successfully")

    # user
    usernames = get_oneusernames()
    msg(
        level="info",
        message="User in OpenNebula is required to manage the trial networks deployed in 6G-SANDBOX. We recommend to create a new user for this purpose"
    )
    username = ask_select(
        message="Select an existing OpenNebula username or create a new one",
        choices=["Create new user"] + usernames
    )
    if username == "Create new user":
        username = ask_text(
            message="Introduce new OpenNebula username:",
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
        msg(level="info", message=f"User {username} already exists in OpenNebula")
    
    # group
    groups_names = get_onegroups_names()
    msg(
        level="info",
        message="Group in OpenNebula is required to manage the trial networks deployed in 6G-SANDBOX. We recommend to create a new group for this purpose"
    )
    group_name = ask_select(
        message="Select an existing OpenNebula group name or create a new one",
        choices=["Create new group"] + groups_names
    )
    if group_name == "Create new group":
        group_name = ask_text(
            message="Introduce new OpenNebula group name:",
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
        msg(level="info", message=f"Group {group_name} already exists in OpenNebula")
    
    # permissions
    oneuser_chgrp(username=username, group_name=group_name)
    msg(level="info", message=f"User {username} added to group {group_name}")
    onegroup_addadmin(username=username, group_name=group_name)
    msg(level="info", message=f"User {username} added to group {group_name} as admin")
    oneacl_create(group_id=group_id, resources="NET+CLUSTER/*", rights="USE+MANAGE+ADMIN+CREATE *")
    msg(level="info", message=f"Permissions for user {username} in group {group_name} created successfully")

    # marketplaces
    _ = onemarket_create(
        marketplace_name=opennebula_public_marketplace_name,
        marketplace_description=opennebula_public_marketplace_description,
        marketplace_endpoint=opennebula_public_marketplace_endpoint,
        marketplace_monitoring_interval=marketplace_monitoring_interval
    )
    msg(level="info", message=f"Marketplace {opennebula_public_marketplace_name} created successfully")
    _ = onemarket_create(
        marketplace_name=opennebula_sandbox_marketplace_name,
        marketplace_description=opennebula_sandbox_marketplace_description,
        marketplace_endpoint=opennebula_sandbox_marketplace_endpoint,
        marketplace_monitoring_interval=marketplace_monitoring_interval
    )
    msg(level="info", message=f"Marketplace {opennebula_sandbox_marketplace_name} created successfully")
    onemarketapp_add(
        group_name=group_name,
        username=username,
        marketplace_name=opennebula_sandbox_marketplace_name,
        appliances=[marketapp_toolkit_service]
    )
    msg(level="info", message=f"Marketapp/appliance {marketapp_toolkit_service} added")
    
    # toolkit service
    msg(
        level="info",
        message=(
            f"Proceeding to instantiate the service {marketapp_toolkit_service} in OpenNebula. "
            "The service automates the deployment of the MinIO, Jenkins and TNLCM virtual machines in OpenNebula"
        )
    )
    _ = oneflow_template_instantiate(
        oneflow_template_name=marketapp_toolkit_service,
        username=username, group_name=group_name
    ) # TODO: validate length of custom attrs values
    msg(level="info", message=f"Service {marketapp_toolkit_service} instantiated successfully")
    msg(
        level="info",
        message=(
            f"Adding Jenkins public SSH key to user {username}. "
            f"The public SSH key generated by the Jenkins virtual machine needs to be added to the user {username} in order to deploy trial networks. "
            "The public SSH key is stored in the user template of the Jenkins virtual machine."
            )
    )
    jenkins_vm = get_oneflow_role_vm_name(
        oneflow_name=marketapp_toolkit_service,
        oneflow_role=toolkit_service_jenkins_role
    )
    jenkins_ssh_key = get_onevm_user_template_param(
        vm_name=jenkins_vm,
        param=toolkit_service_jenkins_ssh_key_param
    )
    sites_ansible_token = get_oneflow_custom_attr_value(
        oneflow_name=marketapp_toolkit_service,
        attr_key=toolkit_service_sites_ansible_token
    )
    oneuser_update_public_ssh_key(username=username, public_ssh_key=jenkins_ssh_key)
    msg(level="info", message=f"Public SSH key added to user {username}")
    msg(
        level="info",
        message=f"Resizing MinIO disk {toolkit_service_minio_disk_id} to {toolkit_service_minio_disk_size} GB"
    )
    minio_vm = get_oneflow_role_vm_name(
        oneflow_name=marketapp_toolkit_service,
        oneflow_role=toolkit_service_minio_role
    )
    onevm_disk_resize(
        vm_name=minio_vm,
        disk_id=toolkit_service_minio_disk_id,
        size=int(toolkit_service_minio_disk_size)
    )
    msg(
        level="info",
        message=f"Disk {toolkit_service_minio_disk_id} resized to {toolkit_service_minio_disk_size} GB"
    )

    # sites


    # msg(level="info", message="Toolkit installation process completed successfully")

except KeyboardInterrupt:
    print("Operation interrupted by user")
    exit(1)

except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)
