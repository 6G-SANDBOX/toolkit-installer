from typing import Dict, List

from dotenv import load_dotenv

from utils.cli import run_command
from utils.file import (
    SITES_SKIP_KEYS,
    is_encrypted_ansible,
    load_yaml,
    loads_json,
    read_component_site_variables,
    read_site_yaml,
    save_file,
    save_yaml_file,
)
from utils.git import (
    git_add,
    git_branches,
    git_checkout,
    git_clean_fd,
    git_clone,
    git_commit,
    git_create_branch,
    git_current_branch,
    git_detect_changes,
    git_fetch_prune,
    git_pull,
    git_push,
    git_reset_hard,
    git_sync_branches,
    git_team_access,
    git_validate_token,
)
from utils.logs import msg, setup_logger
from utils.one import (
    check_one_health,
    oneacl_create,
    oneflow_custom_attr_value,
    oneflow_role_vm_name,
    onegate_endpoint,
    onegroup_addadmin,
    onegroup_create,
    onegroup_id,
    onegroups_names,
    onehost_cpu_model,
    onehosts_avx_cpu_mem,
    onemarket_create,
    onemarket_show,
    onemarketapp_add,
    onemarketapp_instantiate,
    onemarketapp_name,
    oneuser_chgrp,
    oneuser_create,
    oneuser_update_public_ssh_key,
    oneusername_id,
    oneusernames,
    onevm_cpu_model,
    onevm_deploy,
    onevm_disk_resize,
    onevm_ip,
    onevm_undeploy_hard,
    onevm_updateconf_cpu_model,
    onevm_user_input,
    onevm_user_template_param,
)
from utils.os import (
    DOTENV_PATH,
    TEMP_DIRECTORY,
    get_dotenv_var,
    join_path,
    list_dirs_no_hidden,
    make_directory,
    remove_directory,
    remove_file,
    rename_directory,
)
from utils.parser import ansible_decrypt, ansible_encrypt, decode_base64, encode_base64
from utils.questionary import (
    ask_checkbox,
    ask_confirm,
    ask_password,
    ask_select,
    ask_text,
)

