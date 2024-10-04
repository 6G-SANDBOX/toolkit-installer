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
    print()
    msg("info", "[6GSANDBOX MARKETPLACE CHECK]")
    print()
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

            # Sets monitoring interval to 10s, restarts OpenNebula, waits 15s and sets the old interval value back
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

    # PHASE 2
    # Appliance downloading and instantiation
    print()
    msg("info", "[REQUIRED APPLIANCES DOWNLOADING]")
    print()
    download_appliance_guided("ubuntu", "VM")
    download_appliance_guided("service oneke", "SERVICE")
    toolkit_service_id = download_appliance_guided("6g-sandbox toolkit", "SERVICE")["SERVICETEMPLATE"]

    # PHASE 2.1
    # 6GSandbox Core SVC instantiation
    print()
    msg("info", "[6GSANDBOX CORE SERVICE INSTANTIATION]")
    print()
    instantiate_sandbox_service(toolkit_service_id)
    #create_jenkins_user()

    # PHASE 3
    # Scan 6G-SANDBOX/6G-Library repo looking for appliance URLs
    print()
    msg("info", "[6GLIBRARY REPO SCANNING]")
    print()
    appliance_urls = extract_appliance_values("6G-SANDBOX/6G-Library")

    # Match repo appliance URLs to APPs in the Sandbox Marketplace
    matching_apps = match_appliance_urls(appliance_urls)

    if matching_apps == []:
        msg("info", "No 6G-Library appliances found in the 6G-SANDBOX marketplace. Please, check if the repo and marketplace appliance URLs match.")
    else:
        # User selects the desired appliances for download
        selected_apps = select_elements(matching_apps, elem_type="appliances", action="download", display_field="NAME")

        # User selects the desired datastore for download
        selected_datastore = select_elements(list_image_datastores(), elem_type="datastore", action="use", display_field="ID", select_single=True)
        print()
        msg("info", "[6GLIBRARY APPLIANCES DOWNLOADING]")
        print()
        # Selected appliances are downloaded
        for app in selected_apps:
            download_appliance(app["NAME"], app["ID"], selected_datastore["ID"])


if __name__ == "__main__":
    main()
