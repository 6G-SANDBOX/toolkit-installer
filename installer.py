from phases.zero_phase import zero_phase
from phases.first_phase import first_phase
from phases.second_phase import second_phase
from phases.third_phase import third_phase
from phases.fourth_phase import fourth_phase
from phases.fifth_phase import fifth_phase

try:
    # PHASE 0
    zero_phase()
    
    # PHASE 1
    sixg_sandbox_group, jenkins_user = first_phase()
    
    # PHASE 2
    sites_token, vm_tnlcm_name = second_phase(sixg_sandbox_group, jenkins_user)
    
    # PHASE 3
    third_phase(sixg_sandbox_group, jenkins_user)
    
    # PHASE 4
    # site = fourth_phase(sixg_sandbox_group, jenkins_user, sites_token)
    
    # PHASE 5
    # fifth_phase(site, vm_tnlcm_name)

except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)