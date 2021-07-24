'''
Preamble and introduction on how to use this
'''
# from north_c9 import NorthC9
from nrc_custom.Potentiostat import Technique
import csv, json

# Class variables - must define
root_path = 'C:/Users/Blackr/Documents/NRC_EMAP/EChem/'
test_name = 'Check_CV_Multiple' # Use format 'rbnbp121_TestA', as an example
channel = 0

# current = 0.000171 # current applied in amperes
# duration_initial_cp = 120 # in seconds
# duration_mid_cp = 180 # in seconds
# duration_end_cp = 600 # in seconds

#Instantiate the Technique class, giving access to all the implemented measurement techniques
#TODO - put rootpath, testname, and channel into the class level and not function level
experiment = Technique(root_path,test_name,channel)

# Put below the various techniques and associated parameters that are to be run. Note as it is currently written, each technique will
# save to separate .json files with a specific index number labeling and technique ID, as it would the biologic file. This
# makes it easier to post-process specific sections.

'''The following is the saved format:
{ExperimentID}_{technique}_{exp_count}_raw.json'''

# print(experiment.channel)
# experiment.ocv(rest_time_T = 5)
#
# experiment.ocv(
#         root_path,
#         test_name,
#         rest_time_T = 2.0)

# for i in [0,1]:
#     experiment.cv(
#        root_path,
#        test_name,
#        vs_initial = ['True']*5,
#        voltage_step = [0,-0.25,0,0,0.25],
#        scan_rate = [0.005]*5,
#        record_every_dE = 0.005)

experiment.cv(
   root_path,
   test_name,
   vs_initial = ['True','False','False','True','True'],
   voltage_step = [0,0.3,0.25,0,0],
   scan_rate = [0.05]*5,
   record_every_dE = 0.005)

# experiment.ca(
#        root_path,
#        test_name,
#        vs_initial = ['False']*5,
#        voltage_step = [0,2,0,0,1],
#        duration_step = [0.5]*5)

# experiment.cp(
#        root_path,
#        test_name,
#        vs_initial = ['False']*5,
#        current_step = [100E-6,200E-6,100E-6,-300E-6,0],
#        duration_step = [1]*5)
#
# experiment.geis(
#         root_path,
#         test_name,
#         vs_initial='False',
#         vs_final = 'False',
#         initial_current_step = -1E-3,
#         final_current_step = -1E-3,
#         amplitude = 2E-3,
#         frequency_number = 30,
#         final_frequency=1000E-3,
#         initial_frequency=100E3,
#         duration_step = 0, #refers to how long to hold the voltage initially prior to any frequency measurement
#         average_n_times = 2,)

'''
RB experimentation for Jan 27, 2021
'''
# Deposition Step - do with IDE due to complications of constant current

#Do initial experimentation with a blank slide, just to ensure the formatting works as below

#Step 1 - Initial GEIS with current = 0 #TODO
# experiment.geis(
#         root_path,
#         test_name,
#         vs_initial='False',
#         vs_final = 'False',
#         initial_current_step = 0,
#         final_current_step = 0,
#         amplitude = 5E-6,
#         frequency_number = 10,
#         final_frequency= 1,
#         initial_frequency= 200E3,
#         duration_step = 0, #refers to how long to hold the voltage initially prior to any frequency measurement
#         average_n_times = 1)
#
# #Step 2 - Constant current for initial 2 min 'burn in'
# experiment.cp(
#        root_path,
#        test_name,
#        vs_initial = ['False']*1,
#        current_step = [current]*1,
#        duration_step = [duration_initial_cp]*1)
#
# #Step 3 - Initial GEIS
# experiment.geis(
#         root_path,
#         test_name,
#         vs_initial='False',
#         vs_final = 'False',
#         initial_current_step = current,
#         final_current_step = current,
#         amplitude = 50E-6,
#         frequency_number = 57, # Number of frequencies, back end has it as a log plot - chosen based on rbnbp153 test procedure
#         final_frequency= 60E-3,
#         initial_frequency= 30E3,
#         duration_step = 0, #refers to how long to hold the voltage initially prior to any frequency measurement
#         average_n_times = 1)
#
# #Step 4 - First set of cp measurements, set to run 5 times
# for i in range(0,6):
#        experiment.cp(
#               root_path,
#               test_name,
#               vs_initial = ['False']*1,
#               current_step = [current]*1,
#               duration_step = [duration_mid_cp]*1)
#
#        experiment.geis(
#                root_path,
#                test_name,
#                vs_initial='False',
#                vs_final = 'False',
#                initial_current_step = current,
#                final_current_step = current,
#                amplitude = 50E-6,
#                frequency_number = 57, # Number of frequencies, back end has it as a log plot - chosen based on rbnbp153 test procedure
#                final_frequency= 60E-3,
#                initial_frequency= 30E3,
#                duration_step = 0, #refers to how long to hold the voltage initially prior to any frequency measurement
#                average_n_times = 1)
#
# #Step 5 - Longer spacing for measurements
# for i in range(0, 6):
#        experiment.cp(
#               root_path,
#               test_name,
#               vs_initial=['False']*1,
#               current_step=[current]*1,
#               duration_step=[duration_end_cp]*1)
#
#        experiment.geis(
#               root_path,
#               test_name,
#               vs_initial='False',
#               vs_final='False',
#               initial_current_step=current,
#               final_current_step=current,
#               amplitude=50E-6,
#               frequency_number= 57,
#               # Number of frequencies, back end has it as a log plot - chosen based on rbnbp153 test procedure
#               final_frequency=60E-3,
#               initial_frequency=30E3,
#               duration_step=0,  # refers to how long to hold the voltage initially prior to any frequency measurement
#               average_n_times=1)

'''Running changes to make:
a) GEIS - ensure that you can collect the front end matter as well as the back end into two separate keys in the .json file
b) Add columns to the .json file for Re and Z? Or keep that as post processing? 
e) Ensure the outputs in the .json are equivalent to those currently used in the excel wrapper to allow for same script to be used by both IDE and the NRC python script.
f) Create a larger .json file of all the experiments, along with separate ones? What is better?
g) Errors for all inputs where needed to ensure proper information is passed
h) Add some indicators so can see the progress of a run and in general get an idea of where the experiment is at
'''


