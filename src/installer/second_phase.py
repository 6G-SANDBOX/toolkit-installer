import os

from src.utils.cli import run_command
from src.utils.file import load_yaml, save_yaml, get_env_var
from src.utils.git import git_branch, git_branches, git_clone, git_switch, git_add, git_commit, git_push
from src.utils.interactive import ask_text, ask_confirm
from src.utils.logs import msg
from src.utils.temp import save_temp_file, save_temp_directory, temp_path

def _create_site(sites_path: str) -> str:
    """
    Create a new site
    
    :param sites_path: the path to the sites repository, ``str``
    :return: the name of the site, ``str``
    """
    site = ask_text(prompt="Enter the name of the site:", default="", validate=True)
    sites = git_branches(sites_path)
    if site in sites:
        site = ask_text(prompt="Site already exists, enter a new name:", default="", validate=True)
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
        elif isinstance(value, bool):
            new_value = ask_confirm(
                f"Current value of '{key}' is '{value}' (or press Enter to use default value):",
                default=value
            )
            updated_data[key] = new_value
        elif isinstance(value, list):
            new_value = ask_text(
                f"Current value of '{key}' is '{value}'. Format the list with commas. For example: 0,1,2 (or press Enter to use default value):",
                default=str(value),
                validate=True
            )
            updated_data[key] = value if new_value == "" else new_value.split(",")
        else:
            new_value = ask_text(
                f"Current value of '{key}' is '{value}' (or press Enter to use default value):",
                default=str(value),
                validate=True
            )
            updated_data[key] = value if new_value == "" else new_value
    return updated_data

def second_phase() -> str:
    msg("info", "SECOND PHASE")
    github_sites_https = get_env_var("GITHUB_SITES_HTTPS")
    sites_directory = get_env_var("SITES_DIRECTORY")
    sites_path = save_temp_directory(sites_directory)
    github_sites_token = ask_text(prompt="Enter the token for the GitHub sites repository:", default="", validate=True)
    github_sites_https = github_sites_https.replace("https://", f"https://{github_sites_token}@")
    git_clone(github_sites_https, sites_path)
    msg("info", f"Repository {sites_directory} cloned successfully")
    site = _create_site(sites_path)
    msg("info", f"Site name: '{site}'")
    git_branch(sites_path, site)
    git_switch(sites_path, site)
    msg("info", f"Site branch '{site}' created successfully in local")
    site_path = save_temp_directory(os.path.join(sites_path, site))
    msg("info", f"Site directory '{site_path}' created successfully")
    dummy_core_path = temp_path(os.path.join("6G-Sandbox-Sites", ".dummy_site", "core.yaml"))
    site_core_path = os.path.join(site_path, "core.yaml")
    run_command(f"cp {dummy_core_path} {site_core_path}")
    msg("info", f"Site structure copied successfully from '{dummy_core_path}' to '{site_core_path}'")
    site_core = load_yaml(site_core_path, mode="rt", encoding="utf-8")
    current_config = _update_site_config(site_core)
    save_yaml(data=current_config, file_path=site_core_path)
    msg("info", f"Site configuration updated successfully")
    sites_token = ask_text(prompt="Enter the token for the site:", default="", validate=True)
    msg("info", f"Token '{sites_token}' generated successfully")
    token_path = save_temp_file(data=sites_token, file_path="sites_token", mode="w", encoding="utf-8")
    msg("info", f"Token saved successfully in '{token_path}'")
    # TODO: use ansible_encrypt in src-utils-parser.py
    run_command(f"ansible-vault encrypt {site_core_path} --vault-password-file {token_path}")
    msg("info", f"File '{site_core_path}' encrypted successfully")
    git_add(sites_path)
    git_commit(sites_path, f"Add site '{site}'")
    git_push(sites_path, site)
    return site_core_path, sites_token