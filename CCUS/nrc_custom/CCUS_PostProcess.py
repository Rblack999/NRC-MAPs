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
    
    def curate_performance(self):
        
        global loaded_data # Want to have the variable outside of the function
        # import in the empty pickle file that already exists
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'rb') as file:
            loaded_data = pickle.load(file)

        # Put the raw potentiostat data into the .pkl file
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
            ESCA_current_negative[i] = np.mean(current_values[current_values < 0]) 
            ESCA_current_positive_std[i] = np.std(current_values[current_values > 0]) 
            ESCA_current_negative_std[i] = np.std(current_values[current_values < 0])
            
            #store each iteration as a plot:
            plt.plot(Ewe_array,current_array,label = scan_rate[i])

        #plot the individual cycling data
        plt.legend()
        plt.ylabel('Current (A)')
        plt.xlabel('Ewe (V)')
        plt.title(f'ESCA Individual Cycles {self.test}')
        plt.savefig(f'{self.root_path}ESCA_Cycling_Data_{self.test}.jpeg',dpi = 300)
        plt.show()
        
        #linear fit
        ESCA_current_negative = -ESCA_current_negative #want to make the negative values positive
        ESCA_positive, intercept_positive = np.polyfit(scan_rate,ESCA_current_positive,1)
        ESCA_negative, intercept_negative = np.polyfit(scan_rate,ESCA_current_negative,1) #make the current values positive
        print(f'ECSA positive = {ESCA_positive} F')
        print(f'ECSA negative = {ESCA_negative} F')
        
        
        #plot the ESCA data
        plt.scatter(scan_rate,ESCA_current_positive,label = 'positive I')
        plt.scatter(scan_rate,ESCA_current_negative,label = 'negative I')
        plt.plot(scan_rate,ESCA_positive*scan_rate + intercept_positive)
        plt.plot(scan_rate,ESCA_negative*scan_rate + intercept_negative)
        plt.xlabel('Scan Rate (V/s)')
        plt.ylabel('Current (A)')
        plt.title(f'ESCA Fit {self.test}')
        plt.savefig(f'{self.root_path}ESCA_{self.test}.jpeg',dpi = 300)
        plt.show()
        
        # Store the values as metric values in the .json file
        loaded_data[f'{self.experiment_name}'][f'{self.test}']['Metric']['ECSA'] = {'scan_rate':scan_rate,'I(A)':[ESCA_current_positive,ESCA_current_negative,ESCA_current_positive_std,ESCA_current_negative_std],'ESCA(F)':{'ESCA_positive':ESCA_positive,'ESCA_negative':ESCA_negative,
                                                                                                                    'intercept_positive':intercept_positive,'intercept_negative':intercept_negative}}
        
        # Save the pickle file
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as file:
            pickle.dump(loaded_data, file)
        
        #return loaded_data

    def determine_performance(self, data):
        # Update to include he metric for optimization, and ensure it is put into data['Metric']['CO_Eff']
        pass

    def plot_results(self, data):
        # Placeholder for plotting the results of the experiment, should do it and have a window pop-up including saving the
        # .jpeg that is produced for easy looking
        pass

    def experiment_update(self, data, exp_count, X_choice):
        
        # Import files: #TODO UPDATE LOCATION
        with open(f'{self.root_path}master_runs_depo.json','r') as f:
           depo_json = json.load(f)

        with open(f'{self.root_path}master_runs_char1.json','r') as f:
           char1_json = json.load(f)

        with open(f'{self.root_path}master_runs_char2.json','r') as f:
           char2_json = json.load(f)

        # Update the run status of all
        char1_json['Runs'][0]['status'] = 'incomplete'
        char2_json['Runs'][0]['status'] = 'incomplete'
        depo_json['Runs'][0]['status'] = 'incomplete'
        char1_json['Runs'][0]['expID'] = exp_count
        char2_json['Runs'][0]['expID'] = exp_count
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
        with open(f'{self.root_path}master_runs_char1.json','w') as f:
            json.dump(char1_json, f)
        with open(f'{self.root_path}master_runs_char2.json','w') as f:
            json.dump(char2_json, f)






##################################################################

# Seem to have a big problem when putting the dispense class as an external library and 'c9' not being defined. 
# Calling the class here seems fine, but as an external library, run into the problem????
# **********************************************************************************************
# Define statements

CAROUSEL_ROT = 4 # rotary
CAROUSEL_Z = 6 # elevation
# **********************************  FLUID DISPENSATION FUNCTIONS END ****************************************

