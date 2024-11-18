import os

from src.utils.cli import run_command
from src.utils.dotenv import get_env_var
from src.utils.file import load_yaml, save_yaml
from src.utils.git import git_branches, git_clone, git_switch, git_add, git_commit, git_push
from src.utils.interactive import ask_text, ask_confirm
from src.utils.logs import msg
from src.utils.temp import save_temp_file, save_temp_directory, temp_path

def _create_site(sites_path: str) -> str:
    """
    Create a new site
    
    :param sites_path: the path to the sites repository, ``str``
    :return: the name of the site, ``str``
    """
    site = ask_text("Enter the name of the site:")
    sites = git_branches(sites_path)
    while True:
        if site in sites:
            site = ask_text("Site already exists, enter a new name:")
        else:
            break
    return site

def _update_site_config(site_core: str) -> dict:
    """
    Update the site configuration file

    :param site_core: the path to the site, ``str``
    :return: the updated site configuration, ``dict``
    """
    updated_data = {}
    for key, value in site_core.items():
        if isinstance(value, dict):
            print(f"\nUpdating nested fields in '{key}':")
            updated_data[key] = _update_site_config(value)
        else:
            new_value = ask_text(
                f"Current value of '{key}' is '{value}' (or press Enter to use default value):",
                default=str(value)
            )
            updated_data[key] = value if new_value == "" else new_value
    
    add_fields = ask_confirm("Do you want to add new components?", default=False)
    if add_fields:
        while True:
            new_key = ask_text("Enter the name of the new field (or press Enter to stop):")
            if not new_key:
                break
            new_value = ask_text(f"Enter the value for '{new_key}':")
            if new_key in updated_data:
                msg("error", f"Field '{new_key}' already exists")
            updated_data[new_key] = new_value
    return updated_data

def first_phase() -> None:
    """
    The first phase of the 6G-SANDBOX installation
    """
    github_sites_https = get_env_var("GITHUB_SITES_HTTPS")
    sites_path = save_temp_directory("6G-Sandbox-Sites")
    git_clone(github_sites_https, sites_path)
    msg("Repository 6G-Sandbox-Sites cloned successfully")
    site = _create_site(sites_path)
    msg(f"Site name: '{site}'")
    git_switch(sites_path, site)
    msg(f"Site branch '{site}' created successfully in local")
    site_path = save_temp_directory(site)
    msg(f"Site directory '{site_path}' created successfully")
    dummy_core_path = temp_path(os.path.join("6G-Sandbox-Sites", ".dummy_site", "core.yaml"))
    site_core_path = os.path.join(site_path, "core.yaml")
    run_command(f"cp {dummy_core_path} {site_core_path}")
    msg(f"Site structure copied successfully from '{dummy_core_path}' to '{site_core_path}'")
    site_core = load_yaml(site_core_path)
    site_config = _update_site_config(site_core)
    save_yaml(site_core_path, site_config)
    msg(f"Site configuration updated successfully")
    sites_token = ask_text("Enter the token for the site:")
    msg(f"Token '{sites_token}' generated successfully")
    token_path = save_temp_file(data=sites_token, file_path="sites_token.txt", mode="w", encoding="utf-8")
    msg(f"Token saved successfully in '{token_path}'")
    run_command(f"ansible-vault encrypt {site_core_path} --vault-password-file {token_path}")
    msg(f"File '{site_core_path}' encrypted successfully")
    git_add(sites_path, ".")
    git_commit(sites_path, f"Add site '{site}'")
    git_push(sites_path, site)