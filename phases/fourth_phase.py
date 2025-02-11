import os

from ruamel.yaml.scalarstring import DoubleQuotedScalarString

from phases.utils.cli import run_command
from phases.utils.file import load_yaml, save_file, get_env_var
from phases.utils.git import git_branch, git_branches, git_switch, git_add, git_commit, git_push
from phases.utils.interactive import ask_text, ask_confirm
from phases.utils.logs import msg
from phases.utils.one import get_onegate_endpoint
from phases.utils.parser import ansible_encrypt, object_to_yaml
from phases.utils.temp import save_temp_directory, temp_path

def _create_site(sites_path: str) -> str:
    """
    Create a new site
    
    :param sites_path: the path to the sites repository, ``str``
    :return: the name of the site, ``str``
    """
    def validate_site(site: str) -> bool | str:
        """
        Validate if the site name does not already exist.
        
        :param site: the name of the site, ``str``
        :return: True if valid, or an error message if invalid, ``bool | str``
        """
        if site in sites:
            return f"Site {site} already exists, please enter a new name."
        return True

    msg("info", "Creating a new site")
    sites = git_branches(sites_path)
    site = ask_text(prompt="Enter the name of the site:", default="", validate=validate_site)
    msg("info", f"New site: {site}")
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
                f"Enter the value of '{key}':",
                default=value
            )
            updated_data[key] = new_value
        elif isinstance(value, list):
            new_value = ask_text(
                f"Enter the value of '{key}' separated by commas. For example: 0, 1, 2:",
                default=str(value),
                validate=True
            )
            updated_data[key] = [int(item.strip()) for item in new_value.split(",")]
        elif isinstance(value, int):
            new_value = ask_text(
                f"Enter the value of '{key}':",
                default=str(value),
                validate=True
            )
            updated_data[key] = int(new_value)
        elif isinstance(value, str):
            if key == "site_onegate":
                onegate_endpoint = get_onegate_endpoint()
                updated_data[key] = DoubleQuotedScalarString(onegate_endpoint)
            else:
                new_value = ask_text(
                    f"Enter the value of '{key}':",
                    default=str(value),
                    validate=True
                )
                updated_data[key] = DoubleQuotedScalarString(new_value)
        else:
            updated_data[key] = value
    return updated_data

def fourth_phase(sites_token: str) -> str:
    msg("info", "FOURTH PHASE")
    sites_directory = get_env_var("SITES_DIRECTORY")
    sites_path = temp_path(sites_directory)
    site = _create_site(sites_path)
    git_branch(sites_path, site)
    git_switch(sites_path, branch=site)
    site_path = save_temp_directory(os.path.join(sites_path, site))
    dummy_core_path = temp_path(os.path.join(sites_directory, ".dummy_site", "core.yaml"))
    site_core_path = os.path.join(site_path, "core.yaml")
    run_command(f"cp {dummy_core_path} {site_core_path}")
    site_core = load_yaml(site_core_path, mode="rt", encoding="utf-8")
    current_config = _update_site_config(site_core)
    current_config_yaml = object_to_yaml(current_config)
    encrypted_data = ansible_encrypt(current_config_yaml, sites_token)
    save_file(encrypted_data, site_core_path, mode="wb", encoding=None)
    dummy_path = temp_path(os.path.join(sites_directory, ".dummy_site"))
    readme_path = temp_path(os.path.join(sites_directory, "README.md"))
    github_path = temp_path(os.path.join(sites_directory, ".github"))
    run_command(f"rm -r {dummy_path}")
    run_command(f"rm {readme_path}")
    run_command(f"rm -r {github_path}")
    git_add(sites_path)
    git_commit(sites_path, f"Add new site {site}")
    git_push(sites_path, site)
    return site