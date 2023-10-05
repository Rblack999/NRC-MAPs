'''
General #TODO
Real file to perform an actual campaign for CO2R optimization using the HCells. 
'''
# Import all libraries at once
import csv, json, time
from datetime import date
import pickle
import os
import json
import numpy as np
import math
from nrc_custom.CCUS_Initiation import Campaign_Initiation
from nrc_custom.CCUS_PostProcess import PostProcessing
from nrc_custom.CCUS_Active_Learning_Noise import ActiveLearning
from nrc_custom.CCUS_N9_workflow import N9_Workflow
from scipy.stats import qmc
from north_c9 import NorthC9
from alicat import FlowController
import nest_asyncio
nest_asyncio.apply()

# Initial User Variables
experiment_name = 'awnb1p10061'
root_path = f'C:/Users/whittingha/Desktop/Potentiostat_API/Campaigns/{experiment_name}/'
number_runs = 100 # Input the total number of possible runs 
test = 'Test_0' # Always keep this as is, is a dummy
exp_start = 2 # If a new campaign, this = 0. Else, input the exp_count to continue an existing campaign

# COM PORTS
com_port_Ecell = 'COM10'
depo_flow_controller_com_port = 'COM3'
# combine all com ports into a tuple
com_ports_N9 = (com_port_Ecell,depo_flow_controller_com_port) #....add more as system expands

# Connect to the robot and start the initialization steps to get automation ready

# connect to N9 and instantiate
c9 = NorthC9('A', network_serial='FT2YOSLD')
c9.get_info()

#TODO connect to URe3
#TODO connect to everything else
#depo_flow_controller = FlowController(f'{depo_flow_controller_com_port}')
#TODO put in some check function/unit tests to ensure everything is connected okay?

exp_count = 0
dispense_concentration = 0.0

# Homing of everything and instantiation of necessary objects, used some dummy variables for initiatilizatio purposes
N9_go = N9_Workflow(c9, root_path,experiment_name, exp_count, dispense_concentration, *com_ports_N9)
N9_go.homing_procedure()

# The below starts the campaign, pulling in the correct information from the active learning protocol

# If a new campaign make the associated folder and .pkl file, else pass and start at the previously user specified experiment number
if exp_start == 0:
    # Initiate the campaign
    campaign = Campaign_Initiation(root_path,experiment_name,test,number_runs)
    campaign.CCUS_initiation()
else:
    pass

for exp_count in range(exp_start,number_runs):

    # Update test name and dictionary

    test = f'Test_{exp_count}' # current experiment name - note in the potentiostat.py there is built in protection incase forget to change
    print(f'The following is to be run: {experiment_name} on {test}')

    # Initialize the active learning
    next_experiment = ActiveLearning(root_path, experiment_name, test, exp_count)
    
    # Initialize the experiment_update module
    experiment_update = PostProcessing(root_path, experiment_name, test)

    # Pick the first experiment randomly OR follow what was provided:
    if exp_count == 0:

        #Call in data from previous method to be able to access here:
        next_experiment.determine_first_experiment()
        
        with open(f'{root_path}{experiment_name}_saved_data.pkl', 'rb') as f:
            loaded_data = pickle.load(f)        

        X_choice = list(np.array(loaded_data[f'{experiment_name}'][f'Test_{exp_count}']['AL']['X_sample'][0]))

        print(f'Initial experiment to run: {X_choice}')

        experiment_update.experiment_update(loaded_data, exp_count, X_choice)

        dispense_concentration = float(X_choice[0])

    else: # If this is not the first experiment (ie. you need to continue the campaign after an error)

        #Call in data from previous method to be able to access here:
        with open(f'{root_path}{experiment_name}_saved_data.pkl', 'rb') as f:
            loaded_data = pickle.load(f)

        #TODO: this will need to pull the last value from the previous test_name based on how it is stored, see Test_{i-1}
        X_choice = list(np.array(loaded_data[f'{experiment_name}'][f'Test_{exp_count-1}']['AL']['X_sample'][-1]))

        print(f'Next experiment to run: {X_choice}')

        experiment_update.experiment_update(loaded_data, exp_count, X_choice)

        dispense_concentration = float(X_choice[0])

    while True:

        next_exp = input('Understood what experiment to run next? Type -ok- to continue:')

        if next_exp == 'ok':

            break

##############################################

    print("RUN EXPERIMENT")

    #TODO - input code for automation here

    N9_go = N9_Workflow(c9, root_path,experiment_name,exp_count,dispense_concentration,*com_ports_N9)
    N9_go.auto_deposition()
    N9_go.auto_char()

    print("PROCESS DATA AND UPDATE ASSOCIATED OUTPUT MATRICES WITH NEW DATA")

    # Currently the data used is mock data of old excel files

    process_data = PostProcessing(root_path, experiment_name, test = f'Test_{exp_count}')

    process_data.curate_deposition()

    process_data.determine_mass_loading(truncate_time = 10)

    process_data.curate_characterization()

    process_data.determine_ESCA()

    process_data.curate_performance_proxy()

    process_data.determine_performance_proxy()

##############################################        

    # Run the optimizer

    #next_experiment.determine_next_experiment_random(data) #random for now, to ensure everything works

    next_experiment.determine_next_experiment() # Uncomment when ready to run real optimization

print("Workflow Successful")