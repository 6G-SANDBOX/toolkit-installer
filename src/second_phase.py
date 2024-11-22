from time import sleep

from src.utils.dotenv import get_env_var
from src.utils.logs import msg
from src.utils.one import get_onemarket, add_marketplace, get_marketplace_monitoring_interval, update_marketplace_monitoring_interval, restart_one, check_one_health

def second_phase() -> None:
    msg("info", "SECOND PHASE")
    marketplace_name = get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_NAME")
    marketplace_description = get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_DESCRIPTION")
    marketplace_endpoint = get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_ENDPOINT")
    marketplace = get_onemarket(marketplace_name=marketplace_name)
    if not marketplace:
        msg("info", f"Marketplace {marketplace_name} not present, adding...")
        _ = add_marketplace(marketplace_name, marketplace_description, marketplace_endpoint)
        force_fast_marketplace_monitoring = get_env_var("FORCE_FAST_MARKETPLACE_MONITORING")
        if force_fast_marketplace_monitoring == "false":
            msg("info", "Please, wait 600s for the marketplace to be ready...")
            sleep(600)
        else:
            msg("info", "Forcing fast marketplace monitoring...")
            marketplace_interval = get_env_var("OPENNEBULA_SANDBOX_MARKETPLACE_INTERVAL")
            old_interval = get_marketplace_monitoring_interval()
            update_marketplace_monitoring_interval(interval=marketplace_interval)
            restart_one()
            sleep(marketplace_interval)
            check_one_health()
            update_marketplace_monitoring_interval(interval=old_interval)
            restart_one()
            check_one_health()
    else:
        msg("info", f"Marketplace {marketplace_name} already present")