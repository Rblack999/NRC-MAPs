# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 12:43:51 2019

@author: Blackr
"""
"""Cyclic Voltammetry (CV) technique class.

The CV technique returns data on fields (in order):

* time (float)
* Ec (float)
* I (float)
* Ewe (float)
* cycle (int)
"""
''' E_we
         ^
         |       E_1
         |       /\
         |      /  \
         |     /    \      E_f
         | E_i/      \    /
         |            \  /
         |             \/
         |             E_2
         +----------------------> t

        Args:
            vs_initial (list): List (or tuple) of 5 booleans indicating
                whether the current step is vs. the initial one
            voltage_step (list): List (or tuple) of 5 floats (Ei, E1, E2, Ei,
                Ef) indicating the voltage steps (V)
            scan_rate (list): List (or tuple) of 5 floats indicating the scan
                rates (mV/s)
            record_every_dE (float): Record every dE (V)
            average_over_dE (bool): Whether averaging should be performed over
                dE
            N_cycles (int): The number of cycles
            begin_measuring_I (float): Begin step accumulation, 1 is 100%
            end_measuring_I (float): Begin step accumulation, 1 is 100%
            I_Range (str): A string describing the I range, see the
                :data:`I_RANGES` module variable for possible values
            E_range (str): A string describing the E range to use, see the
                :data:`E_RANGES` module variable for possible values
            Bandwidth (str): A string describing the bandwidth setting, see the
                :data:`BANDWIDTHS` module variable for possible values'''

"""CV example"""
'''A program to run a typical CV experiment and export the data to a .csv file'''
'''Currently have 32-bit vs. 64-bit interpreter problems with pandas library, so dump to .csv and use other to put into pandas database'''
import time
import numpy
from bio_logic import SP150, CV

def run_cv():
    """Test the CV technique"""
    ip_address = 'USB0'  # REPLACE THIS WITH A VALID IP
    # Instantiate the instrument and connect to it
    sp150 = SP150(ip_address, 'C:\\EC-Lab Development Package\\EC-Lab Development Package\\EClib.dll')
    sp150.connect()
    sp150.load_firmware([1])
    # Instantiate the technique. Make sure to give values for all the
    # arguments where the default values does not fit your purpose. The
    # default values can be viewed in the API documentation for the
    # technique.
    cv = CV(vs_initial=(False,) * 5,
             voltage_step=(2, 0.5, -0.7, 0.0, 0.0),
             scan_rate=(10.0,) * 5,
             record_every_dE=0.01,
             N_cycles=3)

    # Load the technique onto channel 0 of the potentiostat and start it
    sp150.load_technique(0, cv)
    sp150.start_channel(0)

    Time = numpy.array([])
    Ewe = numpy.array([])
    Ec = numpy.array([])
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
        # print("Time:", data_out.time)
        # print("Ewe:", data_out.Ewe)

        # If numpy is installed, the data can also be retrieved as
        # numpy arrays
        # printing the values to follow for testing
        print('Time:', data_out.time_numpy)
        print('Ewe:', data_out.Ewe_numpy)
        print('Ec', data_out.Ec_numpy)
        print('I', data_out.I_numpy)
        print('cycle', data_out.cycle_numpy)
        # Updating the variables with the appended data per data call
        Ewe = numpy.append(Ewe, data_out.Ewe_numpy_numpy)
        Time = numpy.append(Time, data_out.time_numpy)
        Ec = numpy.append(Ec, data_out.Ec_numpy)
        I = numpy.append(I, data_out.I_numpy)
        cycle = numpy.append(cycle, data_out.cycle_numpy)
        # Sleep
    # dataframe of each variable
    df = (Time, Ewe, Ec, I, cycle)

    #Due to compatibility issues (in my head, this can be fixed), writing data to a .csv for importing into pandas
    # Note the order of header and the df as indicated
    numpy.savetxt("testCV.csv", numpy.transpose(df), delimiter=",", header = 'Time,Ewe,Ec,I,cycle', comments = '')

    sp150.stop_channel(0)
    sp150.disconnect()


if __name__ == '__main__':
    run_cv()