# **********************************************************************************************
# Class 
class DispenseProcedure:
    # **********************************************************************************************
    # Constructor definition
    def __init__(self,pumpnum,target_wgt,carouselsink,carouseldump):
        
        self.pumpnum = pumpnum # 9
        self.target_wgt = target_wgt
        
        self.carouselsink = carouselsink #3 - Count from 1.  Sink position changes depending on which sink port we want to dispense.
        self.carouseldump = carouseldump #2 - Count from 1.  Dump position does not change 

    # **********************************************************************************************
    # Function definition
    
    # Desc : Reports the settings going into the object made by the Constructor
    def ReportSettings(self):
        print("Object Created : Pump Number {0} is active and Target Weight {1} is requested.".format(self.p1.pumpnum,self.p1.target_wgt))

    # Desc : Moves carousel's axes (rotation and elevation) as defined by incoming variables
    def move_carousel(self, rot_deg, z_mm, vel=None, accel=None):
        #self.rot_deg = rot_deg
        #self.z_mm = z_mm
        #self.vel = vel
        #self.accel = accel
        
        if ((rot_deg > 330) or (z_mm > 160)):
            return
        c9.move_axis(CAROUSEL_Z, 0, vel, accel)
        c9.move_axis(CAROUSEL_ROT, int(rot_deg*(51000/360)), vel, accel)
        c9.move_axis(CAROUSEL_Z, int(z_mm*(40000/160)), vel, accel) # vel = counts/sec, accel = counts/sec2

    # Desc : Obtain stable weight of liquid in vial.  Note - mass balance has to be zeroed first.
    def measure_weight(self):
        c9.clear_scale()
        c9.delay(2) # delay enables any drops travelling down the tube fall into the vial
        st = c9.read_steady_scale()
        print(st)
        index = 0
        weight = 0
        
        c9.delay(2)
        weight = st
            
        print("\nFinal stable weight : ", weight)
        return weight

    # Desc : Rotates carousel port to positioned defined by incoming variable.
    #        Checks should be added to function below and tested to ensure port numbers range between 1 and 7 (i.e. not out of range)
    def set_carousel_port(self, pos):
        # pos represents the position of the carousel dispenser from 1 to 7
        self.move_carousel((pos * 45) + 3, 127) # note : the +3 is for the azimuth offset error.  (max vals are 330.0 and 155)
        
    # Desc : Returns carousel axes positions to its home.
    def home_carousel_axis(self):
        # base - rotary (4)
        # top - up/down aka elevation (6)
        c9.home_axis(4)
        c9.home_axis(6)

    # Desc : Clears and zeroes the mass balance.    
    def zero_weigh_scale(self):
        c9.delay(1)
        c9.clear_scale()
        c9.zero_scale()
    
#     def catalyst_procedure(self): # blank holder for catalyst procedure
#         pass

