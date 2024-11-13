from textwrap import dedent

from src.utils.dotenv import get_env_var
from src.utils.cli import run_command
from src.utils.file import loads_json, save_temp_file
from src.utils.logs import msg

def _find_marketplace_id(marketplace_name: str, marketplace_endpoint: str) -> int:
    """
    Check if the 6G-SANDBOX marketplace is already present in the OpenNebula installation
    
    :param marketplace_name: the name of the marketplace, ``str``
    :param marketplace_endpoint: the endpoint of the marketplace, ``str``
    :return: the ID of the marketplace if it is present, ``int``
    """
    msg("info", "[6G-SANDBOX MARKETPLACE CHECK]")
    res = run_command("onemarket list -j")
    if res["rc"] != 0:
        msg("error", "Could not list the marketplaces")
    marketplaces = loads_json(data=res["stdout"])
    marketplace_id = None
    for marketplace in marketplaces["MARKETPLACE_POOL"]["MARKETPLACE"]:
        if marketplace["NAME"] == marketplace_name and marketplace["TEMPLATE"]["ENDPOINT"] == marketplace_endpoint:
            msg("info", "6G-SANDBOX marketplace already present with ID " + marketplace["ID"])
            marketplace_id = int(marketplace["ID"])
            break
    return marketplace_id

def _add_sandbox_marketplace(marketplace_name: str, marketplace_endpoint: str) -> int:
    """
    Add the 6G-SANDBOX marketplace to the OpenNebula installation
    
    :param marketplace_name: the name of the marketplace, ``str``
    :param marketplace_endpoint: the endpoint of the marketplace, ``str``
    :return: the ID of the marketplace, ``int``
    """
    marketplace_content = dedent(f"""
        NAME = {marketplace_name}
        DESCRIPTION = "6G-SANDBOX Appliance repository"
        ENDPOINT = {marketplace_endpoint}
        MARKET_MAD = one
    """).strip()
    marketplace_template_path = save_temp_file(data=marketplace_content, file_path="marketplace_template", mode="w", encoding="utf-8")
    res = run_command(f"onemarket create {marketplace_template_path}")
    if res["rc"] != 0:
        msg("error", "The 6G-SANDBOX marketplace could not be registered. Please, review the marketplace_template file")
    marketplace_id = res["stdout"].split()[1]
    msg("info", f"6G-SANDBOX marketplace registered successfully with ID {marketplace_id}")
    return int(marketplace_id)

def first_phase() -> None:
    marketplace_name = get_env_var("OPENNEBULA_MARKETPLACE_NAME")
    marketplace_endpoint = get_env_var("OPENNEBULA_MARKETPLACE_ENDPOINT")
    marketplace_id = _find_marketplace_id(marketplace_name, marketplace_endpoint)
    if not marketplace_id:
        msg("info", "6G-SANDBOX marketplace not present, adding...")
        marketplace_id = _add_sandbox_marketplace(marketplace_name, marketplace_endpoint)