from textwrap import dedent
from time import sleep

from src.zero_phase import check_one_health
from src.utils.dotenv import get_env_var
from src.utils.cli import run_command
from src.utils.file import load_file, loads_json, save_file, save_temp_file
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

def _is_marketplace_ready(marketplace_id: int) -> bool:
    """
    Check if the 6G-SANDBOX marketplace is ready to be used
    
    :param marketplace_id: the ID of the marketplace, ``int``
    :return: whether the marketplace is ready, ``bool``
    """
    res = run_command(f"onemarket show -j {marketplace_id}")
    if res["rc"] != 0:
        msg("error", "Could not show the marketplace")
    marketplace = loads_json(data=res["stdout"])
    return marketplace["MARKETPLACE"]["MARKETPLACEAPPS"]

def _set_marketplace_monitoring_interval(interval: int) -> int:
    """
    Set the monitoring interval of the marketplace
    
    :param interval: the interval in seconds, ``int``
    :return: the old interval value, ``int``
    """
    oned_conf = load_file(file_path="/etc/one/oned.conf", mode="r", encoding="utf-8")
    lines = oned_conf.splitlines()
    old_interval = None
    for i, line in enumerate(lines):
        if line.startswith("MONITORING_INTERVAL_MARKET"):
            old_interval = int(line.split("=")[1].strip())
            lines[i] = f"MARKET_MAD_INTERVAL = {interval}"
            break
    if old_interval is not None:
        oned_conf = "\n".join(lines)
        save_file(data=oned_conf, file_path="/etc/one/oned.conf", mode="w", encoding="utf-8")
        msg("info", f"Market monitoring interval set to interval {interval}")
    return old_interval

def _restart_oned() -> None:
    """
    Restart the OpenNebula daemon
    """
    res = run_command("systemctl restart opennebula")
    if res["rc"] != 0:
        msg("error", "Could not restart the OpenNebula daemon")
    msg("info", "OpenNebula daemon restarted")

def first_phase() -> None:
    marketplace_name = get_env_var("OPENNEBULA_MARKETPLACE_NAME")
    marketplace_endpoint = get_env_var("OPENNEBULA_MARKETPLACE_ENDPOINT")
    marketplace_id = _find_marketplace_id(marketplace_name, marketplace_endpoint)
    if not marketplace_id:
        msg("info", "6G-SANDBOX marketplace not present, adding...")
        marketplace_id = _add_sandbox_marketplace(marketplace_name, marketplace_endpoint)
    
    if not _is_marketplace_ready(marketplace_id):
        msg("info", "The 6G-SANDBOX marketplace is not ready...")
        msg("info", "Forcing fast marketplace monitoring...")
        new_interval = 10
        old_interval = _set_marketplace_monitoring_interval(interval=new_interval)
        if old_interval != new_interval:
            _restart_oned()
            sleep(new_interval)
            check_one_health()
            sleep(15)
            _ = _set_marketplace_monitoring_interval(interval=old_interval)
            _restart_oned()
            sleep(10)
            check_one_health()