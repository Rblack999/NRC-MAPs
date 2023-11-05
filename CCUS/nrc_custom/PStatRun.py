# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 15:34:39 2023

@author: nrc-eme-lab
"""
from nrc_custom.Connection import disconnect, connect
from nrc_custom.Techniques import Techniques
from threading import Thread
import threading
import json
import time
import numpy as np
import logging
import os
import sys
from datetime import date

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def decode_run(run, exp_num, channel, api, id_, device_info, user, labID, material_info, save_loc):
    global error_exp

    # decode the json file to run the specific techniques within an experiment

    logging.info('Experiment started for expID ' + str(exp_num))  # log experiment starting
    flag_read_params = 0  # if flag is 0 no exception occurred reading parameters, if flag is 1 an exception occurred

    # check that all the required parameters are defined before running the experiment
    # check that the correct type is defined for the individual parameters
    # NOT IMPLEMENTED: CHECK FOR CORRECT RANGE OF PARAMETERS
    for tech in run['Techniques']:
        params = tech['params']
        techID = tech['TechID']

        if techID == "OCV":
            try:
                if not isinstance(params["rest_time_T"], float) and not isfloat(params["rest_time_T"]):
                    flag_read_params = 1
                    logging.error('rest_time_T should be of type float for OCV technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["rest_time_T"])))
                if not isinstance(params["record_every_dE"], float) and not isfloat(params["record_every_dE"]):
                    flag_read_params = 1
                    logging.error(
                        'record_every_dE should be of type float for OCV technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["record_every_dE"])))
                if not isinstance(params["record_every_dT"], float) and not isfloat(params["record_every_dT"]):
                    flag_read_params = 1
                    logging.error(
                        'record_every_dT should be of type float for OCV technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["record_every_dT"])))
                if not isinstance(params["E_range"], str):
                    flag_read_params = 1
                    logging.error('E_range should be of type string for OCV technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["E_range"])))
            except Exception as e:
                flag_read_params = 1
                logging.error('Not all parameters have been defined for OCV technique for ExpID ' + str(
                    exp_num) + ' Channel ' + str(channel) + ' DETAILS: ' + str(e))

        if techID == "CV":
            try:
                if not all(isinstance(i, float) for i in params["voltage_step"]) and not all(
                        isfloat(i) for i in params["voltage_step"]):
                    flag_read_params = 1
                    logging.error(
                        'voltage_step should be of a list of floats for CV technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["voltage_step"])))
                if not all(isinstance(i, bool) for i in params["vs_initial"]):
                    flag_read_params = 1
                    logging.error(
                        'vs_initial should be of a list of booleans (true or false) for CV technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["vs_initial"])))
                if not all(isinstance(i, float) for i in params["scan_rate"]) and not all(
                        isfloat(i) for i in params["scan_rate"]):
                    flag_read_params = 1
                    logging.error('scan_rate should be of a list of floats for CV technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["scan_rate"])))
                if not isinstance(params["n_cycles"], int):
                    flag_read_params = 1
                    logging.error('n_cycles should be of type int for CV technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["n_cycles"])))
                if not isinstance(params["record_every_dE"], float) and not isfloat(params["record_every_dE"]):
                    flag_read_params = 1
                    logging.error('record_every_dE should be of type float for CV technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["record_every_dE"])))
                if not isinstance(params["scan_number"], int):
                    flag_read_params = 1
                    logging.error('scan_number should be of type int for CV technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["scan_number"])))
                if not isinstance(params["average_every_dE"], float) and not isfloat(params["average_every_dE"]):
                    flag_read_params = 1
                    logging.error(
                        'average_every_dE should be of type string (true or false) for CV technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["average_every_dE"])))
                if not isinstance(params["begin_measuring_I"], float) and not isfloat(params["begin_measuring_I"]):
                    flag_read_params = 1
                    logging.error(
                        'begin_measuring_I should be of type float for CV technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["begin_measuring_I"])))
                if not isinstance(params["end_measuring_I"], float) and not isfloat(params["end_measuring_I"]):
                    flag_read_params = 1
                    logging.error('end_measuring_I should be of type float for CV technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["end_measuring_I"])))
                if not isinstance(params["I_range"], str):
                    flag_read_params = 1
                    logging.error('I_range should be of type string for CV technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["I_range"])))
                if not isinstance(params["E_range"], str):
                    flag_read_params = 1
                    logging.error('E_range should be of type string for CV technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["E_range"])))
                if not isinstance(params["bandwidth"], str):
                    flag_read_params = 1
                    logging.error('bandwidth should be of type string for CV technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["bandwidth"])))
                if not len(params["voltage_step"]) == len(params["vs_initial"]) == len(params["scan_rate"]):
                    flag_read_params = 1
                    logging.error('The length of voltage_step, vs_initial and scan_rate must be the same and have '
                                    'length = 5 for CV technique for ExpID ' + str(exp_num) + ' Channel '
                                    + str(channel))
            except Exception as e:
                flag_read_params = 1
                logging.error('Not all parameters have been defined for CV technique for ExpID ' + str(
                    exp_num) + ' Channel ' + str(channel) + ' DETAILS: ' + str(e))

        if techID == "CP":
            try:
                if not all(isinstance(i, float) for i in params["current_step"]) and not all(
                        isfloat(i) for i in params["current_step"]):
                    flag_read_params = 1
                    logging.error(
                        'current_step should be of a list of floats for CP technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["current_step"])))
                if not all(isinstance(i, bool) for i in params["vs_initial"]):
                    flag_read_params = 1
                    logging.error(
                        'vs_initial should be of a list of booleans (true or false) for CP technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["vs_initial"])))
                if not all(isinstance(i, float) for i in params["duration_step"]) and not all(
                        isfloat(i) for i in params["duration_step"]):
                    flag_read_params = 1
                    logging.error(
                        'duration_step should be of a list of floats for CP technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["duration_step"])))
                if not isinstance(params["n_cycles"], int):
                    flag_read_params = 1
                    logging.error('n_cycles should be of type int for CP technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["n_cycles"])))
                if not isinstance(params["record_every_dE"], float) and not all(
                        isfloat(i) for i in params["record_every_dE"]):
                    flag_read_params = 1
                    logging.error('record_every_dE should be of type float for CP technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["record_every_dE"])))
                if not isinstance(params["record_every_dt"], float) and not all(
                        isfloat(i) for i in params["record_every_dt"]):
                    flag_read_params = 1
                    logging.error('record_every_dt should be of type float for CP technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["record_every_dt"])))
                if not isinstance(params["I_range"], str):
                    flag_read_params = 1
                    logging.error('I_range should be of type string for CP technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["I_range"])))
                if not isinstance(params["E_range"], str):
                    flag_read_params = 1
                    logging.error('E_range should be of type string for CP technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["E_range"])))
                if not isinstance(params["bandwidth"], str):
                    flag_read_params = 1
                    logging.error('bandwidth should be of type string for CP technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["bandwidth"])))
                if not len(params["current_step"]) == len(params["vs_initial"]) == len(params["duration_step"]):
                    flag_read_params = 1
                    logging.error('The length of current_step, vs_initial and duration_step must be the same for '
                                    'CP technique for ExpID ' + str(exp_num) + ' Channel '
                                    + str(channel))
            except Exception as e:
                flag_read_params = 1
                logging.error('Not all parameters have been defined for CP technique for ExpID ' + str(
                    exp_num) + ' Channel ' + str(channel) + ' DETAILS: ' + str(e))

        if techID == "CA":
            try:
                if not all(isinstance(i, float) for i in params["voltage_step"]) and not all(
                        isfloat(i) for i in params["voltage_step"]):
                    flag_read_params = 1
                    logging.error(
                        'voltage_step should be of a list of floats for CA technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["voltage_step"])))
                if not all(isinstance(i, bool) for i in params["vs_initial"]):
                    flag_read_params = 1
                    logging.error(
                        'vs_initial should be of a list of booleans (true or false) for CA technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["vs_initial"])))
                if not all(isinstance(i, float) for i in params["duration_step"]) and not all(
                        isfloat(i) for i in params["duration_step"]):
                    flag_read_params = 1
                    logging.error(
                        'duration_step should be of a list of floats for CA technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["duration_step"])))
                if not isinstance(params["n_cycles"], int):
                    flag_read_params = 1
                    logging.error('n_cycles should be of type int for CA technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["n_cycles"])))
                if not isinstance(params["record_every_di"], float) and not isfloat(params["record_every_di"]):
                    flag_read_params = 1
                    logging.error('record_every_di should be of type float for CA technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["record_every_di"])))
                if not isinstance(params["record_every_dt"], float) and not isfloat(params["record_every_dt"]):
                    flag_read_params = 1
                    logging.error('record_every_dt should be of type float for CA technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["record_every_dt"])))
                if not isinstance(params["I_range"], str):
                    flag_read_params = 1
                    logging.error('I_range should be of type string for CA technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["I_range"])))
                if not isinstance(params["E_range"], str):
                    flag_read_params = 1
                    logging.error('E_range should be of type string for CA technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["E_range"])))
                if not isinstance(params["bandwidth"], str):
                    flag_read_params = 1
                    logging.error('bandwidth should be of type string for CA technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["bandwidth"])))
                if not len(params["voltage_step"]) == len(params["vs_initial"]) == len(params["duration_step"]):
                    flag_read_params = 1
                    logging.error('The length of voltage_step, vs_initial and duration_step must be the same for '
                                    'CA technique for ExpID ' + str(exp_num) + ' Channel '
                                    + str(channel))
            except Exception as e:
                flag_read_params = 1
                logging.error('Not all parameters have been defined for CA technique for ExpID ' + str(
                    exp_num) + ' Channel ' + str(channel) + ' DETAILS: ' + str(e))

        if techID == "GEIS":
            try:
                if not isinstance(params["vs_initial"], bool):
                    flag_read_params = 1
                    logging.error(
                        'vs_initial should be of type boolean (true or false) for GEIS technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["vs_initial"])))
                if not isinstance(params["vs_final"], bool):
                    flag_read_params = 1
                    logging.error(
                        'vs_final should be of type boolean (true or false) for GEIS technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["vs_final"])))
                if not isinstance(params["initial_current_step"], float) and not isfloat(
                        params["initial_current_step"]):
                    flag_read_params = 1
                    logging.error(
                        'initial_current_step should be of type float for GEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["initial_current_step"])))
                if not isinstance(params["final_current_step"], float) and not isfloat(params["final_current_step"]):
                    flag_read_params = 1
                    logging.error(
                        'final_current_step should be of type float for GEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["final_current_step"])))
                if not isinstance(params["amplitude"], float) and not isfloat(params["amplitude"]):
                    flag_read_params = 1
                    logging.error('amplitude should be of type float for GEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["amplitude"])))
                if not isinstance(params["frequency_number"], int):
                    flag_read_params = 1
                    logging.error(
                        'frequency_number should be of type int for GEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["frequency_number"])))
                if not isinstance(params["final_frequency"], float) and not isfloat(params["final_frequency"]):
                    flag_read_params = 1
                    logging.error(
                        'final_frequency should be of type float for GEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["final_frequency"])))
                if not isinstance(params["initial_frequency"], float) and not isfloat(params["initial_frequency"]):
                    flag_read_params = 1
                    logging.error(
                        'initial_frequency should be of type float for GEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["initial_frequency"])))
                if not isinstance(params["duration_step"], float) and not isfloat(params["duration_step"]):
                    flag_read_params = 1
                    logging.error('duration_step should be of type float for GEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["duration_step"])))
                if not isinstance(params["step_number"], int):
                    flag_read_params = 1
                    logging.error('step_number should be of type int for GEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["step_number"])))
                if not isinstance(params["record_every_dT"], float) and not isfloat(params["record_every_dT"]):
                    flag_read_params = 1
                    logging.error(
                        'record_every_dT should be of type float for GEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["record_every_dT"])))
                if not isinstance(params["record_every_dE"], float) and not isfloat(params["record_every_dE"]):
                    flag_read_params = 1
                    logging.error(
                        'record_every_dE should be of type float for GEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["record_every_dE"])))
                if not isinstance(params["sweep"], bool):
                    flag_read_params = 1
                    logging.error(
                        'sweep should be of type boolean (true or false) for GEIS technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["sweep"])))
                if not isinstance(params["average_n_times"], int):
                    flag_read_params = 1
                    logging.error('average_n_times should be of type int for GEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["average_n_times"])))
                if not isinstance(params["correction"], bool):
                    flag_read_params = 1
                    logging.error(
                        'correction should be of type boolean (true or false) for GEIS technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["correction"])))
                if not isinstance(params["wait_for_steady"], float) and not isfloat(params["wait_for_steady"]):
                    flag_read_params = 1
                    logging.error(
                        'wait_for_steady should be of type string (true or false) for GEIS technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["wait_for_steady"])))
                if not isinstance(params["I_range"], str):
                    flag_read_params = 1
                    logging.error('I_range should be of type string for GEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["I_range"])))
                if not isinstance(params["E_range"], str):
                    flag_read_params = 1
                    logging.error('E_range should be of type string for GEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["E_range"])))
                if not isinstance(params["bandwidth"], str):
                    flag_read_params = 1
                    logging.error('bandwidth should be of type string for GEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["bandwidth"])))
            except Exception as e:
                flag_read_params = 1
                logging.error('Not all parameters have been defined for GEIS technique for ExpID ' + str(
                    exp_num) + ' Channel ' + str(channel) + ' DETAILS: ' + str(e))

        if techID == "PEIS":
            try:
                if not isinstance(params["vs_initial"], bool):
                    flag_read_params = 1
                    logging.error(
                        'vs_initial should be of type boolean (true or false) for PEIS technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["vs_initial"])))
                if not isinstance(params["vs_final"], bool):
                    flag_read_params = 1
                    logging.error(
                        'vs_final should be of type boolean (true or false) for PEIS technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["vs_final"])))
                if not isinstance(params["initial_voltage_step"], float) and not isfloat(
                        params["initial_voltage_step"]):
                    flag_read_params = 1
                    logging.error(
                        'initial_voltage_step should be of type float for PEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["initial_voltage_step"])))
                if not isinstance(params["final_voltage_step"], float) and not isfloat(params["final_voltage_step"]):
                    flag_read_params = 1
                    logging.error(
                        'final_voltage_step should be of type float for PEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["final_voltage_step"])))
                if not isinstance(params["amplitude"], float) and not isfloat(params["amplitude"]):
                    flag_read_params = 1
                    logging.error('amplitude should be of type float for PEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["amplitude"])))
                if not isinstance(params["frequency_number"], int):
                    flag_read_params = 1
                    logging.error(
                        'frequency_number should be of type int for PEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["frequency_number"])))
                if not isinstance(params["final_frequency"], float) and not isfloat(params["final_frequency"]):
                    flag_read_params = 1
                    logging.error(
                        'final_frequency should be of type float for PEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["final_frequency"])))
                if not isinstance(params["initial_frequency"], float) and not isfloat(params["initial_frequency"]):
                    flag_read_params = 1
                    logging.error(
                        'initial_frequency should be of type float for PEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["initial_frequency"])))
                if not isinstance(params["duration_step"], float) and not isfloat(params["duration_step"]):
                    flag_read_params = 1
                    logging.error('duration_step should be of type float for PEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["duration_step"])))
                if not isinstance(params["step_number"], int):
                    flag_read_params = 1
                    logging.error('step_number should be of type int for PEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["step_number"])))
                if not isinstance(params["record_every_dT"], float) and not isfloat(params["record_every_dT"]):
                    flag_read_params = 1
                    logging.error(
                        'record_every_dT should be of type float for PEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["record_every_dT"])))
                if not isinstance(params["record_every_dI"], float) and not isfloat(params["record_every_dI"]):
                    flag_read_params = 1
                    logging.error(
                        'record_every_dI should be of type float for PEIS technique for ExpID ' + str(exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["record_every_dI"])))
                if not isinstance(params["sweep"], bool):
                    flag_read_params = 1
                    logging.error(
                        'sweep should be of type boolean (true or false) for PEIS technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["sweep"])))
                if not isinstance(params["average_n_times"], int):
                    flag_read_params = 1
                    logging.error('average_n_times should be of type int for PEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["average_n_times"])))
                if not isinstance(params["correction"], bool):
                    flag_read_params = 1
                    logging.error(
                        'correction should be of type boolean (true or false) for PEIS technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["correction"])))
                if not isinstance(params["wait_for_steady"], float) and not isfloat(params["wait_for_steady"]):
                    flag_read_params = 1
                    logging.error(
                        'wait_for_steady should be of type string (true or false) for PEIS technique for ExpID ' + str(
                            exp_num)
                        + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                        + str(type(params["wait_for_steady"])))
                if not isinstance(params["I_range"], str):
                    flag_read_params = 1
                    logging.error('I_range should be of type string for PEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["I_range"])))
                if not isinstance(params["E_range"], str):
                    flag_read_params = 1
                    logging.error('E_range should be of type string for PEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["E_range"])))
                if not isinstance(params["bandwidth"], str):
                    flag_read_params = 1
                    logging.error('bandwidth should be of type string for PEIS technique for ExpID ' + str(exp_num)
                                    + ' Channel ' + str(channel) + ' DETAILS: current value is of type'
                                    + str(type(params["bandwidth"])))
            except Exception as e:
                flag_read_params = 1
                logging.error('Not all parameters have been defined for PEIS technique for ExpID ' + str(
                    exp_num) + ' Channel ' + str(channel) + ' DETAILS: ' + str(e))

    # if flag_read_params == 1:
    #     error_exp = np.append(error_exp, exp_num)

    flag_run_exp = 0  # if flag is 0 no exception occurred running techniques in experiment,
    # if flag is 1 an exception occurred

    if flag_read_params == 0:  # if all variables are defined and no exceptions occurred, run the experiment
        # create an object for the specific channel and experiment
        ch_ob = Techniques(exp_num, channel, api, id_, device_info, user, labID, material_info, save_loc)

        for tech in run['Techniques']:
            params = tech['params']
            techID = tech['TechID']

            if flag_run_exp == 0:

                if techID == "OCV":
                    rest_time_T_ocv = params["rest_time_T"]
                    record_every_dE_ocv = params["record_every_dE"]
                    record_every_dT_ocv = params["record_every_dT"]
                    E_range_ocv = params["E_range"]
                    try:
                        ch_ob.OCV_run_tech(rest_time_T_ocv, record_every_dE_ocv, record_every_dT_ocv, E_range_ocv)
                    except Exception as e:
                        logging.error('Error occurred in expID ' + str(exp_num) + ' Channel ' + str(
                            channel) + ' for technique OCV. DETAILS: ' + str(e))
                        flag_run_exp = 1

                if techID == "CV":
                    vs_initial_cv = params["vs_initial"]
                    voltage_step_cv = params["voltage_step"]
                    scan_rate_cv = params["scan_rate"]
                    record_every_dE_cv = params["record_every_dE"]
                    scan_number_cv = params["scan_number"]
                    average_every_dE_cv = params["average_every_dE"]
                    n_cycles_cv = params["n_cycles"]
                    begin_measuring_I_cv = params["begin_measuring_I"]
                    end_measuring_I_cv = params["end_measuring_I"]
                    I_range_cv = params["I_range"]
                    E_range_cv = params["E_range"]
                    bandwidth_cv = params["bandwidth"]
                    try:
                        ch_ob.CV_run_tech(vs_initial_cv, voltage_step_cv, scan_rate_cv, record_every_dE_cv,
                                          scan_number_cv,
                                          average_every_dE_cv, n_cycles_cv, begin_measuring_I_cv, end_measuring_I_cv,
                                          I_range_cv, E_range_cv, bandwidth_cv)
                    except Exception as e:
                        logging.error('Error occurred in expID ' + str(exp_num) + ' Channel ' + str(channel)
                                        + ' for technique CV. DETAILS: ' + str(e))
                        flag_run_exp = 1

                if techID == "CP":
                    current_step_cp = params["current_step"]
                    vs_initial_cp = params["vs_initial"]
                    duration_step_cp = params["duration_step"]
                    n_cycles_cp = params["n_cycles"]
                    record_every_dE_cp = params["record_every_dE"]
                    record_every_dt_cp = params["record_every_dt"]
                    I_range_cp = params["I_range"]
                    E_range_cp = params["E_range"]
                    bandwidth_cp = params["bandwidth"]
                    try:
                        ch_ob.CP_run_tech(current_step_cp, vs_initial_cp, duration_step_cp, n_cycles_cp,
                                          record_every_dE_cp,
                                          record_every_dt_cp, I_range_cp, E_range_cp, bandwidth_cp)
                    except Exception as e:
                        logging.error('Error occurred in expID ' + str(exp_num) + ' Channel ' + str(channel)
                                        + ' for technique CP. DETAILS: ' + str(e))
                        flag_run_exp = 1

                if techID == "CA":
                    voltage_step_ca = params["voltage_step"]
                    vs_initial_ca = params["vs_initial"]
                    duration_step_ca = params["duration_step"]
                    n_cycles_ca = params["n_cycles"]
                    record_every_di_ca = params["record_every_di"]
                    record_every_dt_ca = params["record_every_dt"]
                    I_range_ca = params["I_range"]
                    E_range_ca = params["E_range"]
                    bandwidth_ca = params["bandwidth"]
                    try:
                        ch_ob.CA_run_tech(voltage_step_ca, vs_initial_ca, duration_step_ca, n_cycles_ca,
                                          record_every_di_ca,
                                          record_every_dt_ca, I_range_ca, E_range_ca, bandwidth_ca)
                    except Exception as e:
                        logging.error('Error occurred in expID ' + str(exp_num) + ' Channel ' + str(channel)
                                        + ' for technique CA. DETAILS: ' + str(e))
                        flag_run_exp = 1

                if techID == "GEIS":
                    vs_initial_geis = params["vs_initial"]
                    vs_final_geis = params["vs_final"]
                    initial_current_step_geis = params["initial_current_step"]
                    final_current_step_geis = params["final_current_step"]
                    amplitude_geis = params["amplitude"]
                    frequency_number_geis = params["frequency_number"]
                    final_frequency_geis = params["final_frequency"]
                    initial_frequency_geis = params["initial_frequency"]
                    duration_step_geis = params["duration_step"]
                    step_number_geis = params["step_number"]
                    record_every_dT_geis = params["record_every_dT"]
                    record_every_dE_geis = params["record_every_dE"]
                    sweep_geis = params["sweep"]
                    average_n_times_geis = params["average_n_times"]
                    correction_geis = params["correction"]
                    wait_for_steady_geis = params["wait_for_steady"]
                    I_range_geis = params["I_range"]
                    E_range_geis = params["E_range"]
                    bandwidth_geis = params["bandwidth"]

                    try:
                        ch_ob.GEIS_run_tech(vs_initial_geis, vs_final_geis, initial_current_step_geis,
                                            final_current_step_geis, amplitude_geis, frequency_number_geis,
                                            final_frequency_geis, initial_frequency_geis,
                                            duration_step_geis, step_number_geis, record_every_dT_geis,
                                            record_every_dE_geis, sweep_geis, average_n_times_geis,
                                            correction_geis, wait_for_steady_geis, I_range_geis, E_range_geis,
                                            bandwidth_geis)
                    except Exception as e:
                        logging.error('Error occurred in expID ' + str(exp_num) + ' Channel ' + str(channel)
                                        + ' for technique GEIS. DETAILS: ' + str(e))
                        flag_run_exp = 1

                if techID == "PEIS":
                    vs_initial_peis = params["vs_initial"]
                    vs_final_peis = params["vs_final"]
                    initial_voltage_step_peis = params["initial_voltage_step"]
                    final_voltage_step_peis = params["final_voltage_step"]
                    amplitude_peis = params["amplitude"]
                    frequency_number_peis = params["frequency_number"]
                    final_frequency_peis = params["final_frequency"]
                    initial_frequency_peis = params["initial_frequency"]
                    duration_step_peis = params["duration_step"]
                    step_number_peis = params["step_number"]
                    record_every_dT_peis = params["record_every_dT"]
                    record_every_dI_peis = params["record_every_dI"]
                    sweep_peis = params["sweep"]
                    average_n_times_peis = params["average_n_times"]
                    correction_peis = params["correction"]
                    wait_for_steady_peis = params["wait_for_steady"]
                    I_range_peis = params["I_range"]
                    E_range_peis = params["E_range"]
                    bandwidth_peis = params["bandwidth"]
                    try:
                        ch_ob.PEIS_run_tech(vs_initial_peis, vs_final_peis, initial_voltage_step_peis,
                                            final_voltage_step_peis, amplitude_peis, frequency_number_peis,
                                            final_frequency_peis, initial_frequency_peis, duration_step_peis,
                                            step_number_peis, record_every_dT_peis, record_every_dI_peis, sweep_peis,
                                            average_n_times_peis, correction_peis, wait_for_steady_peis, I_range_peis,
                                            E_range_peis, bandwidth_peis)
                    except Exception as e:
                        logging.error('Error occurred in expID ' + str(exp_num) + ' Channel ' + str(channel)
                                        + ' for technique PEIS. DETAILS: ' + str(e))
                        flag_run_exp = 1

    if flag_run_exp == 0 and flag_read_params == 0:
        logging.info('Experiment ended with no errors for expID ' + str(exp_num))  # log experiment ending
    else:
        error_exp = np.append(error_exp, exp_num)
        logging.error('Experiment ended with errors for expID ' + str(exp_num))

def pstat_run(experiment_name, input_procedure):
    
    valid_inputs = ['depo', 'char', 'perf', 'custom'] # Only possible inputs that can be used
    
    if input_procedure not in valid_inputs:
        raise ValueError(f'Invalid input: {input_procedure}. Accepted values are {valid_inputs}')
    
    if input_procedure in ['depo', 'char', 'perf','custom']:
        pstat_procedure = f'master_runs_{input_procedure}.json'
    else:
        raise ValueError(f"Invalid input_procedure: {input_procedure}")
    
    logging_file = 'potentiostat_log.log'  # define logging file to be used for the program running
    logging.basicConfig(filename=logging_file, level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')
    # encoding = 'utf-8',

    address = "USB0"  # address of the device in use
    binary_path =  'C:/Users/Blackr/Desktop/Automation/MultiChannel-Potentiostat-Management-Software/EC_Lab_Development_Package_2022/EC-Lab Development Package/'  # address for dev package
    api, id_, device_info = connect(address, binary_path)  # connect to the device
    
    # The following folder will be the same folder as the .pkl file created during the workflow
    # date_format = date.today().strftime("%Y_%m_%d") # https://www.programiz.com/python-programming/datetime/current-datetime
    save_loc = f'C:/Users/Blackr/Desktop/Automation/Campaigns/{experiment_name}/' # main folder where the data will be saved
    if not os.path.exists(save_loc): # Check if folder exists - if not, make it, else use existing folder
        os.makedirs(save_loc)
    
    # Below is the old save location - keep around for now
    # save_loc = "C:\\Users\\nrc-eme-lab\\Desktop\\Automation\MultiChannel-Potentiostat-Management-Software\\Development_Test\\"  
    # main folder where the data will be saved and where master_runs.json and new_run folder are housed
    # Note: subfolders for the individual experiments will be created within the folder defined at save_loc
    new_runs = 'C:/Users/Blackr/Desktop/Automation/MultiChannel-Potentiostat-Management-Software/Development_Test/New_Runs/' 
    # this is where the user places new json files with experiments to run while the program is running 

    sleep_time = 5  # check for new json file experiments every sleep_time seconds

    # /////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    active_channels = np.array([])  # track channels that are currently in use for the device
    global active_threads
    active_threads = np.array([])  # track threads that are active and running
    experiments_run = np.array([])  # keep a list of all the experiments run during the session
    added_runs = np.chararray(
        [])  # keep track of the names of the runs that have been added to not have a duplicate run
    global error_exp
    error_exp = np.array([])  # keep track of experiments that gave errors
    loop = True  # boolean used to control while loop
    global stop  # used to end the entire program
    stop = 0

    #RB added the following:
    original_threads = print(f'Active thread count = {threading.active_count()}') # Get the number of original threads running in the background
    # Want to use this to ensure the potentiostat starts threading at the right thread location/spot
    while loop:
        try:
            with open(save_loc + pstat_procedure, 'r') as ms:  # load pstat procedure json file
                master_runs = json.loads(ms.read())  # Reading from file

            for run in master_runs['Runs']:  # loop through experiment entries in the file
                status = run['status']  # status of experiment (incomplete, running, complete, error)
                channel = run['channel']  # channel on which the experiment is meant to be run
                exp_num = run['expID']  # experiment number
                user = run['user']  # lab user
                labID = run['labID']  # lab ID
                material_info = run['material_info']  # information about the material

                if status == 'incomplete':  # check that the experiment has not been run
                    if channel not in active_channels:  # check that the channel is not in use
                        run['status'] = 'running'  # update the status for the experiment
                        experiments_run = np.append(experiments_run, exp_num)
                        exp = Thread(target=decode_run, name=str(channel) + str(exp_num),
                                     args=(run, exp_num, channel, api, id_,
                                           device_info, user, labID, material_info, save_loc,))
                        exp.start()  # start thread
                        print(exp)
                # if status == 'running':
                #     do nothing
                # if status == 'error':
                #     do nothing
                # if status == 'complete':  # will log completion
                #     print('Experiment run: ', exp_num)

                # update active channels and threads
                main_thread = threading.current_thread() #RB get confused here, what does this do??
                print("Active current thread right now:", (threading.current_thread()))
                active_threads = np.array([])
                active_channels = np.array([])
                print(f'thread active count = {threading.active_count()}')
                for t in threading.enumerate(): #where t is the index of enumerate # This seems to not enumerate over the actual exp thread but all thread
                    if t is exp:
                        print(f'In the loop {t.getName()}')
                        active_threads = np.append(active_threads, (t.getName()))
                        active_channels = np.append(active_channels, int((t.getName())[0])) #Original from Isabelle
                    else:
                        continue # Note this skips over the case of t = another thread and goes through the loop without doing anything
                print(t.getName())
                # modify active threads to show the experiment number only

                #RB added - this gave me a lot of problems. Previous issue - the original code would have status = complete after one loop, regardless of real status
                #This was due to the active_thread being empty after one loop, and I believe line 774 (t is exp) not working correctly after one loop giving the problem
                #As such, t is still active during the live thread (aka the potentiostat is running), so I updated to use that to update mod_active_thread --> int(t.getName()[1:])
                #however, that only worked until the thread ended, at which point the master thread would take over, called 'Thread-4', and the program shut down due to an int('Thread-4') issue
                #This is why I added the if statement:t.getName()[1] == '1':, to check if the t.getName() was a number or not. If so, correct thread, keep going. If not, empty
                #the array so that the status == complete and will stop according to the stop_program function 
                
                mod_active_threads = np.array([])
                if t.getName()[1].isdigit(): #t.getName is in the form name=str(channel) + str(exp_num), so index [1] should always be a digit (ie. 0-9)
                    mod_active_threads = np.append(mod_active_threads, int(t.getName()[1:])) #RB added this
                else:
                    mod_active_threads = np.array([])
                # for thread in active_threads: *This and line below were in the original, which caused errors as it would disappear after one loop and cause ['status'] to shift to complete prematurely
                #     mod_active_threads = np.append(mod_active_threads, int(thread[1:])) 
                print(f'this is the mod_active threads {mod_active_threads}')

                # update status for experiments that no longer have active threads
                # update status for experiments that have an error
                
                for exp in experiments_run:
                    if not (exp in mod_active_threads):
                        # change the specific master runs at expID, status is complete
                        for run in master_runs['Runs']:
                            if run['expID'] == exp:
                                run['status'] = 'complete'
                    if exp in error_exp:
                        # change the specific master runs at expID, status is complete
                        for run in master_runs['Runs']:
                            if run['expID'] == exp:
                                run['status'] = 'error'

            print('Active Channels (channels with experiment running)', active_channels)
            print('Active Threads (naming is channel_expID)', active_threads)
            print('Experiments that have been started', experiments_run)
            print('Error has occurred in these experiments', error_exp, '\n')

            # check for a new addition to the runs
            for filename in os.listdir(new_runs):  # iterate over the files in new_runs
                if filename not in added_runs:  # check if the file has already been added
                    added_runs = np.append(added_runs, filename)  # add file to the added_runs array to ensure the file
                    # is not read again in the next loop
                    f = os.path.join(new_runs, filename)  # concatenate the paths
                    if os.path.isfile(f):  # confirm the specified path exists
                        try:  # try opening the files and reading them
                            with open(f, 'r') as new:  # load json file
                                new_run = json.loads(new.read())  # Reading from file
                            for new in new_run['Runs']:  # loop through experiment entries in the file
                                master_runs['Runs'].append(new)
                        except Exception as e:  # except all error pertaining to the file and log the error
                            logging.error('Error loading JSON file at ' + str(f) +
                                          + ' DETAILS: ' + str(e))

            print(f'Current status = {status}') # print the status of the run, defined as part of the for loop ~100 lines up, as an active check for user during live operation
            # update json file (specifically new_runs added and status needs to be updated -> incomplete to running to
            # complete (potentially error))
            with open(save_loc + pstat_procedure, 'w') as f:
                json.dump(master_runs, f)
            time.sleep(sleep_time)

            #Defining a stoping function:            
            def stop_program():
                global stop
                global active_threads
            
                with open(save_loc + pstat_procedure, 'r') as ms:  # load json file
                    master_runs = json.loads(ms.read())  # Reading from file
            
                status_check = np.array([])
            
                for run in master_runs['Runs']:  # loop through experiment entries in the file
                    status = run['status']  # status of experiment (incomplete, running, complete, error)
                    if status == 'complete' or status == 'error':
                        status_check = np.append(status_check, 1)
                    else:
                        status_check = np.append(status_check, 0)
            
                print(f'status_check = {status_check}')
                
                if np.array_equal(status_check, [1 for _ in range(len(status_check))]):  # status of exp all complete or error
                    stop += 1
                else:
                    stop = 0  # reset as there were not consecutive trials where status was error or complete
            
                if stop == 3 and not np.any(active_threads):
                    return False  # this will end the while loop in main
                else:
                    return True

            loop = stop_program()  # check whether the program can stop

        except Exception as e:  # except all errors and log
            print('Error occurred. DETAILS: ' + str(e))
            logging.error('Error occurred. DETAILS: ' + str(e))
            sys.exit()  # exit if the main JSON is not correct

    disconnect(address, api, id_)  # disconnect the device

