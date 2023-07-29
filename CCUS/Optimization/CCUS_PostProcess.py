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

    def experiment_update(self, dict, exp_count, X_choice):
        
        # Import files: #TODO UPDATE LOCATION
        potentiostat_location = "C:\\Users\\Blackr\\Documents\\CCUS\\MAPs\\"
        with open(f'{potentiostat_location}master_runs_depo.json','r') as f:
           depo_json = json.load(f)

        with open(f'{potentiostat_location}master_runs_char1.json','r') as f:
           char1_json = json.load(f)

        with open(f'{potentiostat_location}master_runs_char2.json','r') as f:
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
        with open(f'{potentiostat_location}master_runs_depo.json','w') as f:
            json.dump(depo_json, f)
        with open(f'{potentiostat_location}master_runs_char1.json','w') as f:
            json.dump(char1_json, f)
        with open(f'{potentiostat_location}master_runs_char2.json','w') as f:
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
