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
import pandas as pd
import math

class PostProcessing:
    def __init__(self,root_path,experiment_name,test): # add in the rootpath here
	# Have the class initialization create and load the .json file as a dictionary?
            self.root_path = root_path
            self.experiment_name = experiment_name
            self.test = test
	
    def curate_deposition(self): 
        global loaded_data # Want to have the variable outside of the function
        
        # import in the empty pickle file that already exists
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'rb') as file:
            loaded_data = pickle.load(file)

            
        # OCV
        df = pd.read_csv(f'{self.root_path}{self.test}_ch1_OCV_1.csv', header = 14) 
        ocv_data = {}
        for column in df.columns:
            ocv_data[column] = df[column].to_list()
            loaded_data[f'{self.experiment_name}'][f'{self.test}']['Depo']['OCV'] = ocv_data
        
        
        # PEIS
        df = pd.read_csv(f'{self.root_path}{self.test}_ch1_PEIS_2.csv', header = 29) 
        peis_data = {}
        for column in df.columns:
            peis_data[column] = df[column].to_list()
            loaded_data[f'{self.experiment_name}'][f'{self.test}']['Depo']['PEIS'] = peis_data

        # Get the iR value from the initial PEIS scan
        data_iR = loaded_data[f'{self.experiment_name}'][f'{self.test}']['Depo']['PEIS']
        index = [abs(i) for i in data_iR['Phase_zwe']].index(min((abs(i)) for i in data_iR['Phase_zwe']))
        E_phase0 = np.array(data_iR['Ewe_bar(V)'][index])
        I_phase0 = np.array(data_iR['I_bar(A)'][index])
        iR = E_phase0/I_phase0
        print(f'iR for deposition = {iR} ohms')
        loaded_data[f'{self.experiment_name}'][f'{self.test}']['Depo']['PEIS']['iR(ohm)'] = iR
        

        # CA
        df = pd.read_csv(f'{self.root_path}{self.test}_ch1_CA_3.csv', header = 19) 
        ca_data = {}
        for column in df.columns:
            ca_data[column] = df[column].to_list()
            loaded_data[f'{self.experiment_name}'][f'{self.test}']['Depo']['CA'] = ca_data
        # Add a ['Ewe(V)_corrected'] to take into account iR correction
        loaded_data[f'{self.experiment_name}'][f'{self.test}']['Depo']['CA']['Ewe(V)_corrected'] = ca_data['Ewe(V)']-(np.array(ca_data['I(A)'])*iR)
       
        # Save the pickle file
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as file:
            pickle.dump(loaded_data, file)
        
        #return loaded_data

    def curate_characterization(self):
        global loaded_data # Want to have the variable outside of the function
        # import in the empty pickle file that already exists
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'rb') as file:
            loaded_data = pickle.load(file)

        # Import each excel file and put all the data into the dictionary
        df = pd.read_csv(f'{self.root_path}{self.test}_ch2_OCV_1.csv', header = 14) #REPLACE WITH ACTUAL TEST NAME

        ocv_data = {}
        for column in df.columns:
            ocv_data[column] = df[column].to_list()
            loaded_data[f'{self.experiment_name}'][f'{self.test}']['Depo']['OCV'] = ocv_data

        # Curate the PEIS data
        for i in [2,10]:
            df = pd.read_csv(f'{self.root_path}{self.test}_ch2_PEIS_{i}.csv', header = 29) #REPLACE WITH ACTUAL TEST NAME
            peis_data = {}
            for column in df.columns:
                peis_data[column] = df[column].to_list()
                loaded_data[f'{self.experiment_name}'][f'{self.test}']['Char'][f'PEIS_{i}'] = peis_data

        # Curate the CV data
        for i in [3,4,5,6,7,8,9]:
            df = pd.read_csv(f'{self.root_path}{self.test}_ch2_CV_{i}.csv', header = 22) #REPLACE WITH ACTUAL TEST NAME
            cv_data = {}
            for column in df.columns:
                cv_data[column] = df[column].to_list()
                loaded_data[f'{self.experiment_name}'][f'{self.test}']['Char'][f'CV_{i}'] = cv_data
       
        # Save the pickle file
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as file:
            pickle.dump(loaded_data, file)
        
        #return loaded_data
    
    # Proxy performance using CO2R current
    def curate_performance_proxy(self):
        global loaded_data # Want to have the variable outside of the function
        # import in the empty pickle file that already exists
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'rb') as file:
            loaded_data = pickle.load(file)

        df = pd.read_csv(f'{self.root_path}{self.test}_ch2_CA_11.csv', header = 19)

        ca_data = {}
        for column in df.columns:
            ca_data[column] = df[column].to_list()
            loaded_data[f'{self.experiment_name}'][f'{self.test}']['Char']['CA'] = ca_data

        # Plot the data
        x = loaded_data[f'{self.experiment_name}'][f'{self.test}']['Char']['CA']['t(s)']
        y = loaded_data[f'{self.experiment_name}'][f'{self.test}']['Char']['CA']['I(A)']
        plt.plot(x,y)
        plt.ylabel('Current (A)')
        plt.xlabel('Time (s)')
        plt.title(f'CO2R Profile {self.test}')
        plt.savefig(f'{self.root_path}CO2R_Current_{self.test}.jpeg', dpi = 300)
        plt.show()

        # Save the pickle file
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as file:
            pickle.dump(loaded_data, file)

    def curate_performance(self):
        pass
    
    def determine_mass_loading(self, truncate_time):
        global loaded_data
        
        # Entire deposition
        x_all = loaded_data[f'{self.experiment_name}'][f'{self.test}']['Depo']['CA']['t(s)']
        y_all = np.abs(loaded_data[f'{self.experiment_name}'][f'{self.test}']['Depo']['CA']['I(A)'])
        area_all = np.trapz(y_all, x_all)
        print(f'Mass Loading All = {area_all}')

        # Time truncated deposition
        filter = np.where(np.array(loaded_data[f'{self.experiment_name}'][f'{self.test}']['Depo']['CA']['t(s)']) > truncate_time)
        x_trunc = np.array(loaded_data[f'{self.experiment_name}'][f'{self.test}']['Depo']['CA']['t(s)'])[filter]
        y_trunc = np.array(np.abs(loaded_data[f'{self.experiment_name}'][f'{self.test}']['Depo']['CA']['I(A)']))[filter]
        area_trunc = np.trapz(y_trunc, x_trunc)
        print(f'Mass Loading Truncated ({truncate_time} s) = {area_trunc}')

        #plot the data
        plt.plot(x_all,y_all)
        plt.fill_between(x_all, y_all, color='skyblue', alpha=0.5)
        plt.axhline(0, color='red', linestyle='--')
        plt.axvline(0, color='red', linestyle='--')
        plt.legend()
        plt.ylabel('Current (A)')
        plt.xlabel('Time (s)')
        plt.title(f'Deposition Profile {self.test}')
        plt.savefig(f'{self.root_path}Deposition_{self.test}.jpeg', dpi = 300)
        plt.show()
        
        #Put the data into the data archive
        loaded_data[f'{self.experiment_name}'][f'{self.test}']['Metric']['Loading'] = {'mass_total':area_all,'mass_trunc':area_trunc,'trunc_time':truncate_time}

        # Save the pickle file
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as file:
            pickle.dump(loaded_data, file)
        
        #return loaded_data
    
    def determine_ESCA(self):
        global loaded_data # Want to have the variable outside of the function
        
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'rb') as file:
            loaded_data = pickle.load(file)
        
        # define the scan_rate and make other dummy variables to be updated
        # scan_rate = np.array([0.025,0.05,0.075,0.100,0.125,.150])
        scan_rate = np.array([0.025,0.05,0.100,0.125,.150])
        ESCA_current_positive = np.zeros(len(scan_rate))
        ESCA_current_negative = np.zeros(len(scan_rate))
        ESCA_current_positive_baseline = np.zeros(len(scan_rate))
        ESCA_current_negative_baseline = np.zeros(len(scan_rate))
        ESCA_current_positive_std = np.zeros(len(scan_rate))
        ESCA_current_negative_std = np.zeros(len(scan_rate))

        #for i,j in enumerate([4,5,6,7,8,9]): # This can be adjusted based no the number of scan_rates used, note did not use the first CV
        for i,j in enumerate([4,5,7,8,9]): # This can be adjusted based no the number of scan_rates used, note did not use the first CV
            Ewe_array = np.array(loaded_data[f'{self.experiment_name}'][f'{self.test}']['Char'][f'CV_{j}']['Ewe(V)'])
            current_array = np.array(loaded_data[f'{self.experiment_name}'][f'{self.test}']['Char'][f'CV_{j}']['I(A)'])
            cycle_array = np.array(loaded_data[f'{self.experiment_name}'][f'{self.test}']['Char'][f'CV_{j}']['Cycle'])

            # Find the indices for where Ewe ~-0.1V, noting the threshold value used to find something 'close enough'
            target_value = -0.1
            threshold = 0.005
            indices = np.where(np.abs(Ewe_array - target_value) <= threshold)[0]

            # if there are indices value this will not be empty
            # grab associated values from the other arrays
            if indices.size > 0:
                current_values = current_array[indices]
                cycle_values = cycle_array[indices]
            else:
                print('error: no Ewe(V) = -0.1 V values were found') #TODO write this as an error

            # Split the values into anodic and cathodic current values
            ESCA_current_positive[i] = np.mean(current_values[current_values > 0])
            print(ESCA_current_positive[i])
            if  math.isnan(ESCA_current_positive[i]) == True:
                ESCA_current_positive[i] = 0
            else:
                pass
                
            ESCA_current_negative[i] = np.mean(current_values[current_values < 0]) 
            print(ESCA_current_negative[i])
            if  math.isnan(ESCA_current_negative[i]) == True:
                ESCA_current_negative[i] = 0
            else:
                pass
                
            ESCA_current_positive_std[i] = np.std(current_values[current_values > 0]) 
            ESCA_current_negative_std[i] = np.std(current_values[current_values < 0])
            
            # to eliminate charging effects and to zero the CV curves at the y-axis = 0, the following adjustments are made:
            baseline = (ESCA_current_positive[i] + ESCA_current_negative[i])/2 # determine the middle point between the two
            ESCA_current_positive_baseline[i] = ESCA_current_positive[i]-baseline # offset to zero positive numbers
            ESCA_current_negative_baseline[i] = ESCA_current_negative[i]-baseline # offset to zero negative numbers
            
            #store each iteration as a plot:
            plt.plot(Ewe_array,current_array,label = scan_rate[i])


        print(ESCA_current_positive_baseline)
        print(ESCA_current_negative_baseline)
        #plot the individual cycling data
        plt.legend()
        plt.ylabel('Current (A)')
        plt.xlabel('Ewe (V)')
        plt.title(f'ESCA Individual Cycles {self.test}')
        plt.savefig(f'{self.root_path}ESCA_Cycling_Data_{self.test}.jpeg',dpi = 300)
        plt.show()
        
        #linear fit
        ESCA_positive, intercept_positive = np.polyfit(scan_rate,ESCA_current_positive_baseline,1)
        ESCA_negative, intercept_negative = np.polyfit(scan_rate,-ESCA_current_negative_baseline,1) #make the current values positive
        print(f'ECSA positive = {ESCA_positive} F')
        print(f'ECSA negative = {ESCA_negative} F')
        
        
        #plot the ESCA data
        plt.scatter(scan_rate,ESCA_current_positive_baseline,label = 'positive I')
        plt.scatter(scan_rate,ESCA_current_negative_baseline,label = 'negative I')
        plt.plot(scan_rate,ESCA_positive*scan_rate + intercept_positive)
        plt.plot(scan_rate,ESCA_negative*scan_rate + intercept_negative)
        plt.xlabel('Scan Rate (V/s)')
        plt.ylabel('Current (A)')
        plt.title(f'ESCA Fit {self.test}')
        plt.savefig(f'{self.root_path}ESCA_{self.test}.jpeg',dpi = 300)
        plt.show()
        
        # Store the values as metric values in the .json file
        loaded_data[f'{self.experiment_name}'][f'{self.test}']['Metric']['ECSA'] = {'scan_rate':scan_rate,'I(A)':[ESCA_current_positive,ESCA_current_negative,ESCA_current_positive_std,ESCA_current_negative_std,ESCA_current_positive_baseline,ESCA_current_negative_baseline],'ESCA(F)':{'ESCA_positive':ESCA_positive,'ESCA_negative':ESCA_negative,
                                                                                                                    'intercept_positive':intercept_positive,'intercept_negative':intercept_negative}}
        
        # Save the pickle file
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as file:
            pickle.dump(loaded_data, file)
        
        #return loaded_data

    def determine_performance_proxy(self):
        global loaded_data # Want to have the variable outside of the function
        
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'rb') as file:
            loaded_data = pickle.load(file)

        # For this proxy experiment, just take the last current value at the end of the experiment. Note the values are negative, so we want them to be positive
        co2r_current = -loaded_data[f'{self.experiment_name}'][f'{self.test}']['Char']['CA']['I(A)'][-1]

        print(f'The current at the end of the run is {co2r_current} A')

        loaded_data[f'{self.experiment_name}'][f'{self.test}']['Metric']['CO_Eff'] = co2r_current 
        # Store the values as metric values in the .json file
        # Save the pickle file
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as file:
            pickle.dump(loaded_data, file)

    def plot_results(self, data):
        # Placeholder for plotting the results of the experiment, should do it and have a window pop-up including saving the
        # .jpeg that is produced for easy looking
        pass

    def experiment_update(self, data, exp_count, X_choice):
        
        # Import files: #TODO UPDATE LOCATION
        with open(f'{self.root_path}master_runs_depo.json','r') as f:
           depo_json = json.load(f)

        with open(f'{self.root_path}master_runs_char.json','r') as f:
           char_json = json.load(f)

        with open(f'{self.root_path}master_runs_perf.json','r') as f:
           perf_json = json.load(f)

        # Update the run status of all
        char_json['Runs'][0]['status'] = 'incomplete'
        perf_json['Runs'][0]['status'] = 'incomplete'
        depo_json['Runs'][0]['status'] = 'incomplete'
        char_json['Runs'][0]['expID'] = exp_count
        perf_json['Runs'][0]['expID'] = exp_count
        depo_json['Runs'][0]['expID'] = exp_count

        # Update the new experimental parameters in depo.json and the pump parameters
        # Assume X_sample matric is set ip as [0] = Au[], [1] = voltage, [2] = time
        # Update the 
        depo_json['Runs'][0]['Techniques'][1]['params']['voltage_step'] = X_choice[1]
        depo_json['Runs'][0]['Techniques'][1]['params']['duration_step'] = X_choice[2]

        #To update the pump. global variable should have it carry-over into the main text:
        # global px
        # px = []
        # px = 50
        #px.append(DispenseProcedure(1,X_choice[0],1,0)) # pumpnum,target_wgt,carouselsink,carouseldump

        # Save the pickle file
        with open(f'{self.root_path}master_runs_depo.json','w') as f:
            json.dump(depo_json, f)
        with open(f'{self.root_path}master_runs_char.json','w') as f:
            json.dump(char_json, f)
        with open(f'{self.root_path}master_runs_perf.json','w') as f:
            json.dump(perf_json, f)
