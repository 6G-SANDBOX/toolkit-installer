from src.zero_phase import zero_phase
from src.first_phase import first_phase
from src.second_phase import second_phase
from src.third_phase import third_phase
from src.fourth_phase import fourth_phase
from src.fifth_phase import fifth_phase

try:
    # PHASE 0
    zero_phase()
    
    # PHASE 1
    sixg_sandbox_group, jenkins_user = first_phase()
    
    # PHASE 2
    sites_token = second_phase(sixg_sandbox_group, jenkins_user)
    
    # PHASE 3
    site = third_phase(sites_token)
    
    # PHASE 4
    fourth_phase(sixg_sandbox_group, jenkins_user, site, sites_token)
    
    # PHASE 5
    # fifth_phase(site)

except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)