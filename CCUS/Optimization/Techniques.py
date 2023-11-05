import sys
import time
import kbio.kbio_types as KBIO
from kbio.kbio_tech import ECC_parm, make_ecc_parm, make_ecc_parms, unpack_experiment_data
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import csv
import logging
import os
import socket
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Techniques:
    def __init__(self, exp_num, channel, api, id_, device_info, user, labID, material_info, data_save):
        self.exp_num = exp_num
        self.channel = channel
        self.api = api
        self.id_ = id_
        self.device_info = device_info
        self.is_VMP3 = device_info.model in KBIO.VMP3_FAMILY  # detect instrument family
        self.user = user
        self.labID = labID
        self.material_info = material_info
        self.expStart = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
        self.data_save = data_save
        self.data_save_sub = data_save #See original line below. Reassigned here as to not disrupt each technique code below.
        # self.data_save_sub = self.data_save + "exp_" + str(self.exp_num) + "\\"

        # # create subfolder within main
        # if not os.path.exists(self.data_save_sub):
        #     os.makedirs(self.data_save_sub)

        self.tech_num = 0

    def OCV_run_tech(self, rest_time_T, record_every_dE, record_every_dT, E_range):
        """
        Args:
        rest_time_t (float): The amount of time to rest (s)
        record_every_dE (float): Record every dE (V)
        record_every_dT  (float): Record evergy dT (s)
        E_range (str): A string describing the E range to use, see the kbio_types.py for possible values
        """
        Range = {'rest_time_T': rest_time_T, 'record_every_dE': record_every_dE,
                 'record_every_dT': record_every_dT, 'E_range': E_range}
        channel_info = self.api.GetChannelInfo(self.id_, self.channel)  # BL_GetChannelInfos

        if not channel_info.is_kernel_loaded:
            print("> kernel must be loaded in order to run the experiment")
            sys.exit(-1)

        # OCV parameter values
        ocv3_tech_file = "ocv.ecc"
        ocv4_tech_file = "ocv4.ecc"

        # dictionary of OCV parameters
        OCV_parms = {
            'rest_time_T': ECC_parm("Rest_time_T", float),
            'record_every_dT': ECC_parm("Record_every_dT", float),
            'record_every_dE': ECC_parm("Record_every_dE", float),
            'E_range': ECC_parm("E_Range", int),
        }
        # OCV_parms = {
        #     'rest_time_T': ECC_parm("Rest_time_T", float),
        #     'record_every_dT': ECC_parm("Record_every_dT", float),
        #     'record_every_dE': ECC_parm("Record_every_dE", float),
        #     'E_range': ECC_parm("E_Range", int),
        #     'timebase': ECC_parm('tb', int),
        # }

        # pick the correct ecc file based on the instrument family
        tech_file = ocv3_tech_file if self.is_VMP3 else ocv4_tech_file

        # BL_Define<xxx>Parameter
        p_duration = make_ecc_parm(self.api, OCV_parms['rest_time_T'], rest_time_T)
        p_record_dT = make_ecc_parm(self.api, OCV_parms['record_every_dT'], record_every_dT)
        p_record_dE = make_ecc_parm(self.api, OCV_parms['record_every_dE'], record_every_dE)
        p_erange = make_ecc_parm(self.api, OCV_parms['E_range'], KBIO.E_RANGE[E_range].value)
        ecc_parms = make_ecc_parms(self.api, p_duration, p_record_dE, p_record_dT, p_erange)

        # BL_LoadTechnique
        self.api.LoadTechnique(self.id_, self.channel, tech_file, ecc_parms, first=True, last=True, display=False)
        techStart = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
        self.api.StartChannel(self.id_, self.channel)  # BL_StartChannel
        logging.info('Experiment expID: ' + str(self.exp_num) + ' Technique OCV started on channel ' + str(
            self.channel))  # log OCV technique started

        # experiment loop
        t = np.array([])
        Ewe = np.array([])
        Ece = np.array([])
        while True:
            # BL_GetData
            data = self.api.GetData(self.id_, self.channel)
            status, unpacked = unpack_experiment_data(self.api, data, self.is_VMP3)

            t = np.append(t, unpacked[0])
            Ewe = np.append(Ewe, unpacked[1])

            if self.is_VMP3:
                Ece = np.append(Ece, unpacked[2])

            if status == 'STOP':  # save numpy arrays to pandas dataframe and to text file
                techDone = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
                if self.is_VMP3:
                    full_data = pd.DataFrame(data=np.transpose([t, Ewe, Ece]), columns=['t(s)', 'Ewe(V)', 'Ece(V)'])
                else:
                    full_data = pd.DataFrame(data=np.transpose([t, Ewe]), columns=['t(s)', 'Ewe(V)'])
                self.tech_num += 1
                
                filename = 'Test_' + str(self.exp_num) + '_ch' + str(self.channel) + '_OCV_' + str(self.tech_num)+ '.csv'
                #filename = str(self.tech_num) + 'exp' + str(self.exp_num) + '_ch' + str(self.channel) + '_OCV.csv'
                Meta = {'User': self.user, 'LabID': self.labID, 'Material Information': self.material_info, 'Device Type': self.device_info.model,
                        'Exp Start': self.expStart,
                        'Tech Start': techStart, 'Tech Done': techDone, 'Experiment num': self.exp_num,
                        'Technique': 'OCV', 'Channel': self.channel}

                with open(self.data_save_sub + filename, 'w', newline="") as csv_file:
                    writer = csv.writer(csv_file, delimiter=',')
                    for key, value in Meta.items():
                        writer.writerow([key, value])
                    for key, value in Range.items():
                        writer.writerow([key, value])

                full_data.to_csv(self.data_save_sub + filename, header=True, index=None, sep=',', mode='a')
                break

            time.sleep(1)

        logging.info('Experiment expID: ' + str(self.exp_num) + ' Technique OCV finished on channel ' + str(
            self.channel))  # log OCV technique finished
        # print("> OCV experiment done expID=", self.exp_num, " channel=", self.channel)
        return status

    def CP_run_tech(self, current_step, vs_initial, duration_step, n_cycles, record_every_dE,
                    record_every_dt, I_range, E_range, bandwidth):
        """
        NOTE: The current_step, vs_initial and duration_step must be a list or
        tuple with the same length.

        Args:
            current_step (list): List (or tuple) of floats indicating the current steps (A). See NOTE above.
            vs_initial (list): List (or tuple) of booleans indicating whether
                the current steps is vs. the initial one. See NOTE above.
            duration_step (list): List (or tuple) of floats indicating the duration of each step (s). See NOTE above.
            record_every_dt (float): Record every dT (s)
            record_every_dE (float): Record every dE (V)
            n_cycles (int): The number of times the technique is REPEATED.
                NOTE: This means that the default value is 0 which means that the technique will be run once.
            I_range (str): A string describing the I range, see the kbio_types.py for possible values
            E_range (str): A string describing the E range to use, see the kbio_types.py for possible values
            bandwidth (str): A string describing the bandwidth setting, see the kbio_types.py for possible values

        Raises:
            ValueError: When lengths of the lists are not the same length
        """
        Range = {'current_step': current_step, 'vs_initial': vs_initial, 'duration_step': duration_step,
                 'n_cycles': n_cycles, 'record_every_dE': record_every_dE,
                 'record_every_dt': record_every_dt, 'I_range': I_range,
                 'E_range': E_range, 'bandwidth': bandwidth}
        channel_info = self.api.GetChannelInfo(self.id_, self.channel)  # BL_GetChannelInfos
        if not channel_info.is_kernel_loaded:
            print("> kernel must be loaded in order to run the experiment")
            sys.exit(-1)

        # CP parameter values based on the type of device
        cp3_tech_file = "cp.ecc"
        cp4_tech_file = "cp4.ecc",

        # pick the correct ecc file based on the instrument family
        tech_file = cp3_tech_file if self.is_VMP3 else cp4_tech_file

        CP_parms = {
            'current_step': ECC_parm("Current_step", float),
            'step_duration': ECC_parm("Duration_step", float),
            'vs_init': ECC_parm("vs_initial", bool),
            'nb_steps': ECC_parm("Step_number", int),
            'record_dt': ECC_parm("Record_every_dT", float),
            'record_dE': ECC_parm("Record_every_dE", float),
            'repeat': ECC_parm("N_Cycles", int),
            'I_range': ECC_parm("I_Range", int),
            'E_range': ECC_parm("E_Range", int),
            'bandwidth': ECC_parm("Bandwidth", int),
        }

        @dataclass
        class CP_step:
            current: float
            duration: float
            vs_init: bool

        # if not len(current_step) == len(vs_initial) == len(duration_step):
        #     message = 'The length of current_step, vs_initial and ' \
        #               'duration_step must be the same'
        #     raise ValueError(message)

        steps = []
        for i in range(len(current_step)):
            steps.append(CP_step(current_step[i], duration_step[i], vs_initial[i]))

        # BL_Define<xxx>Parameter
        p_steps = list()

        for idx, step in enumerate(steps):
            parm = make_ecc_parm(self.api, CP_parms['current_step'], step.current, idx)
            p_steps.append(parm)
            parm = make_ecc_parm(self.api, CP_parms['step_duration'], step.duration, idx)
            p_steps.append(parm)
            parm = make_ecc_parm(self.api, CP_parms['vs_init'], step.vs_init, idx)
            p_steps.append(parm)

        p_nb_steps = make_ecc_parm(self.api, CP_parms['nb_steps'],
                                   idx)  # number of steps is one less than len(steps)
        p_record_dt = make_ecc_parm(self.api, CP_parms['record_dt'], record_every_dt)
        p_record_dE = make_ecc_parm(self.api, CP_parms['record_dE'], record_every_dE)
        p_repeat = make_ecc_parm(self.api, CP_parms['repeat'], n_cycles)
        p_I_range = make_ecc_parm(self.api, CP_parms['I_range'], KBIO.I_RANGE[I_range].value)
        p_E_range = make_ecc_parm(self.api, CP_parms['E_range'], KBIO.E_RANGE[E_range].value)
        p_bandwidth = make_ecc_parm(self.api, CP_parms['bandwidth'], KBIO.BANDWIDTH[bandwidth].value)

        # make the technique parameter array
        ecc_parms = make_ecc_parms(self.api, *p_steps, p_nb_steps, p_record_dt, p_record_dE, p_I_range, p_E_range,
                                   p_bandwidth, p_repeat)

        # BL_LoadTechnique
        self.api.LoadTechnique(self.id_, self.channel, tech_file, ecc_parms, first=True, last=True, display=False)
        techStart = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
        self.api.StartChannel(self.id_, self.channel)  # BL_StartChannel
        logging.info('Experiment expID: ' + str(self.exp_num) + ' Technique OCV finished on channel ' + str(
            self.channel))  # log OCV technique finished

        # experiment loop
        t = np.array([])
        Ewe = np.array([])
        I = np.array([])
        cycle = np.array([])
        while True:
            # BL_GetData
            data = self.api.GetData(self.id_, self.channel)
            status, unpacked = unpack_experiment_data(self.api, data, self.is_VMP3)

            t = np.append(t, unpacked[0])
            Ewe = np.append(Ewe, unpacked[1])
            I = np.append(I, unpacked[2])
            cycle = np.append(cycle, unpacked[3])

            if status == 'STOP':
                techDone = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
                full_data = pd.DataFrame(data=np.transpose([t, Ewe, I, cycle]),
                                         columns=['t(s)', 'Ewe(V)', 'I(A)', 'cycle'])
                self.tech_num += 1
                filename = 'Test_' + str(self.exp_num) + '_ch' + str(self.channel) + '_CP_' + str(self.tech_num)+ '.csv'
                Meta = {'User': self.user, 'LabID': self.labID, 'Material Information': self.material_info, 'Device Type': self.device_info.model,
                        'Exp Start': self.expStart,
                        'Tech Start': techStart, 'Tech Done': techDone, 'Experiment num': self.exp_num,
                        'Technique': 'CP', 'Channel': self.channel}

                with open(self.data_save_sub + filename, 'w', newline="") as csv_file:
                    writer = csv.writer(csv_file, delimiter=',')
                    for key, value in Meta.items():
                        writer.writerow([key, value])
                    for key, value in Range.items():
                        writer.writerow([key, value])

                full_data.to_csv(self.data_save_sub + filename, header=True, index=None, sep=',', mode='a')
                break
            time.sleep(1)

        logging.info('Experiment expID: ' + str(self.exp_num) + ' Technique CP finished on channel ' + str(
            self.channel))  # log CP technique finished
        # print("> CP experiment done expID=", self.exp_num, " channel=", self.channel)
        return status

    def CV_run_tech(self, vs_initial, voltage_step, scan_rate, record_every_dE, scan_number, average_every_dE,
                    n_cycles, begin_measuring_I, end_measuring_I, I_range, E_range,
                    bandwidth):
        """
        Args:
            vs_initial (list): List (or tuple) of 5 booleans indicating whether the current step is vs. the initial one
            voltage_step (list): List (or tuple) of 5 floats (Ei, E1, E2, Ei, Ef) indicating the voltage steps (V)
            scan_rate (list): List (or tuple) of 5 floats indicating the scan rates (mV/s)
            record_every_dE (float): Record every dE (V)
            scan_number (int): scan number = 2
            average_every_dE (bool): Whether averaging should be performed over dE
            n_cycles (int): The number of cycles
            begin_measuring_I (float): Begin step accumulation, 1 is 100%
            end_measuring_I (float): Begin step accumulation, 1 is 100%
            I_range (str): A string describing the I range, see the kbio_types.py for possible values
            E_range (str): A string describing the E range to use, see the kbio_types.py for possible values
            bandwidth (str): A string describing the bandwidth setting, see the kbio_types.py for possible values

        Raises:
            ValueError: If vs_initial, voltage_step and scan_rate are not all of length 5
        """
        Range = {'vs_initial': vs_initial, 'voltage_step': voltage_step, 'scan_rate': scan_rate,
                 'record_every_dE': record_every_dE,
                 'scan_number': scan_number, 'average_every_dE': average_every_dE, 'n_cycles': n_cycles,
                 'begin_measuring_I': begin_measuring_I, 'end_measuring_I': end_measuring_I,
                 'I_range': I_range, 'E_range': E_range, 'bandwidth': bandwidth}
        channel_info = self.api.GetChannelInfo(self.id_, self.channel)  # BL_GetChannelInfos
        if not channel_info.is_kernel_loaded:
            print("> kernel must be loaded in order to run the experiment")
            sys.exit(-1)

        # CV parameter values based on the type of device
        cv3_tech_file = "cv.ecc"
        cv4_tech_file = "cv4.ecc"

        # pick the correct ecc file based on the instrument family
        tech_file = cv3_tech_file if self.is_VMP3 else cv4_tech_file

        # dictionary of CV parameters (non exhaustive)
        CV_parms = {
            'vs_initial': ECC_parm("vs_initial", bool),
            'voltage_step': ECC_parm("Voltage_step", float),
            'scan_rate': ECC_parm("Scan_Rate", float),
            'record_every_dE': ECC_parm("Record_every_dE", float),
            'scan_number': ECC_parm("Scan_number", int),
            'average_every_dE': ECC_parm("Average_over_dE", bool),
            'n_cycles': ECC_parm("N_Cycles", int),
            'begin_measuring_I': ECC_parm("Begin_measuring_I", float),
            'end_measuring_I': ECC_parm("End_measuring_I", float),
            'I_range': ECC_parm("I_Range", int),
            'E_range': ECC_parm("E_Range", int),
            'bandwidth': ECC_parm("Bandwidth", int),
        }

        @dataclass
        class CV_step:
            voltage: float
            scan: float
            vs_init: bool

        # if len(voltage_step) != 5 or len(vs_initial) != 5 or len(scan_rate) != 5:
        #     message = 'The length of voltage_step, vs_initial and ' \
        #               'scan_rate must be the same and have length = 5'
        #     raise ValueError(message)

        steps = []
        for i in range(len(voltage_step)):
            steps.append(CV_step(voltage_step[i], scan_rate[i], vs_initial[i]))

        # BL_Define<xxx>Parameter
        p_steps = list()

        for idx, step in enumerate(steps):
            parm = make_ecc_parm(self.api, CV_parms['voltage_step'], step.voltage, idx)
            p_steps.append(parm)
            parm = make_ecc_parm(self.api, CV_parms['scan_rate'], step.scan, idx)
            p_steps.append(parm)
            parm = make_ecc_parm(self.api, CV_parms['vs_initial'], step.vs_init, idx)
            p_steps.append(parm)

        p_record_dE = make_ecc_parm(self.api, CV_parms['record_every_dE'], record_every_dE)
        p_scannum = make_ecc_parm(self.api, CV_parms['scan_number'], scan_number)
        p_average_dE = make_ecc_parm(self.api, CV_parms['average_every_dE'], average_every_dE)
        p_ncycles = make_ecc_parm(self.api, CV_parms['n_cycles'], n_cycles)
        p_endI = make_ecc_parm(self.api, CV_parms['end_measuring_I'], end_measuring_I)
        p_beginI = make_ecc_parm(self.api, CV_parms['begin_measuring_I'], begin_measuring_I)
        p_irange = make_ecc_parm(self.api, CV_parms['I_range'], KBIO.I_RANGE[I_range].value)
        p_erange = make_ecc_parm(self.api, CV_parms['E_range'], KBIO.E_RANGE[E_range].value)
        p_bandwidth = make_ecc_parm(self.api, CV_parms['bandwidth'], KBIO.BANDWIDTH[bandwidth].value)

        ecc_parms = make_ecc_parms(self.api, *p_steps, p_record_dE, p_scannum, p_average_dE, p_ncycles, p_endI,
                                   p_beginI, p_irange, p_erange, p_bandwidth)

        # BL_LoadTechnique
        self.api.LoadTechnique(self.id_, self.channel, tech_file, ecc_parms, first=True, last=True, display=False)
        techStart = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
        self.api.StartChannel(self.id_, self.channel)  # BL_StartChannel
        logging.info('Experiment expID: ' + str(self.exp_num) + ' Technique CV started on channel ' + str(
            self.channel))  # log CV technique started

        # experiment loop
        t = np.array([])
        Ewe = np.array([])
        Ec = np.array([])
        Cycle = np.array([])
        I = np.array([])
        while True:
            # BL_GetData
            data = self.api.GetData(self.id_, self.channel)
            status, unpacked = unpack_experiment_data(self.api, data, self.is_VMP3)

            if self.is_VMP3:
                t = np.append(t, unpacked[0])
                Ec = np.append(Ec, unpacked[1])
                I = np.append(I, unpacked[2])
                Ewe = np.append(Ewe, unpacked[3])
                Cycle = np.append(Cycle, unpacked[4])
            else:
                t = np.append(t, unpacked[0])
                I = np.append(I, unpacked[1])
                Ewe = np.append(Ewe, unpacked[2])
                Cycle = np.append(Cycle, unpacked[3])

            if status == 'STOP':
                techDone = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
                if self.is_VMP3:
                    full_data = pd.DataFrame(data=np.transpose([t, Ec, I, Ewe, Cycle]),
                                             columns=['t(s)', 'Ec(V)', 'I(A)', 'Ewe(V)', 'Cycle'])
                else:
                    full_data = pd.DataFrame(data=np.transpose([t, I, Ewe, Cycle]),
                                             columns=['t(s)', 'I(A)', 'Ewe(V)', 'Cycle'])
                self.tech_num += 1
                filename = 'Test_' + str(self.exp_num) + '_ch' + str(self.channel) + '_CV_' + str(self.tech_num)+ '.csv'

                Meta = {'User': self.user, 'LabID': self.labID, 'Material Information': self.material_info, 'Device Type': self.device_info.model,
                        'Exp Start': self.expStart,
                        'Tech Start': techStart, 'Tech Done': techDone, 'Experiment num': self.exp_num,
                        'Technique': 'CV', 'Channel': self.channel}

                with open(self.data_save_sub + filename, 'w', newline="") as csv_file:
                    writer = csv.writer(csv_file, delimiter=',')
                    for key, value in Meta.items():
                        writer.writerow([key, value])
                    for key, value in Range.items():
                        writer.writerow([key, value])
                full_data.to_csv(self.data_save_sub + filename, header=True, index=None, sep=',', mode='a')
                break

            time.sleep(1)

        logging.info('Experiment expID: ' + str(self.exp_num) + ' Technique CV started on channel ' + str(
            self.channel))  # log CV technique started
        # print("> CV experiment done expID=", self.exp_num, " channel=", self.channel)
        return status

    def CA_run_tech(self, voltage_step, vs_initial, duration_step, n_cycles, record_every_di,
                    record_every_dt, I_range, E_range, bandwidth):
        """
        NOTE: The voltage_step, vs_initial and duration_step must be a list or
        tuple with the same length.

        Args:
            voltage_step (list): List (or tuple) of floats indicating the voltage steps (A). See NOTE above.
            vs_initial (list): List (or tuple) of booleans indicating whether
                the current steps is vs. the initial one. See NOTE above.
            duration_step (list): List (or tuple) of floats indicating the duration of each step (s). See NOTE above.
            record_every_dt (float): Record every dT (s)
            record_every_di (float): Record every dI (A)
            n_cycles (int): The number of times the technique is REPEATED.
                NOTE: This means that the default value is 0 which means that the technique will be run once.
            I_range (str): A string describing the I range, see the kbio_types.py for possible values
            E_range (str): A string describing the E range to use, see the kbio_types.py for possible values
            bandwidth (str): A string describing the bandwidth setting, see the kbio_types.py for possible values

        Raises:
            ValueError: When lengths of the lists are not the same length
        """
        Range = {'voltage_step': voltage_step, 'vs_initial': vs_initial, 'duration_step': duration_step,
                 'n_cycles': n_cycles,
                 'record_every_di': record_every_di, 'record_every_dt': record_every_dt, 'I_range': I_range,
                 'E_range': E_range, 'bandwidth': bandwidth}

        channel_info = self.api.GetChannelInfo(self.id_, self.channel)  # BL_GetChannelInfos
        if not channel_info.is_kernel_loaded:
            print("> kernel must be loaded in order to run the experiment")
            sys.exit(-1)

        # CV parameter values based on the type of device
        ca3_tech_file = "ca.ecc"
        ca4_tech_file = "ca4.ecc"

        # pick the correct ecc file based on the instrument family
        tech_file = ca3_tech_file if self.is_VMP3 else ca4_tech_file

        # dictionary of CA parameters (non exhaustive)
        CA_parms = {
            'voltage_step': ECC_parm("Voltage_step", float),
            'step_duration': ECC_parm("Duration_step", float),
            'vs_init': ECC_parm("vs_initial", bool),
            'nb_steps': ECC_parm("Step_number", int),
            'record_dt': ECC_parm("Record_every_dT", float),
            'record_dI': ECC_parm("Record_every_dI", float),
            'repeat': ECC_parm("N_Cycles", int),
            'I_range': ECC_parm("I_Range", int),
            'E_range': ECC_parm("E_Range", int),
            'bandwidth': ECC_parm("Bandwidth", int),
        }
        
        
        # This was the old GC_command that had to be added like this due to the CA run being non-blocking. Had to do it inline with the command after x time
        # def GC_command(command):
        
        #     # create a socket object
        #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #     # connect to the remote host
        #     sock.connect(('192.168.1.90', 8888))

        #     # send the command
        #     cmd = str(command)
        #     sock.send(cmd.encode())

        #     # receive the response
        #     response = sock.recv(1024).decode()
        #     print('Response:', response)

        #     # close the connection
        #     sock.close()

        @dataclass
        class CA_step:
            voltage: float
            duration: float
            vs_init: bool
        
        # if not len(voltage_step) == len(vs_initial) == len(duration_step):
        #     message = 'The length of voltage_step, vs_initial and ' \
        #               'duration_step must be the same'
        #     raise ValueError(message)

        steps = []
        for i in range(len(voltage_step)):
            steps.append(CA_step(voltage_step[i], duration_step[i], vs_initial[i]))

        # BL_Define<xxx>Parameter
        p_steps = list()

        for idx, step in enumerate(steps):
            parm = make_ecc_parm(self.api, CA_parms['voltage_step'], step.voltage, idx)
            p_steps.append(parm)
            parm = make_ecc_parm(self.api, CA_parms['step_duration'], step.duration, idx)
            p_steps.append(parm)
            parm = make_ecc_parm(self.api, CA_parms['vs_init'], step.vs_init, idx)
            p_steps.append(parm)

        p_nb_steps = make_ecc_parm(self.api, CA_parms['nb_steps'],
                                   idx)  # number of steps is one less than len(steps)
        p_record_dt = make_ecc_parm(self.api, CA_parms['record_dt'], record_every_dt)
        p_record_dI = make_ecc_parm(self.api, CA_parms['record_dI'], record_every_di)
        p_repeat = make_ecc_parm(self.api, CA_parms['repeat'], n_cycles)
        p_I_range = make_ecc_parm(self.api, CA_parms['I_range'], KBIO.I_RANGE[I_range].value)
        p_E_range = make_ecc_parm(self.api, CA_parms['E_range'], KBIO.E_RANGE[E_range].value)
        p_bandwidth = make_ecc_parm(self.api, CA_parms['bandwidth'], KBIO.BANDWIDTH[bandwidth].value)

        # make the technique parameter array
        ecc_parms = make_ecc_parms(self.api, *p_steps, p_nb_steps, p_record_dt, p_record_dI, p_repeat, p_I_range,
                                   p_E_range, p_bandwidth)

        # BL_LoadTechnique
        self.api.LoadTechnique(self.id_, self.channel, tech_file, ecc_parms, first=True, last=True, display=False)
        techStart = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
        # BL_StartChannel
        try: 
            status, unpacked = unpack_experiment_data(self.api, data, self.is_VMP3)
        except:
            print('I think the *Cannot unpack NoneType* error has triggered - except to ignore') #Issue with this is it will ignore all errors that occur here, in future make specific to error
            status = 'STOP'

        self.api.StartChannel(self.id_, self.channel)
        logging.info('Experiment expID: ' + str(self.exp_num) + ' Technique CA started on channel ' + str(
            self.channel))  # log CA technique started

        # experiment loop
        t = np.array([])
        Ewe = np.array([])
        I = np.array([])
        cycle = np.array([])
        
        executed = False 
        
        #empty arrays for graphing purposes
        t_graph = []
        I_graph = []
        
        while True:
            # BL_GetData
            data = self.api.GetData(self.id_, self.channel)
            try: 
                status, unpacked = unpack_experiment_data(self.api, data, self.is_VMP3)
            except:
                print('I think the *Cannot unpack NoneType* error has triggered - except to ignore') #Issue with this is it will ignore all errors that occur here, in future make specific to error
                status = 'STOP' #This should make it go back to the previous value and the unpacking did not occur so using previous values

            t = np.append(t, unpacked[0])
            print("Time is: " + str(t[-1]))
            Ewe = np.append(Ewe, unpacked[1])
            print("Voltage is: " + str(Ewe[-1]))
            I = np.append(I, unpacked[2])
            print("Current is: " + str(I[-1]))
            cycle = np.append(cycle, unpacked[3])
                
            # # This is to plot the data as it is generated
            # plt.style.use('fivethirtyeight')
            # fig = plt.figure()
            # ax1 = fig.add_subplot(1,1,1)
            # if len(t) > 1:
            #     t_graph.append(t[-1])
            #     I_graph.append(I[-1])
            #     ax1.clear()
            #     #ax1.ylabel('time (s)')
            #     #ax1.xlabel('current (A)')
            #     #ax1.title('exp' + str(self.exp_num) + '_ch' + str(self.channel) + '_' + str(self.tech_num) + '_CA')
            #     ax1.plot(t_graph, I_graph)
            
            # plt.show()
            
            # This is to plot the data as it is generated
            if len(t) > 1:
                t_graph.append(t[-1])
                I_graph.append(I[-1])
                plt.plot(t_graph, I_graph)
                plt.xlabel('Time (s)')
                plt.ylabel('I (A)')
                plt.title('exp' + str(self.exp_num) + '_ch' + str(self.channel) + '_' + str(self.tech_num) + '_CA')
                plt.show()
        
            # This was the GC command to inject after x amount of time on the Agilent        
            # if len(t) > 1 and t[-1] >= 575 and executed == False:
            #     GC_command('start')
            #     print("The GC is about to do an injection...")
            #     executed = True
            
            print("This is the status: " + str(status))
            
            if status == 'STOP':
                # Process the data and save to an excel file
                techDone = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
                full_data = pd.DataFrame(data=np.transpose([t, Ewe, I, cycle]),
                                         columns=['t(s)', 'Ewe(V)', 'I(A)', 'cycle'])
                self.tech_num += 1
                filename = 'Test_' + str(self.exp_num) + '_ch' + str(self.channel) + '_CA_' + str(self.tech_num)+ '.csv'
                Meta = {'User': self.user, 'LabID': self.labID, 'Material Information': self.material_info, 'Device Type': self.device_info.model,
                        'Exp Start': self.expStart,
                        'Tech Start': techStart, 'Tech Done': techDone, 'Experiment num': self.exp_num,
                        'Technique': 'CA', 'Channel': self.channel}
                with open(self.data_save_sub + filename, 'w', newline="") as csv_file:
                    writer = csv.writer(csv_file, delimiter=',')
                    for key, value in Meta.items():
                        writer.writerow([key, value])
                    for key, value in Range.items():
                        writer.writerow([key, value])

                full_data.to_csv(self.data_save_sub + filename, header=True, index=None, sep=',', mode='a')
                break
            
                #Make and save the final plot
                print('did we get to the final print graph?')
                plt.plot(t, I)
                plt.xlabel('Time (s)')
                plt.ylabel('I (A)')
                plt.title(filename)
                plt.savefig(fname = f'{filename}_Final.jpeg', dpi = 300)
                plt.show()

            time.sleep(1)

        logging.info('Experiment expID: ' + str(self.exp_num) + ' Technique CA finished on channel ' + str(
            self.channel))  # log CA technique finished
        # print("> CA experiment done expID=", self.exp_num, " channel=", self.channel)
        return status

    def GEIS_run_tech(self, vs_initial, vs_final, initial_current_step, final_current_step, amplitude,
                      frequency_number, final_frequency, initial_frequency, duration_step,
                      step_number, record_every_dT, record_every_dE, sweep, average_n_times,
                      correction, wait_for_steady, I_range, E_range, bandwidth):

        """
        Args:
            vs_initial (bool): Whether the voltage step is vs. the initial one
            vs_final (bool): Whether the voltage step is vs. the final one
            initial_current_step (float): The initial current step (A)
            final_current_step (float): The final current step (A)
            amplitude (float): Amplitude of sine (A)
            frequency_number (int): The number of frequencies
            final_frequency (float): The final frequency (Hz)
            initial_frequency (float): The initial frequency (Hz)
            duration_step (float): Duration of step (s)
            step_number (int): The number of current steps (Number of steps minus 1)
            record_every_dT (float): Record every dT (s)
            record_every_dE (float): Record every dE (V)
            sweep (bool): Sweep linear/logarithmic (True for linear points spacing)
            average_n_times (int): The number of repeat times used for frequency averaging
            correction (bool): Non-stationary correction
            wait_for_steady (float): The number of periods to wait before each frequency
            I_range (str): A string describing the I range, see the kbio_types.py for possible values
            E_range (str): A string describing the E range to use, see the kbio_types.py for possible values
            bandwidth (str): A string describing the bandwidth setting, see the kbio_types.py for possible values
        """
        Range = {'vs_initial': vs_initial, 'vs_final': vs_final,
                 'initial_current_step': initial_current_step, 'final_current_step': final_current_step,
                 'amplitude': amplitude, 'frequency_number': frequency_number,
                 'final_frequency': final_frequency, 'initial_frequency': initial_frequency,
                 'duration_step': duration_step, 'step_number': step_number,
                 'record_every_dT': record_every_dT, 'record_every_dE': record_every_dE,
                 'sweep': sweep, 'average_n_times': average_n_times, 'correction': correction,
                 'wait_for_steady': wait_for_steady, 'I_range': I_range,
                 'E_range': E_range, 'bandwidth': bandwidth}
        channel_info = self.api.GetChannelInfo(self.id_, self.channel)  # BL_GetChannelInfos
        if not channel_info.is_kernel_loaded:
            print("> kernel must be loaded in order to run the experiment")
            sys.exit(-1)

        # GEIS parameter values based on the type of device
        geis3_tech_file = "geis.ecc"
        geis4_tech_file = "geis4.ecc"

        # pick the correct ecc file based on the instrument family
        tech_file = geis3_tech_file if self.is_VMP3 else geis4_tech_file

        # dictionary of GEIS parameters (non exhaustive)
        GEIS_parms = {
            'vs_initial': ECC_parm("vs_initial", bool),
            'vs_final': ECC_parm("vs_final", bool),
            'initial_current_step': ECC_parm("Initial_Current_step", float),
            'final_current_step': ECC_parm("Final_Current_step", float),
            'amplitude': ECC_parm("Amplitude_Current", float),
            'frequency_number': ECC_parm("Frequency_number", int),
            'final_frequency': ECC_parm("Final_frequency", float),
            'initial_frequency': ECC_parm("Initial_frequency", float),
            'duration_step': ECC_parm("Duration_step", float),
            'step_number': ECC_parm("Step_number", int),
            'record_every_dT': ECC_parm("Record_every_dT", float),
            'record_every_dE': ECC_parm("Record_every_dE", float),
            'sweep': ECC_parm("sweep", bool),
            'average_n_times': ECC_parm("Average_N_times", int),
            'correction': ECC_parm("Correction", bool),
            'wait_for_steady': ECC_parm("Wait_for_steady", float),
            'I_range': ECC_parm("I_Range", int),
            'E_range': ECC_parm("E_Range", int),
            'bandwidth': ECC_parm("Bandwidth", int),
        }

        # BL_Define<xxx>Parameter
        p_vs_initial = make_ecc_parm(self.api, GEIS_parms['vs_initial'], vs_initial)
        p_vs_final = make_ecc_parm(self.api, GEIS_parms['vs_final'], vs_final)
        p_initial_current_step = make_ecc_parm(self.api, GEIS_parms['initial_current_step'], initial_current_step)
        p_final_current_step = make_ecc_parm(self.api, GEIS_parms['final_current_step'], final_current_step)
        p_amplitude = make_ecc_parm(self.api, GEIS_parms['amplitude'], amplitude)
        p_frequency_number = make_ecc_parm(self.api, GEIS_parms['frequency_number'], frequency_number)
        p_final_frequency = make_ecc_parm(self.api, GEIS_parms['final_frequency'], final_frequency)
        p_initial_frequency = make_ecc_parm(self.api, GEIS_parms['initial_frequency'], initial_frequency)
        p_duration_step = make_ecc_parm(self.api, GEIS_parms['duration_step'], duration_step)
        p_step_number = make_ecc_parm(self.api, GEIS_parms['step_number'], step_number)
        p_record_every_dT = make_ecc_parm(self.api, GEIS_parms['record_every_dT'], record_every_dT)
        p_record_every_dE = make_ecc_parm(self.api, GEIS_parms['record_every_dE'], record_every_dE)
        p_sweep = make_ecc_parm(self.api, GEIS_parms['sweep'], sweep)
        p_average_n_times = make_ecc_parm(self.api, GEIS_parms['average_n_times'], average_n_times)
        p_correction = make_ecc_parm(self.api, GEIS_parms['correction'], correction)
        p_wait_for_steady = make_ecc_parm(self.api, GEIS_parms['wait_for_steady'], wait_for_steady)
        p_irange = make_ecc_parm(self.api, GEIS_parms['I_range'], KBIO.I_RANGE[I_range].value)
        p_erange = make_ecc_parm(self.api, GEIS_parms['E_range'], KBIO.E_RANGE[E_range].value)
        p_bandwidth = make_ecc_parm(self.api, GEIS_parms['bandwidth'], KBIO.BANDWIDTH[bandwidth].value)

        ecc_parms = make_ecc_parms(self.api, p_vs_initial, p_vs_final, p_initial_current_step, p_final_current_step,
                                   p_amplitude, p_frequency_number, p_final_frequency, p_initial_frequency,
                                   p_duration_step, p_step_number, p_record_every_dT, p_record_every_dE, p_sweep,
                                   p_average_n_times, p_correction, p_wait_for_steady, p_irange, p_erange,
                                   p_bandwidth)

        # BL_LoadTechnique
        self.api.LoadTechnique(self.id_, self.channel, tech_file, ecc_parms, first=True, last=True, display=False)
        techStart = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
        self.api.StartChannel(self.id_, self.channel)  # BL_StartChannel
        logging.info('Experiment expID: ' + str(self.exp_num) + ' Technique GEIS started on channel ' + str(
            self.channel))  # log GEIS technique started

        # experiment loop
        t = np.array([])
        freq = np.array([])
        Ewe_bar = np.array([])
        I_bar = np.array([])
        Phase_zwe = np.array([])
        Ewe = np.array([])
        I = np.array([])
        Ece_bar = np.array([])
        Ice_bar = np.array([])
        Phase_zce = np.array([])
        Ece = np.array([])
        I_range = np.array([])
        abs_Z = np.array([])
        Re_Z = np.array([])
        Im_Z = np.array([])
        
        #empty arrays for graphing purposes
        Re_graph = []
        Im_graph = []
        abs_Z_graph = []
        Re_Z_graph = []
        Im_Z_graph = []
        
        while True:
            # BL_GetData
            data = self.api.GetData(self.id_, self.channel)
            status, unpacked = unpack_experiment_data(self.api, data, self.is_VMP3)

            t = np.append(t, unpacked[0])
            freq = np.append(freq, unpacked[1])
            Ewe_bar = np.append(Ewe_bar, unpacked[2])
            I_bar = np.append(I_bar, unpacked[3])
            Phase_zwe = np.append(Phase_zwe, unpacked[4])
            Ewe = np.append(Ewe, unpacked[5])
            I = np.append(I, unpacked[6])
            Ece_bar = np.append(Ece_bar, unpacked[7])
            Ice_bar = np.append(Ice_bar, unpacked[8])
            Phase_zce = np.append(Phase_zce, unpacked[9])
            Ece = np.append(Ece, unpacked[10])

            if self.is_VMP3:
                I_range = np.append(I_range, unpacked[11])
                
            # This is to convert the raw data into a Nyquist plot format and plot
            # if len(t) > 1:
            #     abs_Z_graph = np.divide(Ewe_bar[-1],I_bar[-1])
            #     Re_Z_graph = abs_Z_graph * (np.cos(Phase_zwe[-1]))
            #     Im_Z_graph = abs_Z_graph * (np.sin(Phase_zwe[-1]))
            #     Re_graph.append(Re_Z_graph)
            #     Im_graph.append(Im_Z_graph)
            #     plt.plot(Re_graph, -Im_graph)
            #     plt.xlabel('ReZ (ohm)')
            #     plt.ylabel('-Im(Z) (ohm)')
            #     plt.title('exp' + str(self.exp_num) + '_ch' + str(self.channel) + '_' + str(self.tech_num) + '_GEIS')
            #     plt.show()

            if status == 'STOP':
                techDone = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
                
                #Process the data to make arrays of Re(Z) and Im(Z)
                
                abs_Z = np.divide(Ewe_bar,I_bar)
                Re_Z = abs_Z * (np.cos(Phase_zwe))
                Im_Z = abs_Z * (np.sin(Phase_zwe))
                
                if self.is_VMP3:
                    full_data = pd.DataFrame(data=np.transpose([t, freq, Ewe_bar, I_bar, Phase_zwe, Ewe, I, Ece_bar,
                                                                Ice_bar, Phase_zce, Ece, I_range, abs_Z, Re_Z, Im_Z]),
                                             columns=['t(s)', 'freq(Hz)', 'Ewe_bar(V)', 'I_bar(A)', 'Phase_zwe',
                                                      'Ewe(V)', 'I(A)', 'Ece_bar(V)', 'Ice_bar(A)', 'Phase_zce',
                                                      'Ece(V)','I_range', 'abs_Z', 'Re_Z','Im_Z'])
                else:
                    full_data = pd.DataFrame(data=np.transpose([t, freq, Ewe_bar, I_bar, Phase_zwe, Ewe, I, Ece_bar,
                                                                Ice_bar, Phase_zce, Ece, abs_Z, Re_Z, Im_Z]),
                                             columns=['t(S)', 'freq(Hz)', 'Ewe_bar(V)', 'I_bar(A)', 'Phase_zwe',
                                                      'Ewe(V)', 'I(A)', 'Ece_bar(V)', 'Ice_bar(A)', 'Phase_zce',
                                                      'Ece(V)', 'abs_Z', 'Re_Z','Im_Z'])
                self.tech_num += 1
                filename = 'Test_' + str(self.exp_num) + '_ch' + str(self.channel) + '_GEIS_' + str(self.tech_num)+ '.csv'
                Meta = {'User': self.user, 'LabID': self.labID, 'Material Information': self.material_info, 'Device Type': self.device_info.model,
                        'Exp Start': self.expStart,
                        'Tech Start': techStart, 'Tech Done': techDone, 'Experiment num': self.exp_num,
                        'Technique': 'GEIS', 'Channel': self.channel}

                with open(self.data_save_sub + filename, 'w', newline="") as csv_file:
                    writer = csv.writer(csv_file, delimiter=',')
                    for key, value in Meta.items():
                        writer.writerow([key, value])
                    for key, value in Range.items():
                        writer.writerow([key, value])
                full_data.to_csv(self.data_save_sub + filename, header=True, index=None, sep=',', mode='a')
                break

            time.sleep(1)

        logging.info('Experiment expID: ' + str(self.exp_num) + ' Technique GEIS finished on channel ' + str(
            self.channel))  # log GEIS technique finished
        # print("> GEIS experiment done expID=", self.exp_num, " channel=", self.channel)
        return status

    def PEIS_run_tech(self, vs_initial, vs_final, initial_voltage_step, final_voltage_step, amplitude,
                      frequency_number, final_frequency, initial_frequency, duration_step,
                      step_number, record_every_dT, record_every_dI, sweep, average_n_times,
                      correction, wait_for_steady, I_range, E_range, bandwidth):

        """
        Args:
            vs_initial (bool): Whether the voltage step is vs. the initial one
            vs_final (bool): Whether the voltage step is vs. the final one
            initial_voltage_step (float): The initial voltage step (V)
            final_voltage_step (float): The final voltage step (V))
            amplitude (float): Amplitude of sine (V)
            frequency_number (int): The number of frequencies
            final_frequency (float): The final frequency (Hz)
            initial_frequency (float): The initial frequency (Hz)
            duration_step (float): Duration of step (s)
            step_number (int): The number of current steps (Number of steps minus 1)
            record_every_dT (float): Record every dT (s)
            record_every_dI (float): Record every dI (A)
            sweep (bool): Sweep linear/logarithmic (True for linear points spacing)
            average_n_times (int): The number of repeat times used for frequency averaging
            correction (bool): Non-stationary correction
            wait_for_steady (float): The number of periods to wait before each frequency
            I_range (str): A string describing the I range, see the kbio_types.py for possible values
            E_range (str): A string describing the E range to use, see the kbio_types.py for possible values
            bandwidth (str): A string describing the bandwidth setting, see the kbio_types.py for possible values
        """
        Range = {'vs_initial': vs_initial, 'vs_final': vs_final,
                 'initial_voltage_step': initial_voltage_step, 'final_voltage_step': final_voltage_step,
                 'amplitude': amplitude, 'frequency_number': frequency_number,
                 'final_frequency': final_frequency, 'initial_frequency': initial_frequency,
                 'duration_step': duration_step, 'step_number': step_number,
                 'record_every_dT': record_every_dT, 'record_every_dI': record_every_dI,
                 'sweep': sweep, 'average_n_times': average_n_times, 'correction': correction,
                 'wait_for_steady': wait_for_steady, 'I_range': I_range,
                 'E_range': E_range, 'bandwidth': bandwidth}
        channel_info = self.api.GetChannelInfo(self.id_, self.channel)  # BL_GetChannelInfos
        if not channel_info.is_kernel_loaded:
            print("> kernel must be loaded in order to run the experiment")
            sys.exit(-1)

        # PEIS parameter values based on the type of device
        peis3_tech_file = "peis.ecc"
        peis4_tech_file = "peis4.ecc"

        # pick the correct ecc file based on the instrument family
        tech_file = peis3_tech_file if self.is_VMP3 else peis4_tech_file

        # dictionary of PEIS parameters (non exhaustive)
        PEIS_parms = {
            'vs_initial': ECC_parm("vs_initial", bool),
            'vs_final': ECC_parm("vs_final", bool),
            'initial_voltage_step': ECC_parm("Initial_Voltage_step", float),
            'final_voltage_step': ECC_parm("Final_Voltage_step", float),
            'amplitude': ECC_parm("Amplitude_Voltage", float),
            'frequency_number': ECC_parm("Frequency_number", int),
            'final_frequency': ECC_parm("Final_frequency", float),
            'initial_frequency': ECC_parm("Initial_frequency", float),
            'duration_step': ECC_parm("Duration_step", float),
            'step_number': ECC_parm("Step_number", int),
            'record_every_dT': ECC_parm("Record_every_dT", float),
            'record_every_dI': ECC_parm("Record_every_dI", float),
            'sweep': ECC_parm("sweep", bool),
            'average_n_times': ECC_parm("Average_N_times", int),
            'correction': ECC_parm("Correction", bool),
            'wait_for_steady': ECC_parm("Wait_for_steady", float),
            'I_range': ECC_parm("I_Range", int),
            'E_range': ECC_parm("E_Range", int),
            'bandwidth': ECC_parm("Bandwidth", int),
        }

        # BL_Define<xxx>Parameter
        p_vs_initial = make_ecc_parm(self.api, PEIS_parms['vs_initial'], vs_initial)
        p_vs_final = make_ecc_parm(self.api, PEIS_parms['vs_final'], vs_final)
        p_initial_voltage_step = make_ecc_parm(self.api, PEIS_parms['initial_voltage_step'], initial_voltage_step)
        p_final_voltage_step = make_ecc_parm(self.api, PEIS_parms['final_voltage_step'], final_voltage_step)
        p_amplitude = make_ecc_parm(self.api, PEIS_parms['amplitude'], amplitude)
        p_frequency_number = make_ecc_parm(self.api, PEIS_parms['frequency_number'], frequency_number)
        p_final_frequency = make_ecc_parm(self.api, PEIS_parms['final_frequency'], final_frequency)
        p_initial_frequency = make_ecc_parm(self.api, PEIS_parms['initial_frequency'], initial_frequency)
        p_duration_step = make_ecc_parm(self.api, PEIS_parms['duration_step'], duration_step)
        p_step_number = make_ecc_parm(self.api, PEIS_parms['step_number'], step_number)
        p_record_every_dT = make_ecc_parm(self.api, PEIS_parms['record_every_dT'], record_every_dT)
        p_record_every_dI = make_ecc_parm(self.api, PEIS_parms['record_every_dI'], record_every_dI)
        p_sweep = make_ecc_parm(self.api, PEIS_parms['sweep'], sweep)
        p_average_n_times = make_ecc_parm(self.api, PEIS_parms['average_n_times'], average_n_times)
        p_correction = make_ecc_parm(self.api, PEIS_parms['correction'], correction)
        p_wait_for_steady = make_ecc_parm(self.api, PEIS_parms['wait_for_steady'], wait_for_steady)
        p_irange = make_ecc_parm(self.api, PEIS_parms['I_range'], KBIO.I_RANGE[I_range].value)
        p_erange = make_ecc_parm(self.api, PEIS_parms['E_range'], KBIO.E_RANGE[E_range].value)
        p_bandwidth = make_ecc_parm(self.api, PEIS_parms['bandwidth'], KBIO.BANDWIDTH[bandwidth].value)

        ecc_parms = make_ecc_parms(self.api, p_vs_initial, p_vs_final, p_initial_voltage_step, p_final_voltage_step,
                                   p_amplitude, p_frequency_number, p_final_frequency, p_initial_frequency,
                                   p_duration_step, p_step_number, p_record_every_dT, p_record_every_dI, p_sweep,
                                   p_average_n_times, p_correction, p_wait_for_steady, p_irange, p_erange,
                                   p_bandwidth)

        # BL_LoadTechnique
        self.api.LoadTechnique(self.id_, self.channel, tech_file, ecc_parms, first=True, last=True, display=False)
        techStart = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
        self.api.StartChannel(self.id_, self.channel)  # BL_StartChannel
        logging.info('Experiment expID: ' + str(self.exp_num) + ' Technique PEIS started on channel ' + str(
            self.channel))  # log PEIS technique started

        # experiment loop
        t = np.array([])
        freq = np.array([])
        Ewe_bar = np.array([])
        I_bar = np.array([])
        Phase_zwe = np.array([])
        Ewe = np.array([])
        I = np.array([])
        Ece_bar = np.array([])
        Ice_bar = np.array([])
        Phase_zce = np.array([])
        Ece = np.array([])
        I_range = np.array([])
        abs_Z = np.array([])
        Re_Z = np.array([])
        Im_Z = np.array([])
        
        Re_graph = []
        Im_graph = []
        abs_Z_graph = []
        Re_Z_graph = []
        Im_Z_graph = []
        
        while True:
            # BL_GetData
            data = self.api.GetData(self.id_, self.channel)
            status, unpacked = unpack_experiment_data(self.api, data, self.is_VMP3)

            t = np.append(t, unpacked[0])
            freq = np.append(freq, unpacked[1])
            Ewe_bar = np.append(Ewe_bar, unpacked[2])
            I_bar = np.append(I_bar, unpacked[3])
            Phase_zwe = np.append(Phase_zwe, unpacked[4])
            Ewe = np.append(Ewe, unpacked[5])
            I = np.append(I, unpacked[6])
            Ece_bar = np.append(Ece_bar, unpacked[7])
            Ice_bar = np.append(Ice_bar, unpacked[8])
            Phase_zce = np.append(Phase_zce, unpacked[9])
            Ece = np.append(Ece, unpacked[10])

            if self.is_VMP3:
                I_range = np.append(I_range, unpacked[11])
                
            # This is to convert the raw data into a Nyquist plot format and plot
            # if len(t) > 1:
            #     abs_Z_graph = np.divide(Ewe_bar[-1],I_bar[-1])
            #     Re_Z_graph = abs_Z_graph * (np.cos(Phase_zwe[-1]))
            #     Im_Z_graph = abs_Z_graph * (np.sin(Phase_zwe[-1]))
            #     Re_graph.append(Re_Z_graph)
            #     Im_graph.append(Im_Z_graph)
            #     plt.plot(Re_graph, -Im_graph)
            #     plt.xlabel('ReZ (ohm)')
            #     plt.ylabel('-Im(Z) (ohm)')
            #     plt.title('exp' + str(self.exp_num) + '_ch' + str(self.channel) + '_' + str(self.tech_num) + '_GEIS')
            #     plt.show()

            if status == 'STOP':
                techDone = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
                
                abs_Z = np.divide(Ewe_bar,I_bar)
                Re_Z = abs_Z * (np.cos(Phase_zwe))
                Im_Z = abs_Z * (np.sin(Phase_zwe))
                
                if self.is_VMP3:
                    full_data = pd.DataFrame(data=np.transpose([t, freq, Ewe_bar, I_bar, Phase_zwe, Ewe, I, Ece_bar,
                                                                Ice_bar, Phase_zce, Ece, I_range, abs_Z, Re_Z, Im_Z]),
                                             columns=['t(s)', 'freq(Hz)', 'Ewe_bar(V)', 'I_bar(A)', 'Phase_zwe',
                                                      'Ewe(V)', 'I(A)', 'Ece_bar(V)', 'Ice_bar(A)', 'Phase_zce',
                                                      'Ece(V)','I_range', 'abs_Z', 'Re_Z', 'Im_Z'])
                else:
                    full_data = pd.DataFrame(data=np.transpose([t, freq, Ewe_bar, I_bar, Phase_zwe, Ewe, I, Ece_bar,
                                                                Ice_bar, Phase_zce, Ece, abs_Z, Re_Z, Im_Z]),
                                             columns=['t(s)', 'freq(Hz)', 'Ewe_bar(V)', 'I_bar(A)', 'Phase_zwe',
                                                      'Ewe(V)', 'I(A)', 'Ece_bar(V)', 'Ice_bar(A)', 'Phase_zce',
                                                      'Ece(V)', 'abs_Z', 'Re_Z', 'Im_Z'])
                self.tech_num += 1
                filename = 'Test_' + str(self.exp_num) + '_ch' + str(self.channel) + '_PEIS_' + str(self.tech_num)+ '.csv'
                Meta = {'User': self.user, 'LabID': self.labID, 'Material Information': self.material_info, 'Device Type': self.device_info.model,
                        'Exp Start': self.expStart,
                        'Tech Start': techStart, 'Tech Done': techDone, 'Experiment num': self.exp_num,
                        'Technique': 'PEIS', 'Channel': self.channel}

                with open(self.data_save_sub + filename, 'w', newline="") as csv_file:
                    writer = csv.writer(csv_file, delimiter=',')
                    for key, value in Meta.items():
                        writer.writerow([key, value])
                    for key, value in Range.items():
                        writer.writerow([key, value])
                full_data.to_csv(self.data_save_sub + filename, header=True, index=None, sep=',', mode='a')
                break

            time.sleep(1)

        logging.info('Experiment expID: ' + str(self.exp_num) + ' Technique PEIS finished on channel ' + str(
            self.channel))  # log PEIS technique finished
        # print("> PEIS experiment done expID=", self.exp_num, " channel=", self.channel)
        return status
