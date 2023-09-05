# Import all libraries at once
import csv, json, time
from datetime import date
import pickle
import os
import json
import numpy as np
from nrc_custom.CCUS_Initiation import Campaign_Initiation
from nrc_custom.CCUS_PostProcess import PostProcessing
from nrc_custom.CCUS_Active_Learning_Noise import ActiveLearning
from scipy.stats import qmc

# Initial User Variables
#date_format = date.today().strftime("%Y_%m_%d")
date_format = '2023_09_10'
root_path = f'C:/Users/Blackr/Documents/CCUS/MAPs/Initiate/{date_format}/'
experiment_name = 'rbnb3p1048'
number_runs = 50
test = 'Test_2'

# Initiate the campaign
campaign = Campaign_Initiation(root_path,experiment_name,test,number_runs,date_format)
campaign.CCUS_initiation()

# The below starts the campaign, pulling in the correct information from the active learning protocol

# Important to define the test number that is to be run. exp_start = 0 indicated a new campaign.
exp_start = 0

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
        with open(f'{root_path}{experiment_name}_saved_data.pkl', 'rb') as f:
            data = pickle.load(f)        
            
        next_experiment.determine_first_experiment(data)
        
        X_choice = list(np.array(data[f'{experiment_name}'][f'Test_{exp_count}']['AL']['X_sample'][0]))
        print(f'Initial experiment to run: {X_choice}')
        
        experiment_update.experiment_update(data, exp_count, X_choice)
        px = X_choice[0]
        
    else: # If this is not the first experiment (ie. you need to continue the campaign after an error)
        
        #Call in data from previous method to be able to access here:
        with open(f'{root_path}{experiment_name}_saved_data.pkl', 'rb') as f:
            data = pickle.load(f)

        #TODO: this will need to pull the last value from the previous test_name based on how it is stored, see Test_{i-1}
        X_choice = list(np.array(data[f'{experiment_name}'][f'Test_{exp_count-1}']['AL']['X_sample'][-1]))
        
        print(f'Next experiment to run: {X_choice}')
        
        experiment_update.experiment_update(data, exp_count, X_choice)
        px = X_choice[0]

    while True:
        next_exp = input('Understood what experiment to run next? Type -ok- to continue:')
        if next_exp == 'ok':
            break
##############################################

    print("RUN EXPERIMENT")
    #Todo - input code for automation here
    
    print("PROCESS DATA AND UPDATE ASSOCIATED OUTPUT MATRICES WITH NEW DATA")
    # Currently the data used is mock data of old excel files
    
    process_data = PostProcessing(root_path, experiment_name, test = f'Test_{exp_count}')
    
    process_data.curate_deposition()
    process_data.determine_mass_loading(truncate_time = 10)
    process_data.curate_characterization()
    process_data.determine_ESCA()
    
##############################################        
    
    # Run the optimizer
    next_experiment.determine_next_experiment_random(data) #random for now, to ensure everything works