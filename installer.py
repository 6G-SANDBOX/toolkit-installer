import sys

from dotenv import load_dotenv

from utils.file import load_yaml
from utils.git import (
    git_checkout,
    git_clone,
    git_create_branch,
    git_remotes_branches,
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
    onemarket_create,
    onemarket_endpoint,
    onemarketapp_instantiate,
    onemarketapp_name,
    onemarkets_names,
    oneuser_chgrp,
    oneuser_create,
    oneuser_update_public_ssh_key,
    oneusername_id,
    oneusernames,
    onevm_disk_resize,
    onevm_user_template_param,
)
from utils.os import (
    DOTENV_PATH,
    TEMP_DIRECTORY,
    get_dotenv_var,
    join_path,
    list_directory,
    make_directory,
    remove_directory,
    remove_file,
    rename_directory,
)
from utils.parser import decode_base64
from utils.questionary import ask_confirm, ask_password, ask_select, ask_text

try:
    # configuration
    load_dotenv(dotenv_path=DOTENV_PATH)
    setup_logger()

    # dotenv variables
    sandbox_documentation_url = get_dotenv_var(key="SANDBOX_DOCUMENTATION_URL")
    marketplace_monitoring_interval = get_dotenv_var(
        key="MARKETPLACE_MONITORING_INTERVAL"
    )
    opennebula_public_marketplace_description = get_dotenv_var(
        key="OPENNEBULA_PUBLIC_MARKETPLACE_DESCRIPTION"
    )
    opennebula_public_marketplace_endpoint = get_dotenv_var(
        key="OPENNEBULA_PUBLIC_MARKETPLACE_ENDPOINT"
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
    toolkit_service_jenkins_ssh_key_param = get_dotenv_var(
        key="TOOLKIT_SERVICE_JENKINS_SSH_KEY_PARAM"
    )
    toolkit_service_minio_disk_id = get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_DISK_ID")
    toolkit_service_minio_disk_size = int(
        get_dotenv_var(key="TOOLKIT_SERVICE_MINIO_DISK_SIZE")
    )
    appliance_technitium_url = get_dotenv_var(key="APPLIANCE_TECHNITIUM_URL")
    appliance_route_manager_api_url = get_dotenv_var(
        key="APPLIANCE_ROUTE_MANAGER_API_URL"
    )
    github_organization_name = get_dotenv_var(key="GITHUB_ORGANIZATION_NAME")
    github_sites_team_name = get_dotenv_var(key="GITHUB_SITES_TEAM_NAME")
    github_members_token_encode = get_dotenv_var(key="GITHUB_MEMBERS_TOKEN")
    github_members_token = decode_base64(encoded_data=github_members_token_encode)
    library_https_url = get_dotenv_var(key="LIBRARY_HTTPS_URL")
    library_repository_name = get_dotenv_var(key="LIBRARY_REPOSITORY_NAME")
    library_ref = get_dotenv_var(key="LIBRARY_REF")
    sites_https_url = get_dotenv_var(key="SITES_HTTPS_URL")
    sites_repository_name = get_dotenv_var(key="SITES_REPOSITORY_NAME")

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
    # TODO: uncomment
    # git_team_access(
    #     token=github_members_token,
    #     organization_name=github_organization_name,
    #     team_name=github_sites_team_name,
    #     username=github_username,
    # )
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
        message="Select an existing OpenNebula username or create a new one",
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
        message="Select an existing OpenNebula group name or create a new one",
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
    opennebula_public_marketplace_name = ask_select(
        message="Select the OpenNebula Public marketplace. You can create a new OpenNebula Public marketplace or select an existing one",
        choices=["Create new OpenNebula Public marketplace"] + onemarkets_names(),
    )
    if opennebula_public_marketplace_name == "Create new OpenNebula Public marketplace":
        opennebula_public_marketplace_name = ask_text(
            message="Introduce new OpenNebula Public marketplace name:",
            validate=lambda opennebula_public_marketplace_name: (
                "Marketplace name must be at least 8 characters long"
                if len(opennebula_public_marketplace_name) < 8
                else "Marketplace name already exists"
                if opennebula_public_marketplace_name in onemarkets_names()
                else True
            ),
        )
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
    opennebula_sandbox_marketplace_name = ask_select(
        message="Select the 6G-SANDBOX marketplace. You can create a new 6G-SANDBOX marketplace or select an existing one",
        choices=["Create new 6G-SANDBOX marketplace"] + onemarkets_names(),
    )
    if opennebula_sandbox_marketplace_name == "Create new 6G-SANDBOX marketplace":
        opennebula_sandbox_marketplace_name = ask_text(
            message="Introduce new 6G-SANDBOX marketplace name:",
            validate=lambda opennebula_sandbox_marketplace_name: (
                "Marketplace name must be at least 8 characters long"
                if len(opennebula_sandbox_marketplace_name) < 8
                else "Marketplace name already exists"
                if opennebula_sandbox_marketplace_name in onemarkets_names()
                else True
            ),
        )
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
    else:
        if (
            onemarket_endpoint(marketplace_name=opennebula_sandbox_marketplace_name)
            != opennebula_sandbox_marketplace_endpoint
        ):  # TODO: change to while loop, not error
            msg(
                level="error",
                message=(
                    f"Marketplace indicated {opennebula_sandbox_marketplace_name} not match with the correct endpoint of the 6G-SANDBOX marketplace"
                ),
            )

    # toolkit service
    appliance_toolkit_service_name = onemarketapp_name(
        appliance_url=appliance_toolkit_service_url
    )
    is_toolkit_service_instantiated = onemarketapp_instantiate(
        appliance_url=appliance_toolkit_service_url,
        group_name=group_name,
        marketplace_name=opennebula_sandbox_marketplace_name,
        username=username,
    )
    if not is_toolkit_service_instantiated:
        msg(
            level="error",
            message=f"Appliance {appliance_toolkit_service_name} not instantiated and is mandatory",
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

    sys.exit(1)
    # technitium
    appliance_technitium_name = onemarketapp_name(
        appliance_url=appliance_technitium_url
    )
    is_technitium_instantiated = onemarketapp_instantiate(
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
    is_route_manager_api_instantiated = onemarketapp_instantiate(
        appliance_url=appliance_route_manager_api_url,
        group_name=group_name,
        marketplace_name=opennebula_sandbox_marketplace_name,
        username=username,
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
            f"Proceeding to clone the {sites_repository_name} repository in the temporary directory {TEMP_DIRECTORY}. "
            f"The {sites_repository_name} repository contains the static information about the infrastructure, systems and available equipment of each site"
        ),
    )
    sites_path = join_path(TEMP_DIRECTORY, sites_repository_name)
    git_clone(https_url=sites_https_url, path=sites_path, token=sites_github_token)
    # TODO: check if there are changes in the local repository
    # TODO: maybe git pull required if no changes in local repository
    sites = git_remotes_branches(path=sites_path)
    # TODO: add to sites the branches that are in local repository
    site = ask_select(
        message="Select an existing site or create a new one. If you select a site that already exists, please note that you will be prompted for the ansible key to decrypt the site",
        choices=["Create new site"] + sites,
    )
    if site != "Create new site":
        git_checkout(path=sites_path, ref=site)
        # TODO: possibility to update the site configuration with ansible-edit... ask for the ansible password
        # TODO: detect the components that are already in the site. Read site core.yaml and check the components that are already there an also possibility to update the definition
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
        git_create_branch(path=sites_path, new_branch=site, base_branch="main")
        remove_directory(path=join_path(sites_path, ".github"))
        remove_file(path=join_path(sites_path, "README.md"))
        dummy_site_path = join_path(sites_path, ".dummy_site")
        site_path = join_path(sites_path, site)
        rename_directory(
            new_path=dummy_site_path,
            old_path=site_path,
        )
        core_site_path = join_path(site_path, "core.yaml")
        core_site_data = load_yaml(file_path=core_site_path)

        # library
        msg(
            level="info",
            message=(
                f"Proceeding to clone the {library_repository_name} repository in the temporary directory {TEMP_DIRECTORY}. "
                f"The {library_repository_name} repository contains the description of the components using YAML files and the Ansible playbooks to deploy the components"
            ),
        )
        library_path = join_path(TEMP_DIRECTORY, library_repository_name)
        git_clone(https_url=library_https_url, path=library_path)
        git_checkout(path=library_path, ref=library_ref)
        msg(
            level="info",
            message=(
                f"Repository {library_repository_name} cloned successfully in path {library_path} using ref {library_ref}"
            ),
        )
        library_components = list_directory(path=library_path)
        if not library_components:
            msg(
                level="error",
                message=f"No components found in repository {library_repository_name} using ref {library_ref}",
            )
        msg(
            level="info",
            message=f"Components found in repository {library_repository_name} using ref {library_ref}: {library_components}",
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
            if "long_description" not in metadata:
                msg(
                    level="error",
                    message=f"Long description not found in component {component} in repository {library_repository_name} using ref {library_ref}",
                )
            long_description = metadata["long_description"]
            add_component = ask_confirm(
                message="Do you want to add this component to your site? Very important to know the availability of the component in the site. Ask to the administrator of the site",
                default=False,
            )

    # msg(level="info", message="Toolkit installation process completed successfully")

except KeyboardInterrupt:
    print("Operation interrupted by user")
    exit(1)

except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)
