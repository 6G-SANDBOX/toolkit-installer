# -*- coding: utf-8 -*-
import questionary
import yaml
import socket
import sys
from functions import *
from time import sleep

BANNER = """

 ██████╗  ██████╗ ███████╗ █████╗ ███╗   ██╗██████╗ ██████╗  ██████╗ ██╗  ██╗
██╔════╝ ██╔════╝ ██╔════╝██╔══██╗████╗  ██║██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝
███████╗ ██║  ███╗███████╗███████║██╔██╗ ██║██║  ██║██████╔╝██║   ██║ ╚███╔╝
██╔═══██╗██║   ██║╚════██║██╔══██║██║╚██╗██║██║  ██║██╔══██╗██║   ██║ ██╔██╗
╚██████╔╝╚██████╔╝███████║██║  ██║██║ ╚████║██████╔╝██████╔╝╚██████╔╝██╔╝ ██╗
 ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝
          ████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗██╗████████╗                      
          ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝██║╚══██╔══╝                      
             ██║   ██║   ██║██║   ██║██║     █████╔╝ ██║   ██║                         
             ██║   ██║   ██║██║   ██║██║     ██╔═██╗ ██║   ██║                         
             ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗██║   ██║                         
             ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝                         

"""
'''
 force_fast_market_monitoring => Defines whether maket monitoring should be forced. If True, oned will be restarted. If false, market monitoring will take by default 600s.
 Please, set to false if the script is being used in critical environments where restarting oned could represent a risk.
'''
force_fast_market_monitoring = True



def main():
    check_user()
    check_one_health()

    # PHASE 1
    # Marketplace registering

    ID = find_sandbox_marketplace()
    if ID == False:
        msg("info", "6GSANDBOX marketplace not present, adding...")
        ID = add_sandbox_marketplace()

    if marketapps_ready(ID) == False:
    # Appliance list refresh
        msg("info", "Marketplace not ready...")
        if force_fast_market_monitoring:
            # Forcing fast marketplace monitoring
            msg("info", "Forcing fast marketplace monitoring...")
            old_value = set_market_monitoring_interval(10)
            if old_value != 10:
                restart_oned()
                sleep(15)
                set_market_monitoring_interval(old_value)
                restart_oned()
        else:
            msg("info", "Waiting 600s for maketplace monitoring...")
            sleep(605)
    else:
        msg("info", "Marketplace ready.")

    # PHASE 2 AND 2.1
    # Appliance downloading and instantiation
    download_appliance_guided("ubuntu")
    download_appliance_guided("service oneke")
    # Lacking 6GSandbox Core SVC downloading and instantiation


    # PHASE 3
    # Scan 6G-SANDBOX/6G-Library repo looking for appliance URLs
    appliance_urls = extract_appliance_values("6G-SANDBOX/6G-Library")
    # Match those appliance URLs to APPs in the Sandbox Marketplace
    matching_apps = match_appliance_urls(appliance_urls)
    msg("info", "Available appliances for download:")
    for app in matching_apps:
        print("[  ID: " + app["ID"] + "  |  Name: " + app["NAME"] + "  ]")




if __name__ == "__main__":
    main()

