# Desc : This program demonstrats how to run the Potentiostat .exe program from Python.

# libraries.
import sys, string, os
import json, csv, io
import numpy as np
import pprint as pp
import time

# change directory.
directory = 'C:/EC-Lab Development Package_Copy4/Examples/C-C++/VisualStudio/MFCStaticLink/output/'
os.chdir(directory);
# run the program.
# replace the text string after -p to the technique required and corresponding settings.
# the example below illustrates the OCV technique.


class Technique():

    #expt_count is for keeping track of numerous experiments run in succession. Change this number if for whatever
    #reason you do not want to start at 0
    global expt_count
    global total_time
    expt_count = 0
    total_time = 0

    def ocv(self, root_path, test_name, rest_time_T, record_every_dE = 0.1, record_every_dT = 0.1, E_range = 'KBIO_ERANGE_AUTO', xctr = 0):
        ''' Eventual information and parameters for this technique and how it works'''
        global expt_count #Setting global variable so it can update outside of function
        global total_time #Setting global variable so it can update outside of function
        info = locals() #Obtaining parameter data to store as meta data
        time_start = time.time() # Get time that sequence started

        parameter_string = f'The following parameters will be run: \nOCV\nrest_time_T = {rest_time_T} s\nrecord_every_dE = {record_every_dE} V\n' \
                           f'record_every_dT = {record_every_dT} s\nE_range = {E_range}\nxctr = {xctr}'
        print(parameter_string)
        os.system(f'MFCStaticLink.exe -p OCV {rest_time_T} {record_every_dE} {record_every_dT} {E_range} {xctr}')
        time_end = time.time() - time_start # Obtain total time length of the sequence

        with open(f'{directory}potentiostat_data.txt') as f:
            data = csv.DictReader(f)
            dict = {'OCV': {'meta':[],'time_all':[],'time': [], 'Ewe': [], 'Ece': []}}
            dict['OCV']['meta'].append(time.ctime(time_start))
            dict['OCV']['meta'].append(f'Sequence time = {time_end} s')
            dict['OCV']['meta'].append(str(info))
            i = 0
            for row in data:
                dict['OCV']['time_all'].append(float(row['Time (s)']) + total_time)
                dict['OCV']['time'].append(float(row['Time (s)']))
                dict['OCV']['Ewe'].append(float(row['Ewe (V)']))
                dict['OCV']['Ece'].append(float(row['Ece (V)']))
                i += 1
        with open(f'{root_path}{test_name}_OCV_{expt_count}_raw.json', 'w') as fp:
            json.dump(dict, fp, indent=4)
        expt_count += 1
        total_time = total_time + time_end

    def cv(self, root_path, test_name, vs_initial, voltage_step, scan_rate, record_every_dE, scan_number = 2, average_every_dE = 'FALSE', n_cycles = 0,
           begin_measuring_I = 1,end_measuring_I = 1,I_range = 'KBIO_IRANGE_10mA',E_range = 'KBIO_ERANGE_AUTO',bandwidth = 'KBIO_BW_5',xctr = 0):
        ''' Eventual information and parameters for this technique'''

        if (len(vs_initial) !=5 or len(voltage_step) !=5 or len(scan_rate) !=5): # Error in case fed parameters are not of length = 5 (required for this technique)
            raise CustomError('vs_initial,voltage_step and scan_rate must be equal length array = 5')
        else:
            pass

        global expt_count
        global total_time
        info = locals()  # Obtaining parameter data to store as meta data
        time_start = time.time()  # Get time that sequence started

        print(f'The following parameters will be run: CV {vs_initial[0]} {voltage_step[0]} {scan_rate[0]} '
              f'{vs_initial[1]} {voltage_step[1]} {scan_rate[1]} '
              f'{vs_initial[2]} {voltage_step[2]} {scan_rate[2]} '
              f'{vs_initial[3]} {voltage_step[3]} {scan_rate[3]} '
              f'{vs_initial[4]} {voltage_step[4]} {scan_rate[4]} '
              f'{scan_number} {record_every_dE} {average_every_dE} {n_cycles} '
              f'{begin_measuring_I} {end_measuring_I} {I_range} {E_range} {bandwidth} {xctr}')

        #Below populates the .exe command string and then runs the .exe
        cv_string = 'MFCStaticLink.exe -p CV '
        for i in range(len(vs_initial)):
            cv_string += f'{vs_initial[i]} {voltage_step[i]} {scan_rate[i]} '
        cv_string += f'{scan_number} {record_every_dE} {average_every_dE} {n_cycles} {begin_measuring_I} {end_measuring_I} {I_range} {E_range} {bandwidth} {xctr}'
        os.system(cv_string)

        time_end = time.time() - time_start #Obtain total time length of the sequence
        with open(f'{directory}potentiostat_data.txt') as f:
            data = csv.DictReader(f)
            dict = {'CV':{'meta':[],'time_all':[],'time':[],'Ewe':[],'Ece':[],'I':[],'cycle':[]}}
            dict['CV']['meta'].append(time.ctime(time_start))
            dict['CV']['meta'].append(f'Sequence time = {time_end} s')
            dict['CV']['meta'].append(str(info))
            i = 0
            for row in data:
                dict['CV']['time_all'].append(float(row['Time (s)']) + total_time)
                dict['CV']['time'].append(float(row['Time (s)']))
                dict['CV']['Ewe'].append(float(row['Ewe (V)']))
                dict['CV']['Ece'].append(float(row['Ece (V)']))
                dict['CV']['I'].append(float(row['I (A)']))
                dict['CV']['cycle'].append(float(row['Cycle']))
                i += 1
        with open(f'{root_path}{test_name}_CV_{expt_count}_raw.json', 'w') as fp:
            json.dump(dict, fp, indent=4)
        expt_count += 1
        total_time = total_time + time_end

    def ca(self, root_path, test_name, voltage_step, vs_initial, duration_step, n_cycles = 0, record_every_dI = 0.01, record_every_dt = 0.1,
           I_range = 'KBIO_IRANGE_1mA',E_range = 'KBIO_ERANGE_AUTO',bandwidth = 'KBIO_BW_5',xctr = 0):

        # if len(vs_initial) != len(voltage_step) != len(duration_step):  # Error in case fed parameters are not of length = 5 (required for this technique)
        #     raise CustomError('vs_initial,voltage_step and scan_rate must be equal length array = 5')
        # else:
        #     pass

        global expt_count
        global total_time
        info = locals()  # Obtaining parameter data to store as meta data
        time_start = time.time()  # Get time that sequence started

        print(f'Currently running CA on step {expt_count} of the experiment')
        #Below populates the .exe command string and then runs the .exe
        cv_string = f'MFCStaticLink.exe -p CA {len(voltage_step) -1}' # -1 due to the offset of the first term being 0
        for i in range(len(voltage_step)):
            cv_string += f' {voltage_step[i]} {vs_initial[i]} {duration_step[i]}'
        cv_string += f' {n_cycles} {record_every_dI} {record_every_dt} {I_range} {E_range} {bandwidth} {xctr}'

        print(f'The following parameters will be run \n{cv_string}')
        os.system(cv_string)

        time_end = time.time() - time_start  # Obtain total time length of the sequence

        with open(f'{directory}potentiostat_data.txt') as f:
            data = csv.DictReader(f)
            dict = {'CA':{'meta':[],'time_all':[],'time':[],'Ewe':[],'I':[],'cycle':[]}}
            dict['CA']['meta'].append(time.ctime(time_start))
            dict['CA']['meta'].append(f'Sequence time = {time_end} s')
            dict['CA']['meta'].append(str(info))
            i = 0
            for row in data:
                dict['CA']['time_all'].append(float(row['Time (s)']) + total_time)
                dict['CA']['time'].append(float(row['Time (s)']))
                dict['CA']['Ewe'].append(float(row['Ewe (V)']))
                dict['CA']['I'].append(float(row['I (A)']))
                dict['CA']['cycle'].append(float(row['Cycle']))
                i += 1
        with open(f'{root_path}{test_name}_CA_{expt_count}_raw.json', 'w') as fp:
            json.dump(dict, fp, indent=4)
        expt_count += 1
        total_time = total_time + time_end

    '''TODO - need to figure out a way with the current format to limit deposition based on total charge passed - how to actually monitor this during deposition'''

    def cp(self,root_path, test_name, current_step, vs_initial, duration_step, n_cycles = 0, record_every_dE = 0.01, record_every_dt = 0.1,
           I_range = 'KBIO_IRANGE_1mA',E_range = 'KBIO_ERANGE_AUTO',bandwidth = 'KBIO_BW_5',xctr = 0):

        global expt_count
        global total_time
        info = locals()  # Obtaining parameter data to store as meta data
        time_start = time.time()  # Get time that sequence started

        print(f'Currently running CP on step {expt_count} of the experiment')
        #Below populates the .exe command string and then runs the .exe
        cv_string = f'MFCStaticLink.exe -p CP {len(current_step) -1}' # -1 due to the offset of the first term being 0
        for i in range(len(current_step)):
            cv_string += f' {current_step[i]} {vs_initial[i]} {duration_step[i]}'
        cv_string += f' {n_cycles} {record_every_dE} {record_every_dt} {I_range} {E_range} {bandwidth} {xctr}'

        print(f'The following parameters will be run \n{cv_string}')
        os.system(cv_string)

        time_end = time.time() - time_start  # Obtain total time length of the sequence

        with open(f'{directory}potentiostat_data.txt') as f:
            data = csv.DictReader(f)
            dict = {'CP':{'meta':[],'time_all':[],'time':[],'Ewe':[],'I':[],'cycle':[]}}
            dict['CP']['meta'].append(time.ctime(time_start))
            dict['CP']['meta'].append(f'Sequence time = {time_end} s')
            dict['CP']['meta'].append(str(info))
            i = 0
            for row in data:
                dict['CP']['time_all'].append(float(row['Time (s)']) + total_time)
                dict['CP']['time'].append(float(row['Time (s)']))
                dict['CP']['Ewe'].append(float(row['Ewe (V)']))
                dict['CP']['I'].append(float(row['I (A)']))
                dict['CP']['cycle'].append(float(row['Cycle']))
                i += 1
        with open(f'{root_path}{test_name}_CP_{expt_count}_raw.json', 'w') as fp:
            json.dump(dict, fp, indent=4)
        expt_count += 1
        total_time = total_time + time_end

    def geis(self, root_path, test_name, vs_initial,vs_final,initial_current_step,final_current_step, amplitude, frequency_number, final_frequency, initial_frequency,
             duration_step = 0, step_number = 0, record_every_dT = 0.1,record_every_dE = 0.01,sweep = 'False', average_n_times = 1, correction = 'False',
             wait_for_steady = 0.1, I_range = 'KBIO_IRANGE_1mA', E_range = 'KBIO_ERANGE_AUTO', bandwidth = 'KBIO_BW_5', xctr = 0):

        global expt_count
        global total_time
        info = locals()  # Obtaining parameter data to store as meta data
        time_start = time.time()  # Get time that sequence started
        print(f'Currently running GEIS on step {expt_count} of the experiment')

        print(f'The following parameters will be run {vs_initial} {vs_final} {initial_current_step} {final_current_step} {duration_step} {step_number} '
             f'{record_every_dT} {record_every_dE} {final_frequency} {initial_frequency} {sweep} {amplitude} {frequency_number} '
             f'{average_n_times} {correction} {wait_for_steady} {I_range} {E_range} {bandwidth} {xctr}')

        os.system(f'MFCStaticLink.exe -p GEIS {vs_initial} {vs_final} {initial_current_step} {final_current_step} {duration_step} {step_number} '
             f'{record_every_dT} {record_every_dE} {final_frequency} {initial_frequency} {sweep} {amplitude} {frequency_number} '
             f'{average_n_times} {correction} {wait_for_steady} {I_range} {E_range} {bandwidth} {xctr}')

        time_end = time.time() - time_start  # Obtain total time length of the sequence
        with open(f'{directory}potentiostat_data.txt') as f:
            data = csv.DictReader(f)
            dict = {'GEIS':{'meta':[],'time_all':[],'time':[],'freq':[],'Ewe_bar':[],'I_bar':[],'phase_Zwe':[],'Ewe':[],'I':[],'Ece_bar':[],
                          'Ice_bar':[],'phase_Zce':[],'Ece':[]}}
            dict['GEIS']['meta'].append(time.ctime(time_start))
            dict['GEIS']['meta'].append(f'Sequence time = {time_end} s')
            dict['GEIS']['meta'].append(str(info))
            i = 0
            for row in data:
                dict['GEIS']['time_all'].append(float(row['t']) + total_time)
                dict['GEIS']['time'].append(float(row['t']))
                dict['GEIS']['freq'].append(float(row['freq']))
                dict['GEIS']['Ewe_bar'].append(float(row['ewe_bar']))
                dict['GEIS']['I_bar'].append(float(row['I_bar']))
                dict['GEIS']['phase_Zwe'].append(float(row['phase_zwe']))
                dict['GEIS']['Ewe'].append(float(row['ewe']))
                dict['GEIS']['I'].append(float(row['I']))
                dict['GEIS']['Ece_bar'].append(float(row['ece_bar']))
                dict['GEIS']['Ice_bar'].append(float(row['ice_bar']))
                dict['GEIS']['phase_Zce'].append(float(row['phase_zce']))
                dict['GEIS']['Ece'].append(float(row['ece']))
                i += 1
        with open(f'{root_path}{test_name}_GEIS_{expt_count}_raw.json', 'w') as fp:
            json.dump(dict, fp, indent=4)
        expt_count += 1
        total_time = total_time + time_end

class CustomError(Exception):
    pass

# class Post_Processing():