# **********************************************************************************************
    def prime_pumps(self):
        # pos represents the position of the carousel dispenser from 1 to 7
        p1.set_carousel_port(p1.carouseldump) 

        # --------------------------------------------------------------------
        # Prime the pump - this is on the Source side

        # First, set the pump and valve to the default valve position
        # NOTE : Default valve position has the valve to the source tank open.
        c9.set_pump_valve(p1.pumpnum,0)

        c9.delay(1)
        c9.home_pump(p1.pumpnum)

        # home the pump (again?!)
        c9.delay(1)
        c9.set_pump_valve(p1.pumpnum,0)

        # suck up X ml from vial
        c9.delay(1)
        c9.aspirate_ml(p1.pumpnum,1) # 1 was 0.5
        c9.delay(2) # almost certainly need this delay for the fluid to be sucked up fully with the negative pump pressure

        # set the pump and switch the valve to the dispense position
        c9.set_pump_valve(p1.pumpnum,1)

        # dispense X ml from vial
        c9.delay(1)
        c9.dispense_ml(p1.pumpnum,1)
        c9.delay(2) # need this delay as there are still some drops falling as the tube dispenses the fluid with positive pump pressure

        # set the pump and switch the valve back to default valve position
        c9.set_pump_valve(p1.pumpnum,0)
        c9.delay(1)
        
    def catalyst_procedure(self, dispense_num):
        # Move Carousel to position where it will Dispense into Vial
        # dispense_num is for tracking and recording the weights
        p1.set_carousel_port(p1.carouselsink)

        # --------------------------------------------------------------------
        # Have the pump suck up a full cylinder of fluid from Source

        # First, set the pump and valve to the default valve position (just in case)
        # NOTE : Default valve position has the valve to the source tank open.
        c9.set_pump_valve(p1.pumpnum,0)
        c9.delay(1)

        # suck up X ml from source
        c9.aspirate_ml(p1.pumpnum,1) # 1 was 0.5
        c9.delay(2) # almost certainly need this delay for the fluid to be sucked up fully with the negative pump pressure

        # set the pump and switch the valve to the dispense position
        c9.set_pump_valve(p1.pumpnum,1)
        c9.delay(1)

        # -------------------------------------------------------------

        # Zero the weight scale with the empty vial
        # We are about to measure (by weight) how much liquid we have dispensed  
        p1.zero_weigh_scale()

        # -------------------------------------------------------------
        # Measuring weight of (incrementally) dispensed fluid on mass balance in a closed feedback loop manner till it hits the weight target.
        # Dispensation quantity of fluid from the pump is stepped down as mass balance approaches its target of 0.050 mL.
        # For distilled water, there is a 1:1 relationship between fluid weight and fluid volume (i.e. 1.000 g = 1.000 mL).
        # Would need to calculate the ratio for fluids of different chemicals accordingly using their concentration (i.e. molar mass).
        # If the fluid pump has already dispensed more than 3/4 of the quantity of fluid in the cylinder, the pump is refilled (re-primed).

        wgt = p1.measure_weight()
        addon_disp = 0
        # p1.target_wgt = 1.000  # use this if you want to over-ride the setting made in the constructor (way up above)
        dispvar = 0.025  # by default, dispense this much mL (the smallest displacement as seen below in the while)

        # we are attempting to hit the targeted weight within 0.01 of the vial's weight reading
        # whereupon we stop dispensing fluid.
        while ((p1.target_wgt - wgt) > 0.005):
            # dispense X ml from vial    
            if (p1.target_wgt - wgt > 0.50):
                dispvar = 0.45     
            elif (p1.target_wgt - wgt > 0.35):
                dispvar = 0.32   
            elif (p1.target_wgt - wgt > 0.15):
                dispvar = 0.12
            elif (p1.target_wgt - wgt > 0.05):
                dispvar = 0.04
            elif (p1.target_wgt - wgt > 0.02):
                dispvar = 0.025
            else:
                dispvar = 0.025

            addon_disp += dispvar

            c9.dispense_ml(p1.pumpnum,dispvar)

            wgt = p1.measure_weight()
            #print(wgt)

            # if pump has dispensed more than 3/4 of its volume, dump the remainder and refill (re-prime) the pump
            if(addon_disp > 0.9):     
                p1.set_carousel_port(p1.carouseldump) # move to the position of the fluid dump receptical

                c9.delay(1)
                c9.home_pump(p1.pumpnum)

                c9.delay(1)
                c9.set_pump_valve(p1.pumpnum,0)

                # suck up X ml from source
                c9.aspirate_ml(p1.pumpnum,1) # fill full cylinder
                c9.delay(2) # almost certainly need this delay for the fluid to be sucked up fully with the negative pump pressure

                # move carousel back over vial
                p1.set_carousel_port(p1.carouselsink)

                # return back to dispensing valve position
                c9.delay(2)
                c9.set_pump_valve(p1.pumpnum,1)
                c9.delay(2)            

                addon_disp = 0 # reset the adddon_disp variable since we have filled up the cylinder to 100%
                # we are ready to continue

        print(wgt)
        dict[f'{experiment_name}'][f'Test_{exp_count}']['Metric']['X_mass'][dispense_num] = wgt # Add final weight to dictionary for tracking

        # --------------------------------------------------------------------

        # Set the pump and switch the valve back to default valve position.
        c9.delay(0.5)
        c9.set_pump_valve(p1.pumpnum,0)
        c9.delay(2)

        # --------------------------------------------------------------------

        # Move to the fluid dump receptical to dump remainder fluid in the pump's cylinder.
        p1.set_carousel_port(p1.carouseldump)

        # --------------------------------------------------------------------

        # Perform the dump of fluid into the fluid dump receiptical.
        c9.home_pump(p1.pumpnum)
        c9.delay(3)

        # --------------------------------------------------------------------

        # Return the carousel rotation and elevation axis to its home position.
        # p1.home_carousel_axis()

    # --------------------------------------------------------------------
    # END
