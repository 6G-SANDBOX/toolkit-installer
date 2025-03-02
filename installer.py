from utils.file import load_dotenv_file
from utils.questionary import ask_password, ask_select, ask_text
from utils.logs import msg, setup_logger
from utils.one import check_one_health, get_group_id, get_groups_names, get_usernames, get_username_id, get_oneflow_template_custom_attrs, oneacl_create, onegroup_addadmin, onegroup_create, onemarket_create, oneuser_chgrp, oneuser_create, onemarketapp_add
from utils.os import get_dotenv_var
from utils.temp import create_temp_directory

try:

    load_dotenv_file()
    setup_logger()
    msg(level="info", message="Starting toolkit installation process")
    check_one_health()
    create_temp_directory()

    # user
    usernames = get_usernames()
    username = ask_select(
        message="User in OpenNebula is required to manage the trial networks deployed in 6G-SANDBOX. We recommend creating a new user for this purpose. Select an existing OpenNebula username or create a new one",
        choices=["Create new user"] + usernames
    )
    if username == "Create new user":
        username = ask_text(
            message="Introduce new OpenNebula username",
            default="",
            validate=lambda username: (
                "Username must be at least 8 characters long" if len(username) < 8 else
                "Username already exists" if username in usernames else
                True
            )
        )
        password = ask_password(
            message=f"Introduce the password for user {username}",
            validate=lambda password: 
                len(password) < 8 or "Password must be at least 8 characters long"
        )
        username_id = oneuser_create(username=username, password=password)
        msg(level="info", message=f"User {username} created successfully")
    else:
        username_id = get_username_id(username=username)
        msg(level="info", message=f"User {username} already exists")
    
    # group
    groups_names = get_groups_names()
    group_name = ask_select(
        message="Group in OpenNebula is required to manage the trial networks deployed in 6G-SANDBOX. We recommend creating a new group for this purpose. Select an existing OpenNebula group name or create a new one",
        choices=["Create new group"] + groups_names
    )
    if group_name == "Create new group":
        group_name = ask_text(
            message="Introduce new OpenNebula group name",
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
        group_id = get_group_id(group_name=group_name)
        msg(level="info", message=f"Group {group_name} already exists")
    
    # permissions
    oneuser_chgrp(username=username, group_name=group_name)
    onegroup_addadmin(username=username, group_name=group_name)
    oneacl_create(group_id=group_id, resources="CLUSTER+NET/*", rights="USE+MANAGE+ADMIN+CREATE *")

    # marketplaces
    marketplace_monitoring_interval = get_dotenv_var(key="MARKETPLACE_MONITORING_INTERVAL")
    _ = onemarket_create(
        marketplace_name=get_dotenv_var(key="OPENNEBULA_PUBLIC_MARKETPLACE_NAME"),
        marketplace_description=get_dotenv_var(key="OPENNEBULA_PUBLIC_MARKETPLACE_DESCRIPTION"),
        marketplace_endpoint=get_dotenv_var(key="OPENNEBULA_PUBLIC_MARKETPLACE_ENDPOINT"),
        marketplace_monitoring_interval=marketplace_monitoring_interval
    )
    # msg(level="info", message=f"Marketplace {get_dotenv_var(key='OPENNEBULA_PUBLIC_MARKETPLACE_NAME')} created successfully")
    _ = onemarket_create(
        marketplace_name=get_dotenv_var(key="OPENNEBULA_SANDBOX_MARKETPLACE_NAME"),
        marketplace_description=get_dotenv_var(key="OPENNEBULA_SANDBOX_MARKETPLACE_DESCRIPTION"),
        marketplace_endpoint=get_dotenv_var(key="OPENNEBULA_SANDBOX_MARKETPLACE_ENDPOINT"),
        marketplace_monitoring_interval=marketplace_monitoring_interval
    )
    # msg(level="info", message=f"Marketplace {get_dotenv_var(key='OPENNEBULA_SANDBOX_MARKETPLACE_NAME')} created successfully")
    onemarketapp_add(
        group_name=group_name,
        username=username,
        marketplace_name=get_dotenv_var(key="OPENNEBULA_SANDBOX_MARKETPLACE_NAME"),
        appliances=[get_dotenv_var(key="OPENNEBULA_TOOLKIT_SERVICE")]
    )
    # msg(level="info", message=f"Appliance {get_dotenv_var(key='OPENNEBULA_TOOLKIT_SERVICE')} added")
    
    # toolkit service
    custom_attrs = get_oneflow_template_custom_attrs(oneflow_template_name=get_dotenv_var(key="OPENNEBULA_TOOLKIT_SERVICE"))
    # msg(level="info", message="Toolkit installation process completed successfully")

except KeyboardInterrupt:
    print("Operation interrupted by user")
    exit(1)

except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)
