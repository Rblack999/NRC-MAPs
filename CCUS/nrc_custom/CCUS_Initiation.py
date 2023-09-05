import os
import pickle

class Campaign_Initiation:
    def __init__(self,root_path,experiment_name,test,number_runs,date_format):
    	# Have the class initialization create and load the .json file as a dictionary?
            self.root_path = root_path
            self.experiment_name = experiment_name
            self.test = test
            self.number_runs = number_runs
            self.date_format = date_format
    
    def CCUS_initiation(self):
        data = {}
        data[f'{self.experiment_name}'] = {}

        #Pre populate the dictionary with the general data structure
        for exp_count in range(self.number_runs):
            data[f'{self.experiment_name}'][f'Test_{exp_count}'] = {'Depo':{},'Char':{},'Metric':{},'AL':{}}

        # Create the folder if it doesn't exist based on the date of creation
        root_path = f'C:/Users/Blackr/Documents/CCUS/MAPs/Initiate/{self.date_format}/'

        if not os.path.exists(self.root_path): # Check if folder exists - if not, make it, else use existing folder
            os.makedirs(self.root_path)

        # # Save the initial pickle file
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as f:
                    pickle.dump(data, f)