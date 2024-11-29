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
    sixg_sandbox_group_id, jenkins_user_id = first_phase()
    
    # PHASE 2
    site_core_path, token_path = second_phase()
    
    # PHASE 3
    third_phase(sixg_sandbox_group_id, jenkins_user_id, site_core_path, token_path)
    
    # PHASE 4
    # fourth_phase()
    
    # PHASE 5
    # fifth_phase()

except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)