try:
    # configuration
    load_dotenv(dotenv_path=DOTENV_PATH)
    setup_logger()

    # dotenv variables
    sandbox_documentation_url = get_dotenv_var(key="SANDBOX_DOCUMENTATION_URL")
    marketplace_monitoring_interval = get_dotenv_var(
        key="MARKETPLACE_MONITORING_INTERVAL"
    )
    opennebula_public_marketplace_name = get_dotenv_var(
        key="OPENNEBULA_PUBLIC_MARKETPLACE_NAME"
    )
    opennebula_public_marketplace_description = get_dotenv_var(
        key="OPENNEBULA_PUBLIC_MARKETPLACE_DESCRIPTION"
    )
    opennebula_public_marketplace_endpoint = get_dotenv_var(
        key="OPENNEBULA_PUBLIC_MARKETPLACE_ENDPOINT"
    )
    opennebula_sandbox_marketplace_name = get_dotenv_var(
        key="OPENNEBULA_SANDBOX_MARKETPLACE_NAME"
    )
    opennebula_sandbox_marketplace_description = get_dotenv_var(
        key="OPENNEBULA_SANDBOX_MARKETPLACE_DESCRIPTION"
    )
    opennebula_sandbox_marketplace_endpoint = get_dotenv_var(
        key="OPENNEBULA_SANDBOX_MARKETPLACE_ENDPOINT"
    )
    appliance_toolkit_service_url = get_dotenv_var(key="APPLIANCE_TOOLKIT_SERVICE_URL")
    toolkit_service_sites_ansible_token = get_dotenv_var(
        key="TOOLKIT_SERVICE_SITES_ANSIBLE_TOKEN"
    )
    toolkit_service_minio_role = get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_ROLE")
    toolkit_service_jenkins_role = get_dotenv_var(key="TOOLKIT_SERVICE_JENKINS_ROLE")
    toolkit_service_tnlcm_role = get_dotenv_var(key="TOOLKIT_SERVICE_TNLCM_ROLE")
    tnlcm_default_cpu_model = get_dotenv_var(key="TNLCM_DEFAULT_CPU_MODEL")
    toolkit_service_jenkins_ssh_key_param = get_dotenv_var(
        key="TOOLKIT_SERVICE_JENKINS_SSH_KEY_PARAM"
    )
    toolkit_service_minio_disk_id = get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_DISK_ID")
    toolkit_service_minio_disk_size = int(
        get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_DISK_SIZE")
    )
    min_percentage_cpu_available_host = int(
        get_dotenv_var(key="MIN_PERCENTAGE_CPU_AVAILABLE_HOST")
    )
    min_percentage_mem_available_host = int(
        get_dotenv_var(key="MIN_PERCENTAGE_MEM_AVAILABLE_HOST")
    )
    appliance_technitium_url = get_dotenv_var(key="APPLIANCE_TECHNITIUM_URL")
    appliance_route_manager_api_url = get_dotenv_var(
        key="APPLIANCE_ROUTE_MANAGER_API_URL"
    )
    route_manager_api_token_param = get_dotenv_var(key="ROUTE_MANAGER_API_TOKEN_PARAM")
    github_organization_name = get_dotenv_var(key="GITHUB_ORGANIZATION_NAME")
    github_sites_team_name = get_dotenv_var(key="GITHUB_SITES_TEAM_NAME")
    github_members_token_encode = get_dotenv_var(key="GITHUB_MEMBERS_TOKEN")
    github_members_token = decode_base64(encoded_data=github_members_token_encode)
    sites_https_url = get_dotenv_var(key="SITES_HTTPS_URL")
    sites_repository_name = get_dotenv_var(key="SITES_REPOSITORY_NAME")
    dummy_site_url = get_dotenv_var(key="DUMMY_SITE_URL")
    library_https_url = get_dotenv_var(key="LIBRARY_HTTPS_URL")
    library_repository_name = get_dotenv_var(key="LIBRARY_REPOSITORY_NAME")
    library_ref = get_dotenv_var(key="LIBRARY_REF")
    trial_network_component = get_dotenv_var(key="TRIAL_NETWORK_COMPONENT")
    pipeline_tn_deploy = get_dotenv_var(key="PIPELINE_TN_DEPLOY")
    tnlcm_port = get_dotenv_var(key="TNLCM_PORT")

    # message
    msg(
        level="info",
        message=(
            f"Proceeding to install 6G-SANDBOX toolkit in OpenNebula. "
            "Toolkit installer is a Python script developed for the 6G-SANDBOX project, designed to facilitate the creation of new 6G-SANDBOX sites. "
            "This script automates the installation of the MinIO, Jenkins and TNLCM stack in OpenNebula using the toolkit service. "
            f"Please read the official documentation {sandbox_documentation_url}/toolkit-installer/installation and follow the instructions carefully. "
            "It is very important to complete all the requirements indicated in the documentation before running this script. "
            "The script will guide you through the installation process. If you skip using Ctrl+C, the script will be interrupted and later you can continue from where you left off"
        ),
    )

    # temporary directory
    msg(level="info", message="Creating temporary directory")
    make_directory(path=TEMP_DIRECTORY)
    msg(level="info", message=f"Temporary directory created in path: {TEMP_DIRECTORY}")

    # validation
    msg(
        level="info",
        message=(
            "Proceed to validate: \n "
            "1) if the script is running in the OpenNebula frontend \n "
            f"2) if the user executing the script is a member of the {github_sites_team_name} which is a team defined in the {github_organization_name} organization: https://github.com/orgs/{github_organization_name}/teams/{github_sites_team_name} \n "
            f"3) if the user executing the script has a token with access to the {sites_repository_name} which is a repository defined in the {github_organization_name} organization: https://github.com/{github_organization_name}/{sites_repository_name}"
        ),
    )
    msg(level="info", message="Checking OpenNebula health")
    check_one_health()
    msg(level="info", message=f"Your onegate endpoint is {onegate_endpoint()}")
    msg(level="info", message="OpenNebula is healthy")
    github_username = ask_text(
        message=f"Introduce the username that has been given access to the team {github_sites_team_name} in the organization {github_organization_name}:",
        validate=lambda github_username: (
            "Username is required" if not github_username else True
        ),
    )
    msg(
        level="info",
        message=f"Validating if user {github_username} has access to the team {github_sites_team_name} in the organization {github_organization_name}",
    )
    git_team_access(
        token=github_members_token,
        organization_name=github_organization_name,
        team_name=github_sites_team_name,
        username=github_username,
    )
    msg(
        level="info",
        message=f"User {github_username} has access to the team {github_sites_team_name} in the organization {github_organization_name}",
    )
    sites_github_token = ask_text(
        message=(
            f"Introduce the personal access token of the user {github_username} with access to the {sites_repository_name} repository. "
            f"This token must be created as indicated in the {sandbox_documentation_url}/toolkit-installer/installation#create-site-token section of the documentation:"
        ),
        validate=lambda sites_github_token: (
            "Token is required" if not sites_github_token else True
        ),
    )
    msg(
        level="info",
        message=f"Validating if the personal access token of the user {github_username} with access to the {sites_repository_name} repository is correct",
    )
    git_validate_token(
        token=sites_github_token,
        organization_name=github_organization_name,
        repository_name=sites_repository_name,
        username=github_username,
    )
    msg(level="info", message="Token validated successfully")

    # user
    usernames = oneusernames()
    msg(
        level="info",
        message="User in OpenNebula is required to manage the trial networks deployed in 6G-SANDBOX. We recommend to create a new user for this purpose",
    )
    username = ask_select(
        message="Select an existing OpenNebula username or create a new one:",
        choices=["Create new user"] + usernames,
    )
    if username == "Create new user":
        username = ask_text(
            message="Introduce new OpenNebula username:",
            validate=lambda username: (
                "Username must be at least 8 characters long"
                if len(username) < 8
                else "Username already exists"
                if username in usernames
                else True
            ),
        )
        password = ask_password(
            message=f"Introduce the password for user {username}:",
            validate=lambda password: "Password must be at least 8 characters long"
            if len(password) < 8
            else True,
        )
        username_id = oneuser_create(username=username, password=password)
        msg(level="info", message=f"User {username} created successfully")
    else:
        username_id = oneusername_id(username=username)
        msg(level="info", message=f"User {username} already exists in OpenNebula")

    # group
    groups_names = onegroups_names()
    msg(
        level="info",
        message="Group in OpenNebula is required to manage the trial networks deployed in 6G-SANDBOX. We recommend to create a new group for this purpose",
    )
    group_name = ask_select(
        message="Select an existing OpenNebula group name or create a new one:",
        choices=["Create new group"] + groups_names,
    )
    if group_name == "Create new group":
        group_name = ask_text(
            message="Introduce new OpenNebula group name:",
            validate=lambda group_name: (
                "Group name must be at least 8 characters long"
                if len(group_name) < 8
                else "Group name already exists"
                if group_name in groups_names
                else True
            ),
        )
        group_id = onegroup_create(group_name=group_name)
        msg(level="info", message=f"Group {group_name} created successfully")
    else:
        group_id = onegroup_id(group_name=group_name)
        msg(level="info", message=f"Group {group_name} already exists in OpenNebula")

    # permissions
    oneuser_chgrp(username=username, group_name=group_name)
    msg(level="info", message=f"User {username} added to group {group_name}")
    onegroup_addadmin(username=username, group_name=group_name)
    msg(level="info", message=f"User {username} added to group {group_name} as admin")
    oneacl_create(
        group_id=group_id, resources="NET+CLUSTER/*", rights="USE+MANAGE+ADMIN+CREATE *"
    )
    msg(
        level="info",
        message=f"Permissions for user {username} in group {group_name} created successfully",
    )

    # marketplaces
    if not onemarket_show(marketplace_name=opennebula_public_marketplace_name):
        _ = onemarket_create(
            marketplace_name=opennebula_public_marketplace_name,
            marketplace_description=opennebula_public_marketplace_description,
            marketplace_endpoint=opennebula_public_marketplace_endpoint,
            marketplace_monitoring_interval=marketplace_monitoring_interval,
        )
        msg(
            level="info",
            message=f"Marketplace {opennebula_public_marketplace_name} created successfully",
        )
    if not onemarket_show(marketplace_name=opennebula_sandbox_marketplace_name):
        _ = onemarket_create(
            marketplace_name=opennebula_sandbox_marketplace_name,
            marketplace_description=opennebula_sandbox_marketplace_description,
            marketplace_endpoint=opennebula_sandbox_marketplace_endpoint,
            marketplace_monitoring_interval=marketplace_monitoring_interval,
        )
        msg(
            level="info",
            message=f"Marketplace {opennebula_sandbox_marketplace_name} created successfully",
        )

    # toolkit service
    appliance_toolkit_service_name = onemarketapp_name(
        appliance_url=appliance_toolkit_service_url
    )
    is_toolkit_service_instantiated, appliance_toolkit_service_name = (
        onemarketapp_instantiate(
            appliance_url=appliance_toolkit_service_url,
            group_name=group_name,
            marketplace_name=opennebula_sandbox_marketplace_name,
            username=username,
        )
    )
    if not is_toolkit_service_instantiated:
        msg(
            level="error",
            message=f"Appliance {appliance_toolkit_service_name} not instantiated and is MANDATORY",
        )
    msg(
        level="info",
        message=(
            f"Adding Jenkins public SSH key to user {username}. "
            f"The public SSH key generated by the Jenkins virtual machine needs to be added to the user {username} in order to deploy trial networks. "
            "The public SSH key is stored in the user template of the Jenkins virtual machine."
        ),
    )
    jenkins_vm = oneflow_role_vm_name(
        oneflow_name=appliance_toolkit_service_name,
        oneflow_role=toolkit_service_jenkins_role,
    )
    jenkins_ssh_key = onevm_user_template_param(
        vm_name=jenkins_vm, param=toolkit_service_jenkins_ssh_key_param
    )
    sites_ansible_token = oneflow_custom_attr_value(
        oneflow_name=appliance_toolkit_service_name,
        attr_key=toolkit_service_sites_ansible_token,
    )
    sites_ansible_token_path = join_path(
        TEMP_DIRECTORY, toolkit_service_sites_ansible_token
    )
    save_file(
        data=sites_ansible_token,
        file_path=sites_ansible_token_path,
    )
    oneuser_update_public_ssh_key(username=username, public_ssh_key=jenkins_ssh_key)
    msg(level="info", message=f"Public SSH key added to user {username}")
    msg(
        level="info",
        message=f"Resizing MinIO disk with id {toolkit_service_minio_disk_id} to {toolkit_service_minio_disk_size} GB",
    )
    minio_vm = oneflow_role_vm_name(
        oneflow_name=appliance_toolkit_service_name,
        oneflow_role=toolkit_service_minio_role,
    )
    onevm_disk_resize(
        vm_name=minio_vm,
        disk_id=toolkit_service_minio_disk_id,
        size=toolkit_service_minio_disk_size,
    )
    msg(
        level="info",
        message=f"Disk with id {toolkit_service_minio_disk_id} resized to {toolkit_service_minio_disk_size} GB",
    )
    tnlcm_vm = oneflow_role_vm_name(
        oneflow_name=appliance_toolkit_service_name,
        oneflow_role=toolkit_service_tnlcm_role,
    )
    msg(
        level="info",
        message=f"The TNLCM virtual machine requires a CPU model with AVX support because it uses MongoDB. Readme more here: {sandbox_documentation_url}/toolkit-installer/installation#known-issues"
        "By default, the TNLCM virtual machine is configured with host-passthrough as the CPU model, but we RECOMMEND changing it to a CPU model with AVX support. "
        "Therefore, we proceed to read the hosts linked to OpenNebula and determine which of them are compatible with avx. "
        "Then, if there are compatible hosts, select the one where TNLCM will be deployed. "
        "If there are no compatible models, the default value is used: host-passthrough",
    )
    tnlcm_cpu_model = onevm_cpu_model(vm_name=tnlcm_vm)
    if tnlcm_cpu_model != tnlcm_default_cpu_model:
        msg(
            level="warning",
            message=(
                f"CPU model of the TNLCM virtual machine is {tnlcm_cpu_model} and not the default value {tnlcm_default_cpu_model} this means that the CPU model has been changed previously"
            ),
        )
    update_cpu_model = ask_confirm(
        message="Do you want to change the CPU model of the TNLCM virtual machine?",
        default=False,
    )
    if update_cpu_model:
        hosts_avx_cpu_mem = onehosts_avx_cpu_mem(
            min_percentage_cpu_available_host=min_percentage_cpu_available_host,
            min_percentage_mem_available_host=min_percentage_mem_available_host,
        )
        if hosts_avx_cpu_mem:
            host_tnlcm = ask_select(
                message=f"The following hosts support AVX and have an available CPU percentage greater than {min_percentage_cpu_available_host}% and an available MEM percentage greater than {min_percentage_mem_available_host}%. Select one:",
                choices=hosts_avx_cpu_mem,
            )
            onevm_undeploy_hard(vm_name=tnlcm_vm)
            host_cpu_model = onehost_cpu_model(host_name=host_tnlcm)
            onevm_updateconf_cpu_model(vm_name=tnlcm_vm, cpu_model=host_cpu_model)
            onevm_deploy(vm_name=tnlcm_vm, host_name=host_tnlcm)
            msg(
                level="info",
                message=f"CPU model of the TNLCM virtual machine changed to {host_cpu_model} and now deploy in host {host_tnlcm}",
            )
        else:
            msg(
                level="warning", message="No hosts with AVX support found in OpenNebula"
            )
    else:
        msg(
            level="info",
            message="The CPU model of the TNLCM virtual machine has not been changed",
        )

    # technitium
    appliance_technitium_name = onemarketapp_name(
        appliance_url=appliance_technitium_url
    )
    is_technitium_instantiated, appliance_technitium_name = onemarketapp_instantiate(
        appliance_url=appliance_technitium_url,
        group_name=group_name,
        marketplace_name=opennebula_sandbox_marketplace_name,
        username=username,
    )
    if not is_technitium_instantiated:
        msg(
            level="warning",
            message=f"Appliance {appliance_technitium_name} not instantiated and is optional",
        )

    # route-manager-api
    appliance_route_manager_api_name = onemarketapp_name(
        appliance_url=appliance_route_manager_api_url
    )
    is_route_manager_api_instantiated, appliance_route_manager_api_name = (
        onemarketapp_instantiate(
            appliance_url=appliance_route_manager_api_url,
            group_name=group_name,
            marketplace_name=opennebula_sandbox_marketplace_name,
            username=username,
        )
    )
    route_manager_api_token = None
    if is_route_manager_api_instantiated:
        route_manager_api_token = onevm_user_input(
            vm_name=appliance_route_manager_api_name,
            user_input=route_manager_api_token_param,
        )
    if not is_route_manager_api_instantiated:
        msg(
            level="warning",
            message=(
                f"Appliance {appliance_route_manager_api_name} not instantiated and is optional"
            ),
        )

    # sites
    msg(
        level="info",
        message=(
            f"Clone the {sites_repository_name} repository in the temporary directory {TEMP_DIRECTORY}. "
            f"The {sites_repository_name} repository contains the static information about the infrastructure, systems and available equipment of each site encrypted with ansible-vault for secutiry reasons. "
            f"Read the dummy site documentation here {dummy_site_url} before start with this process. Just fill in the requested fields. Some are autocomplete"
        ),
    )
    sites_path = join_path(TEMP_DIRECTORY, sites_repository_name)
    git_clone(https_url=sites_https_url, path=sites_path, token=sites_github_token)
    git_fetch_prune(path=sites_path)
    git_sync_branches(path=sites_path)
    sites = git_branches(path=sites_path)
    site = ask_select(
        message=(
            "Select an existing site or create a new one. If you select a site that already exists, the documentation is encrypted for security reasons. "
            f"Therefore, please note that the content will be decrypted using the key specified in the {toolkit_service_sites_ansible_token} field of the {appliance_toolkit_service_name} service selected in previous steps:"
        ),
        choices=["Create new site"] + sites,
    )
    if site != "Create new site":
        current_branch = git_current_branch(path=sites_path)
        if current_branch != site:
            if git_detect_changes(path=sites_path):
                git_reset_hard(path=sites_path)
                git_clean_fd(path=sites_path)
            git_checkout(path=sites_path, ref=site)
        site_path = join_path(sites_path, site)
        core_site_path = join_path(site_path, "core.yaml")
        if is_encrypted_ansible(file_path=core_site_path):
            ansible_decrypt(
                data_path=core_site_path,
                token_path=sites_ansible_token_path,
            )
        core_site_data = load_yaml(file_path=core_site_path)
    else:
        site = ask_text(
            message="Introduce new site name:",
            validate=lambda site: (
                "Site name must be at least 3 characters long"
                if len(site) < 3
                else "Site name already exists"
                if site in sites
                else True
            ),
        )
        if git_detect_changes(path=sites_path):
            git_reset_hard(path=sites_path)
            git_clean_fd(path=sites_path)
        git_create_branch(path=sites_path, new_branch=site, base_branch="main")
        remove_directory(path=join_path(sites_path, ".github"))
        remove_file(path=join_path(sites_path, "README.md"))
        dummy_site_path = join_path(sites_path, ".dummy_site")
        site_path = join_path(sites_path, site)
        rename_directory(
            new_path=site_path,
            old_path=dummy_site_path,
        )
        core_site_path = join_path(site_path, "core.yaml")
        core_site_data = load_yaml(file_path=core_site_path)
    site_data = read_site_yaml(data=core_site_data)
    for sites_key in SITES_SKIP_KEYS:
        if sites_key not in core_site_data:
            msg(
                level="error",
                message=f"Key {sites_key} not found in site {site} in repository {sites_repository_name}",
            )
    if is_technitium_instantiated:
        site_data["site_dns"] = onevm_ip(vm_name=appliance_technitium_name)
    else:
        site_data["site_dns"] = "8.8.8.8,1.1.1.1"
    site_data["site_hypervisor"] = "one"
    site_data["site_onegate"] = onegate_endpoint()
    site_data["site_s3_server"] = core_site_data["site_s3_server"]
    if "endpoint" not in core_site_data["site_s3_server"]:
        msg(
            level="error",
            message=f"Endpoint not found in site_s3_server in site {site} in repository {sites_repository_name}",
        )
    site_data["site_s3_server"]["endpoint"] = (
        f"https://{onevm_ip(vm_name=minio_vm)}:9000"
    )
    site_data["site_routemanager"] = core_site_data["site_routemanager"]
    if is_route_manager_api_instantiated:
        if "api_endpoint" not in core_site_data["site_routemanager"]:
            msg(
                level="error",
                message=f"API endpoint not found in site_routemanager in site {site} in repository {sites_repository_name}",
            )
        site_data["site_routemanager"]["api_endpoint"] = onevm_ip(
            vm_name=appliance_route_manager_api_name
        )
        if "token" not in core_site_data["site_routemanager"]:
            msg(
                level="error",
                message=f"Token not found in site_routemanager in site {site} in repository {sites_repository_name}",
            )
        site_data["site_routemanager"]["token"] = route_manager_api_token
    site_data["site_available_components"] = core_site_data["site_available_components"]

    # library
    msg(
        level="info",
        message=(
            f"Clone the {library_repository_name} repository in the temporary directory {TEMP_DIRECTORY}. "
            f"The {library_repository_name} repository contains the description of the components using YAML files and the ansible playbooks to deploy the components"
        ),
    )
    library_path = join_path(TEMP_DIRECTORY, library_repository_name)
    git_clone(https_url=library_https_url, path=library_path)
    git_pull(path=library_path)
    git_fetch_prune(path=library_path)
    git_sync_branches(path=library_path)
    git_checkout(path=library_path, ref=library_ref)
    library_components = list_dirs_no_hidden(path=library_path)
    if not library_components:
        msg(
            level="error",
            message=f"No components found in repository {library_repository_name} using ref {library_ref}",
        )
    msg(
        level="info",
        message=f"Proceed to read component by component of the {library_repository_name} to determine if you want to add it to your site {site}",
    )
    for component in library_components:
        component_data = load_yaml(
            file_path=join_path(library_path, component, ".tnlcm", "public.yaml")
        )
        if "metadata" not in component_data:
            msg(
                level="error",
                message=f"Metadata not found in component {component} in repository {library_repository_name} using ref {library_ref}",
            )
        metadata = component_data["metadata"]
        if not isinstance(metadata, Dict):
            msg(
                level="error",
                message=f"Metadata for component {component} in repository {library_repository_name} using ref {library_ref} is not a dictionary",
            )
        if "long_description" not in metadata:
            msg(
                level="error",
                message=f"Long description not found in component {component} in repository {library_repository_name} using ref {library_ref}",
            )
        long_description = metadata["long_description"]
        if not isinstance(long_description, str):
            msg(
                level="error",
                message=f"Long description for component {component} in repository {library_repository_name} using ref {library_ref} is not a string",
            )
        add_component = ask_confirm(
            message=(
                f"\nDo you want to add {component} component to your site? Very important to know the availability of the component in the site. Ask to the administrator of the site. \n{long_description}"
            ),
            default=False,
        )
        if add_component:
            if "appliances" not in component_data["metadata"]:
                if component not in site_data["site_available_components"]:
                    site_data["site_available_components"][component] = None
            else:
                if "site_variables" not in component_data:
                    msg(
                        level="error",
                        message=f"Site variables not found in component {component} in repository {library_repository_name} using ref {library_ref}",
                    )
                appliance_site_variables = component_data["site_variables"]
                if not isinstance(appliance_site_variables, Dict):
                    msg(
                        level="error",
                        message=f"Site variables for component {component} in repository {library_repository_name} using ref {library_ref} is not a dictionary",
                    )
                component_appliances_urls = component_data["metadata"]["appliances"]
                if not isinstance(component_appliances_urls, List):
                    msg(
                        level="error",
                        message=f"Appliances key for component {component} in repository {library_repository_name} using ref {library_ref} is not a list",
                    )
                if not component_appliances_urls:
                    msg(
                        level="error",
                        message=f"No appliances found for component {component} in repository {library_repository_name} using ref {library_ref}",
                    )
                component_appliances_names = []
                component_appliances_urls_names = {}
                for component_appliance_url in component_appliances_urls:
                    component_appliance_name = onemarketapp_name(
                        appliance_url=component_appliance_url
                    )
                    component_appliances_names.append(component_appliance_name)
                    component_appliances_urls_names[component_appliance_name] = (
                        component_appliance_url
                    )
                component_appliances_names_add = ask_checkbox(
                    message=f"Select the appliances that you want to add to the {site} site for the component {component}",
                    choices=component_appliances_names,
                )
                for component_appliance_name in component_appliances_names_add:
                    component_appliance_url = component_appliances_urls_names[
                        component_appliance_name
                    ]
                    if component_appliance_url.startswith(
                        opennebula_public_marketplace_endpoint
                    ):
                        is_added, _ = onemarketapp_add(
                            group_name=group_name,
                            username=username,
                            marketplace_name=opennebula_public_marketplace_name,
                            appliance_url=component_appliance_url,
                        )
                    elif component_appliance_url.startswith(
                        opennebula_sandbox_marketplace_endpoint
                    ):
                        is_added, _ = onemarketapp_add(
                            group_name=group_name,
                            username=username,
                            marketplace_name=opennebula_sandbox_marketplace_name,
                            appliance_url=component_appliance_url,
                        )
                    else:
                        msg(
                            level="error",
                            message=(
                                f"Appliance {component_appliance_name} not found in marketplaces {opennebula_public_marketplace_name} or {opennebula_sandbox_marketplace_name}"
                            ),
                        )
                appliance_site_variables = read_component_site_variables(
                    data=appliance_site_variables
                )
                site_data["site_available_components"][component] = (
                    appliance_site_variables
                )
    save_yaml_file(data=site_data, file_path=core_site_path)
    ansible_encrypt(data_path=core_site_path, token_path=sites_ansible_token_path)
    if git_detect_changes(path=site_path):
        git_add(path=site_path)
        git_commit(path=site_path, message=f"change: site {site}")
        git_push(path=site_path)
    msg(
        level="info",
        message=(
            f"Site {site} created/updated successfully with the components selected. "
            f"The site is stored in the {sites_repository_name} repository in the branch {site}. "
            f"Consider that the site {site} is encrypted with the {sites_ansible_token} key using ansible-vault. "
            f"If you want to update the site, you can re-run the script and select the {appliance_toolkit_service_name} service that has in the key {toolkit_service_sites_ansible_token} as value the key to decrypt the {site} site or you can follow this documentation: {sandbox_documentation_url}/6g-sandbox-sites/work-on-your-site "
        ),
    )

    # trial network
    deploy_trial_network = ask_confirm(
        message="Do you want to deploy a trial network in the site?",
        default=False,
    )
    if deploy_trial_network:
        tnlcm_ip = onevm_ip(vm_name=tnlcm_vm)
        tnlcm_url = f"http://{tnlcm_ip}:{tnlcm_port}"
        tnlcm_admin_user = onevm_user_input(
            vm_name=tnlcm_vm, user_input="ONEAPP_TNLCM_ADMIN_USER"
        )
        tnlcm_admin_password = onevm_user_input(
            vm_name=tnlcm_vm, user_input="ONEAPP_TNLCM_ADMIN_PASSWORD"
        )
        credentials = f"{tnlcm_admin_user}:{tnlcm_admin_password}"
        encoded_credentials = encode_base64(data=credentials)
        tnlcm_login = f'curl -w "%{{http_code}}" -X POST {tnlcm_url}/api/v1/user/login -H "accept: application/json" -H "authorization: Basic {encoded_credentials}"'
        stdout, stderr, rc = run_command(command=tnlcm_login)
        tokens, status_code = stdout[:-3].strip(), stdout[-3:]
        if status_code != "201":
            msg(
                level="error",
                message=f"Failed to login to TNLCM. Command: {tnlcm_login}. Error received: {stderr}. Return code: {rc}",
            )
        access_token = loads_json(data=tokens)["access_token"]
        msg(level="info", message="Logged in successfully to TNLCM")
        trial_network_path = join_path(
            library_path, trial_network_component, "sample_tnlcm_descriptor.yaml"
        )
        tnlcm_create_trial_network = f'''curl -w "%{{http_code}}" -X POST "{tnlcm_url}/api/v1/trial-network?validate=True" \
            -H "accept: application/json" \
            -H "Authorization: Bearer {access_token}" \
            -H "Content-Type: multipart/form-data" \
            -F "tn_id=test" \
            -F "descriptor=@{trial_network_path}" \
            -F "library_reference_type=branch" \
            -F "library_reference_value={library_ref}" \
            -F "sites_branch={site}" \
            -F "deployment_site={site}"'''
        stdout, stderr, rc = run_command(command=tnlcm_create_trial_network)
        response_create_trial_network, status_code = stdout[:-3].strip(), stdout[-3:]
        if status_code != "201":
            msg(
                level="error",
                message=f"Failed to create trial network in TNLCM. Command: {tnlcm_create_trial_network}. Error received: {stderr}. Return code: {rc}",
            )
        trial_network_id = loads_json(data=response_create_trial_network)["tn_id"]
        msg(
            level="info",
            message=f"Trial network {trial_network_id} created successfully in TNLCM",
        )
        deploy_trial_network = f'''curl -w "%{{http_code}}" -X POST "{tnlcm_url}/api/v1/trial-network/{trial_network_id}/activate" \
            -H "accept: application/json" \
            -H "Authorization: Bearer {access_token}"'''
        stdout, stderr, rc = run_command(command=deploy_trial_network)
        response_deploy_trial_network, status_code = stdout[:-3].strip(), stdout[-3:]
        if status_code != "200":
            msg(
                level="error",
                message=f"Failed to deploy trial network in TNLCM. Command: {deploy_trial_network}. Error received: {stderr}. Return code: {rc}",
            )
        msg(
            level="info",
            message=f"Trial network {trial_network_id} deployed successfully in TNLCM",
        )

    msg(level="info", message="Toolkit installation process completed successfully")

except KeyboardInterrupt:
    print("Operation interrupted by user")
    exit(1)

except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)
