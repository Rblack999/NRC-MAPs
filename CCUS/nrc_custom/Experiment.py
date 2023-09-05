'''
In progress, not yet implemented - RB Jan 2,2022
'''

import sys, string, os
import json, csv, io
import numpy as np
import pprint as pp
import os.path
import time
from Potentiostat import Technique

class Experiment(Technique):

    super().__init__(root_path,test_name,directory,channel = 0)

        # self.root_path = root_path
        # self.experiment_name = experiment_name
        # self.test = test
        # self.channel = channel

    #---------------Define electrochemical experiments-----------
    def run_electrodeposition(self):#,root_path,experiment_name,test,channel = 0):
        test_name = f'{self.experiment_name}_{self.test}_Depo' #Ensure different than characterization test
        # Below is the directory for accessing USB0 biologic (aka biologic 1)
        directory = 'C:/Users/Blackr/Documents/EC-Lab Development Package_Copy5/Examples/C-C++/VisualStudio/MFCStaticLink/output/'
        experiment = Technique(self.root_path,test_name,directory,self.channel)
        
        # Step 1 - OCV for initial stabilization
        experiment.ocv(
            root_path,
            test_name,
            rest_time_T = 30)

         # Step 2 - CA for electrodeposition
        experiment.ca(
            root_path,
            test_name,
            vs_initial = ['False'],
            voltage_step = [1.9], # 1.8 V vs. Ag/AgCl
            duration_step = [600], # 10 minutes
            I_range = 'KBIO_IRANGE_10mA') # Set to 10 mA incase of overload

        
    def run_characterization(self,root_path,experiment_name,test, channel):
        test_name = f'{experiment_name}_{test}_Char' # Ensure different than deposition test
        # Below is the directory for accessing USB0 biologic (aka biologic 1)
        directory = 'C:/Users/Blackr/Documents/EC-Lab Development Package_Copy5/Examples/C-C++/VisualStudio/MFCStaticLink/output_USB1/'
        experiment = Technique(root_path,test_name,directory,channel)
        
        # Step 1 - OCV for initial stabilization
        experiment.ocv(
            root_path,
            test_name,
            rest_time_T = 300)

        # Step 2 - EIS for polarization resistance - just run a quick one at zero current to get the solution resistance
        experiment.geis(
            root_path,
            test_name,
            vs_initial='False',
            vs_final = 'False',
            initial_current_step = 0, # Zero current!
            final_current_step = 0,
            amplitude = 5E-6,
            frequency_number = 10, # Just a quick scan
            final_frequency= 1,
            initial_frequency= 100E3,
            duration_step = 0, #refers to how long to hold the voltage initially prior to any frequency measurement
            average_n_times = 1)

         #Step 3 - CP for 'aging' - initial step is only for 1 minute to initialize and 'age' the catalyst
        experiment.cp(
            root_path,
            test_name,
            vs_initial = ['False'],
            current_step = [0.7E-3], # 1 mA/cm2
            duration_step = [60]) # 1 minutes

        #Step 4 - GEIS for measurement
        experiment.geis(
            root_path,
            test_name,
            vs_initial='False',
            vs_final = 'False',
            initial_current_step = 0.7E-3, #1 mA/cm2
            final_current_step = 0.7E-3, # Have them match
            amplitude = 70E-6, #10% of current
            frequency_number = 60, # Just a quick scan
            final_frequency= 100E-3, #Hz
            initial_frequency= 100E3, #Hz
            duration_step = 0, #refers to how long to hold the voltage initially prior to any frequency measurement
            average_n_times = 2)

        #Step 5 - CP for 'aging' - initial step is only for 1 minute to initialize and 'age' the catalyst
        experiment.cp(
            root_path,
            test_name,
            vs_initial = ['False'],
            current_step = [0.7E-3], # 1 mA/cm2
            duration_step = [300]) # 5 minutes

        #Step 6 - GEIS for measurement
        experiment.geis(
            root_path,
            test_name,
            vs_initial='False',
            vs_final = 'False',
            initial_current_step = 0.7E-3, #1 mA/cm2
            final_current_step = 0.7E-3, # Have them match
            amplitude = 70E-6, #10% of current
            frequency_number = 60, # Just a quick scan
            final_frequency= 100E-3, #Hz
            initial_frequency= 100E3, #Hz
            duration_step = 0, #refers to how long to hold the voltage initially prior to any frequency measurement
            average_n_times = 2)

        #Step 7 - CP for 'aging' - initial step is only for 1 minute to initialize and 'age' the catalyst
        experiment.cp(
            root_path,
            test_name,
            vs_initial = ['False'],
            current_step = [0.7E-3], # 1 mA/cm2
            duration_step = [300]) # 5 minutes

        #Step 8 - GEIS for measurement
        experiment.geis(
            root_path,
            test_name,
            vs_initial='False',
            vs_final = 'False',
            initial_current_step = 0.7E-3, #1 mA/cm2
            final_current_step = 0.7E-3, # Have them match
            amplitude = 70E-6, #10% of current
            frequency_number = 60, # Just a quick scan
            final_frequency= 100E-3, #Hz
            initial_frequency= 100E3, #Hz
            duration_step = 0, #refers to how long to hold the voltage initially prior to any frequency measurement
            average_n_times = 2)

        #Step 9 - CP for 'aging' - initial step is only for 1 minute to initialize and 'age' the catalyst
        experiment.cp(
            root_path,
            test_name,
            vs_initial = ['False'],
            current_step = [0.7E-3], # 1 mA/cm2
            duration_step = [300]) # 5 minutes

        #Step 10 - GEIS for measurement
        experiment.geis(
            root_path,
            test_name,
            vs_initial='False',
            vs_final = 'False',
            initial_current_step = 0.7E-3, #1 mA/cm2
            final_current_step = 0.7E-3, # Have them match
            amplitude = 70E-6, #10% of current
            frequency_number = 60, # Just a quick scan
            final_frequency= 100E-3, #Hz
            initial_frequency= 100E3, #Hz
            duration_step = 0, #refers to how long to hold the voltage initially prior to any frequency measurement
            average_n_times = 2)

        #Step 11 - CP for 'aging' - initial step is only for 1 minute to initialize and 'age' the catalyst
        experiment.cp(
            root_path,
            test_name,
            vs_initial = ['False'],
            current_step = [0.7E-3], # 1 mA/cm2
            duration_step = [300]) # 5 minutes

        #Step 12 - GEIS for measurement
        experiment.geis(
            root_path,
            test_name,
            vs_initial='False',
            vs_final = 'False',
            initial_current_step = 0.7E-3, #1 mA/cm2
            final_current_step = 0.7E-3, # Have them match
            amplitude = 70E-6, #10% of current
            frequency_number = 60, # Just a quick scan
            final_frequency= 100E-3, #Hz
            initial_frequency= 100E3, #Hz
            duration_step = 0, #refers to how long to hold the voltage initially prior to any frequency measurement
            average_n_times = 2)