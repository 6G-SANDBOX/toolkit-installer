from src.installer.zero_phase import zero_phase
from src.installer.first_phase import first_phase
from src.installer.second_phase import second_phase
from src.installer.third_phase import third_phase
from src.installer.fourth_phase import fourth_phase
from src.installer.fifth_phase import fifth_phase

try:
    # PHASE 0
    zero_phase()
    
    # PHASE 1
    sixg_sandbox_group, jenkins_user = first_phase()
    
    # PHASE 2
    site_core_path, sites_token = second_phase()
    
    # PHASE 3
    third_phase(sixg_sandbox_group, jenkins_user, site_core_path, sites_token)
    
    # PHASE 4
    fourth_phase(sixg_sandbox_group, jenkins_user, sites_token)
    
    # PHASE 5
    # fifth_phase()

except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)