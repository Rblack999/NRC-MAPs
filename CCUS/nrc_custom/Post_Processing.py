'''
RB Created Dec 24, 2021.

Module to post-process the data , organize into a data structure, and gather/use the data for the AI 
'''

import csv, json, time
from datetime import date
#import matplotlib.pyplot as plt
import numpy as np
import pickle
import matplotlib.pyplot as plt

class PostProcessing:
    def __init__(self,root_path,experiment_name,test): # add in the rootpath here
	# Have the class initialization create and load the .json file as a dictionary?
            self.root_path = root_path
            self.experiment_name = experiment_name
            self.test = test
	
    def curate_deposition(self, dict):
	    # Will need to update this based exactly on the electrochemical experiment being run
		# TOADD - reference electrode fix to NHE - want to add inline or as a function?
		
        with open(f'{self.root_path}{self.experiment_name}_{self.test}_Depo_OCV_0_raw.json') as f:
            data = json.load(f)

        dict[f'{self.experiment_name}'][f'{self.test}']['Depo']['OCV'] = data['OCV']

        with open(f'{self.root_path}{self.experiment_name}_{self.test}_Depo_CA_1_raw.json') as f:
            data = json.load(f)

        dict[f'{self.experiment_name}'][f'{self.test}']['Depo']['CA'] = data['CA']

		# Update Ewe for reference electroce correction and to put as vs. NHE
        dict[f'{self.experiment_name}'][f'{self.test}']['Depo']['CA']['Ewe'] = np.array(dict[f'{self.experiment_name}'][f'{self.test}']['Depo']['CA']['Ewe']) + 0.197

        # Save results to pickle file
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as f:
            pickle.dump(dict,f)

    def curate_characterization(self, dict):
		# Will need to update this based exactly on the electrochemical experiment being run
		# TOADD - EIS correct and reference electrode fix - want to add inline or as a function?
		
        with open(f'{self.root_path}{self.experiment_name}_{self.test}_Char_OCV_2_raw.json') as f:
            data = json.load(f)

        dict[f'{self.experiment_name}'][f'{self.test}']['Char']['OCV'] = data['OCV']

		# Do GEIS first so can get iR data
        for i in [3,5,7,9,11,13]:
            with open(f'{self.root_path}{self.experiment_name}_{self.test}_Char_GEIS_{i}_raw.json') as f:
                data = json.load(f)

            dict[f'{self.experiment_name}'][f'{self.test}']['Char'][f'GEIS_{i}'] = data['GEIS']

		# # Get the iR value from the initial GEIS scan, note must be done before CP data is taken
        data_iR = dict[f'{self.experiment_name}'][f'{self.test}']['Char']['GEIS_3']
        index = [abs(i) for i in data_iR['phase_Zwe']].index(min((abs(i)) for i in data_iR['phase_Zwe']))
        E_phase0 = np.array(data_iR['Ewe_bar'][index])
        I_phase0 = np.array(data_iR['I_bar'][index])
        iR = E_phase0/I_phase0
        print(f'iR = {iR}')

        for i in [4,6,8,10,12]:
            with open(f'{self.root_path}{self.experiment_name}_{self.test}_Char_CP_{i}_raw.json') as f:
                data = json.load(f)

            dict[f'{self.experiment_name}'][f'{self.test}']['Char'][f'CP_{i}'] = data['CP']

			# Update for iR and reference electrode correction. Currently set for 5 mA/cm2 characterization current

            dict[f'{self.experiment_name}'][f'{self.test}']['Char'][f'CP_{i}']['Ewe'] = dict[f'{self.experiment_name}'][f'{self.test}']['Char'][f'CP_{i}']['Ewe'] - (3.5E-3*iR) + 0.197

            # Update dict with a new time entry to set time_all = 0 point, mostly for plotting and data extraction purposes
            # Take the initial time start value and subtract all subsequent time_all by it to bring everything to t = 0
            offset = dict[f'{self.experiment_name}'][f'{self.test}']['Char'][f'CP_4']['time_all'][0]
            dict[f'{self.experiment_name}'][f'{self.test}']['Char'][f'CP_{i}']['time_all_offset'] = np.array(dict[f'{self.experiment_name}'][f'{self.test}']['Char'][f'CP_{i}']['time_all'])-offset

		#Save the results in a pickle file
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as f:
            pickle.dump(dict, f)

    def overpotential(self, dict):
        # Pull the last CP data collection and grab the I value at the end
        # Note - this method will not be the same time to grab the point for each sample due to differences in the EIS measurements
        # Take t = 1200 as the fixed point and grab the values from there?
        
        OP_point = dict[f'{self.experiment_name}'][f'{self.test}']['Char']['CP_12']['Ewe'][-1]
        #truncating number to take into account the error in the system
        dict[f'{self.experiment_name}'][f'{self.test}']['Metric']['OP'] = np.round(OP_point, decimals = 3)
        
        # Grab the index for the first time point that rounded t = 1200 # Note the [0][0] is due to the return tuple
        # OP_point_index = np.where(np.round(dict[f'{self.experiment_name}'][f'{self.test}']['Char']['CP_12']['time_all_offset']) == 1200)[0][0]
        # OP_point = dict[f'{self.experiment_name}'][f'{self.test}']['Char']['CP_12']['Ewe'][OP_point_index]
        #dict[f'{self.experiment_name}'][f'{self.test}']['Metric']['OP'] = np.round(OP_point, decimals = 3)
        
        print(dict[f'{self.experiment_name}'][f'{self.test}']['Metric']['OP'])

        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as f:
            pickle.dump(dict, f)

    def eis(self, dict):
		# Placeholder for any analysis on the EIS data that is obtained, will need to install the right analysis library and
        # go back to old EIS file notebooks to implement correctly
        # Currently EIS data is just stored as part of the dictionary
        # Be sure to look at old files on github plus plus files you used for the in-draft publication in order to obtain the 
        # the best algorithms you have developed
        pass

    def plot_results(self, dict):
        # Placeholder for plotting the results of the experiment, should do it and have a window pop-up including saving the
        # .jpeg that is produced for easy looking

        # Deposition
        plt.figure(1)
        plt.scatter(dict[f'{self.experiment_name}'][f'{self.test}']['Depo']['CA']['time'],dict[f'{self.experiment_name}'][f'{self.test}']['Depo']['CA']['I'], )
        plt.ylabel('Deposition Current (A)')
        #plt.ylim(1.3,2.0)            
        plt.xlabel('Time (s)')
        #plt.xlim(0,1750)
        plt.title(f'Deposition for {self.experiment_name}_{self.test}')
        plt.legend()

        plt.savefig(f'{self.root_path}{self.experiment_name}_{self.test}_DepoFigure.png', dpi = 300)
        #plt.show()

        # Characterization - CP
        for i in [4,6,8,10,12]:
            plt.figure(2)
            plt.scatter(dict[f'{self.experiment_name}'][f'{self.test}']['Char'][f'CP_{i}']['time_all_offset'],dict[f'{self.experiment_name}'][f'{self.test}']['Char'][f'CP_{i}']['Ewe'], 
				color = 'black')
            plt.ylabel('Ewe vs. NHE (V)')
            plt.ylim(1.5,2.0)            
            plt.xlabel('Time (s)')
            plt.xlim(0,1750)
            plt.title(f'CP data for {self.experiment_name}_{self.test}')

        plt.savefig(f'{self.root_path}{self.experiment_name}_{self.test}_CPFigure.png', dpi = 300)
        #plt.show()


