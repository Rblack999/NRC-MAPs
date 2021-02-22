# -*- coding: utf-8 -*-
"""
@author: Blackr
"""
"""Chrono-Amperometry (CA) technique class.

 The CA technique returns data on fields (in order):

 * time (float)
 * Ewe (float)
 * I (float)
 * cycle (int)
 """
'''NOTE: The voltage_step, vs_initial and duration_step must be a list or
        tuple with the same length.

        Args:
            voltage_step (list): List (or tuple) of floats indicating the
                voltage steps (A). See NOTE above.
            vs_initial (list): List (or tuple) of booleans indicating whether
                the current steps is vs. the initial one. See NOTE above.
            duration_step (list): List (or tuple) of floats indicating the
                duration of each step (s). See NOTE above.
            record_every_dT (float): Record every dT (s)
            record_every_dI (float): Record every dI (A)
            N_cycles (int): The number of times the technique is REPEATED.
                NOTE: This means that the default value is 0 which means that
                the technique will be run once.
            I_Range (str): A string describing the I range, see the
                :data:`I_RANGES` module variable for possible values
            E_range (str): A string describing the E range to use, see the
                :data:`E_RANGES` module variable for possible values
            Bandwidth (str): A string describing the bandwidth setting, see the
                :data:`BANDWIDTHS` module variable for possible values''''''

"""CA example"""'''
'''A program to run a typical CA experiment and export the data to a .csv file'''
'''Currently have 32-bit vs. 64-bit interpreter problems with pandas library, so dump to .csv and use other to put into pandas database'''
import time
import numpy
import json
from bio_logic import SP150, CA

def run_ca():
    """Test the CA technique"""
    ip_address = 'USB0'  # REPLACE THIS WITH A VALID IP
    # Instantiate the instrument and connect to it
    sp150 = SP150(ip_address, 'C:\\EC-Lab Development Package\\EC-Lab Development Package\\EClib.dll')
    sp150.connect()
    sp150.load_firmware([1])
    # Instantiate the technique. Make sure to give values for all the
    # arguments where the default values does not fit your purpose. The
    # default values can be viewed in the API documentation for the
    # technique.
    ca = CA(voltage_step = ([0.2,1.1,0.6]), vs_initial = ([False,False,False]),
                 duration_step = ([2,2,2]),
                 record_every_dT = 0.1, record_every_dI = 5E-3,
                 N_cycles = 0, I_range = 'KBIO_IRANGE_AUTO',
                 E_range = 'KBIO_ERANGE_2_5', bandwidth = 'KBIO_BW_5'
              )

    # Load the technique onto channel 0 of the potentiostat and start it
    sp150.load_technique(0, ca)
    sp150.start_channel(0)

    #Creating blank numpy arrays to populate with .append for each data point
    Time = numpy.array([])
    Ewe = numpy.array([])
    I = numpy.array([])
    cycle = numpy.array([])
    while True:
        # Get the currently available data on channel 0 (only what has
        # been gathered since last get_data)
        data_out = sp150.get_data(0)

        # If there is none, assume the technique has finished
        if data_out is None:
            break

        # The data is available in lists as attributes on the data
        # object. The available data fields are listed in the API
        # documentation for the technique.
        # If numpy is installed, the data can also be retrieved as
        # numpy arrays
        # printing the values to follow for testing purposes only
        #print('Time:', data_out.time_numpy)
        #print('Ewe:', data_out.Ewe_numpy)
        #print('I', data_out.I_numpy)
        #print('cycle', data_out.cycle_numpy)

        # Updating the variables with the appended data per data call
        Ewe = numpy.append(Ewe, data_out.Ewe_numpy_numpy)
        Time = numpy.append(Time, data_out.time_numpy)
        I = numpy.append(I, data_out.I_numpy)
        cycle = numpy.append(cycle, data_out.cycle_numpy)

    #Below are two methods of saving the output data
    #First method is saving the data as columns in a .csv file
    df = (Time, Ewe, I, cycle)
    numpy.savetxt("SP150_CA_Main.csv", numpy.transpose(df), delimiter=",", header = 'Time,Ewe,I,cycle', comments = '')

    #The second method is saving the data as a .json file
    data = {'Time':Time.tolist(),'Ewe':Ewe.tolist(),'I':I.tolist(),'cycle':cycle.tolist()}
    with open('SP150_CA_Main.json', 'w') as json_file:
        json.dump(data, json_file)

    print(data)

    sp150.stop_channel(0)
    sp150.disconnect()

if __name__ == '__main__':
    run_ca()
