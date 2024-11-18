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
    site = ask_text(prompt="Enter the name of the site (mandatory insert value):", default="")
    sites = git_branches(sites_path)
    while True:
        if site in sites:
            site = ask_text(prompt="Site already exists, enter a new name:", default="")
        elif site == "":
            site = ask_text(prompt="Site name cannot be empty, enter a new name:", default="")
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
        # FIX: differnte cases when is dict, bool and when is list indicate the format with example
        if isinstance(value, dict):
            print(f"\nUpdating nested fields in '{key}':")
            updated_data[key] = _update_site_config(value)
        else:
            new_value = ask_text(
                f"Current value of '{key}' is '{value}' (or press Enter to use default value):",
                default=str(value)
            )
            updated_data[key] = value if new_value == "" else new_value
    return updated_data

def _insert_site_token() -> str:
    """
    Insert the token for the site
    
    :return: the token for the site, ``str``
    """
    site_token = ask_text(prompt="Enter the token for the site (mandatory insert value):", default="")
    if site_token == "":
        while True:
            site_token = ask_text(prompt="Token cannot be empty, enter the token:", default="")
            if site_token != "":
                break
    return site_token

def first_phase() -> None:
    """
    The first phase of the 6G-SANDBOX installation
    """
    github_sites_https = get_env_var("GITHUB_SITES_HTTPS")
    sites_path = save_temp_directory("6G-Sandbox-Sites")
    git_clone(github_sites_https, sites_path)
    msg("info", "Repository 6G-Sandbox-Sites cloned successfully")
    site = _create_site(sites_path)
    msg("info", f"Site name: '{site}'")
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
    # TODO: Implement the case when need add _new_components(current_config)
    save_yaml(data=site_core_path, file_path=current_config)
    msg("info", f"Site configuration updated successfully")
    site_token = _insert_site_token()
    msg("info", f"Token '{site_token}' generated successfully")
    token_path = save_temp_file(data=site_token, file_path="sites_token.txt", mode="w", encoding="utf-8")
    msg("info", f"Token saved successfully in '{token_path}'")
    run_command(f"ansible-vault encrypt {site_core_path} --vault-password-file {token_path}")
    msg("info", f"File '{site_core_path}' encrypted successfully")
    git_add(sites_path, ".")
    git_commit(sites_path, f"Add site '{site}'")
    git_push(sites_path, site)