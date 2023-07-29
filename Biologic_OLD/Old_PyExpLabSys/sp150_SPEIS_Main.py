# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 12:43:51 2019

@author: Blackr

Staircase Potentio Electrochemical Impedance Spectroscopy (SPEIS)
    technique class

    The SPEIS technique returns data with a different set of fields depending
    on which process steps it is in. If it is in process step 0 it returns
    data on the following fields (in order):

    * time (float)
    * Ewe (float)
    * I (float)
    * step (int)

    If it is in process 1 it returns data on the following fields:

    * freq (float)
    * abs_Ewe (float)
    * abs_I (float)
    * Phase_Zwe (float)
    * Ewe (float)
    * I (float)
    * abs_Ece (float)
    * abs_Ice (float)
    * Phase_Zce (float)
    * Ece (float)
    * t (float)
    * Irange (float)
    * step (float)

    Which process it is in, can be checked with the ``process`` property on
    the :class:`.KBIOData` object.

A program to run a typical SPEIS experiment and export the data to a .csv file
Currently have 32-bit vs. 64-bit interpreter problems with pandas library, so dump to .csv and use other to put into pandas database
"""
import time
import numpy
from bio_logic import SP150, SPEIS
import json
import impedance

def run_speis():
    """Test the SPEIS technique"""
    ip_address = 'USB0'  # REPLACE THIS WITH A VALID IP
    # Instantiate the instrument and connect to it
    sp150 = SP150(ip_address, 'C:\\EC-Lab Development Package\\EC-Lab Development Package\\EClib.dll')
    sp150.connect()
    sp150.load_firmware([1])
    # Instantiate the technique. Make sure to give values for all the
    # arguments where the default values does not fit your purpose. The
    # default values can be viewed in the API documentation for the
    # technique.
    speis = SPEIS(vs_initial = True, vs_final = False, initial_voltage_step = 0,
                 final_voltage_step = 0, duration_step = 1, step_number = 1,
                 record_every_dT=0.1, record_every_dI=1,
                 final_frequency=100.0E3, initial_frequency=1000.0,
                 sweep=False, amplitude_voltage=0.01,
                 frequency_number=6, average_n_times=2,
                 correction=False, wait_for_steady=0.1,
                 I_range='KBIO_IRANGE_AUTO',
                 E_range='KBIO_ERANGE_2_5', bandwidth='KBIO_BW_5'
              )
    '''Args:
            vs_initial (bool): Whether the voltage step is vs. the initial one
            vs_final (bool): Whether the voltage step is vs. the final one
            initial_step_voltage (float): The initial step voltage (V)
            final_step_voltage (float): The final step voltage (V)
            duration_step (float): Duration of step (s)
            step_number (int): The number of voltage steps
            record_every_dT (float): Record every dT (s)
            record_every_dI (float): Record every dI (A)
            final_frequency (float): The final frequency (Hz)
            initial_frequency (float): The initial frequency (Hz)
            sweep (bool): Sweep linear/logarithmic (True for linear points
                spacing)
            amplitude_voltage (float): Amplitude of sinus (V)
            frequency_number (int): The number of frequencies
            average_n_times (int): The number of repeat times used for
                frequency averaging
            correction (bool): Non-stationary correction
            wait_for_steady (float): The number of periods to wait before each
                frequency
            I_Range (str): A string describing the I range, see the
                :data:`I_RANGES` module variable for possible values
            E_range (str): A string describing the E range to use, see the
                :data:`E_RANGES` module variable for possible values
            Bandwidth (str): A string describing the bandwidth setting, see the
                :data:`BANDWIDTHS` module variable for possible values

        Raises:
            ValueError: On bad lengths for the list arguments'''

    # Load the technique onto channel 0 of the potentiostat and start it
    sp150.load_technique(0, speis)
    sp150.start_channel(0)
    #time.sleep(0.5)

    #Creating blank numpy arrays to populate with .append for each data point
    time = numpy.array([])
    I = numpy.array([])
    freq = numpy.array([])
    abs_Ewe = numpy.array([])
    abs_I = numpy.array([])
    Phase_Zwe = numpy.array([])
    Ewe = numpy.array([])
    abs_Ece = numpy.array([])
    abs_Ice = numpy.array([])
    Phase_Zce = numpy.array([])
    Ece = numpy.array([])
    step = numpy.array([])
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

        #The following is my attempt to split the data into that retrieved at process = 0 and process = 1
        if data_out.process == 0:

           time  = numpy.append(time, data_out.time_numpy)
           Ewe = numpy.append(Ewe, data_out.Ewe_numpy_numpy)
           I = numpy.append(I, data_out.I_numpy)
           step = numpy.append(step, data_out.step_numpy)

        else:
            freq = numpy.append(freq, data_out.freq_numpy)
            abs_Ewe = numpy.append(abs_Ewe, data_out.abs_Ewe_numpy)
            abs_I = numpy.append(abs_I, data_out.abs_I_numpy)
            Phase_Zwe = numpy.append(Phase_Zwe, data_out.Phase_Zwe_numpy)
            abs_Ece= numpy.append(abs_Ece, data_out.abs_Ece_numpy)
            abs_Ice = numpy.append(abs_Ice, data_out.abs_Ice_numpy)
            Phase_Zce = numpy.append(Phase_Zce, data_out.Phase_Zce_numpy)
            Ece = numpy.append(Ece, data_out.Ece_numpy)

    #Below are two methods of saving the output data
    #First method is saving the data as columns in a .csv file
    df = (freq,abs_Ewe,abs_I,Phase_Zwe,abs_Ece,abs_Ice,Phase_Zce,Ece)
    #Due to compatibility issues (in my head, this can be fixed), writing data to a .csv for importing into pandas
    # Note the order of header and the df as indicated
    numpy.savetxt("SP150_SPEIS_Main.csv", numpy.transpose(df), delimiter=",", header = 'freq,abs_Ewe,abs_I,Phase_Zwe,abs_Ece,abs_Ice,Phase_Zce,Ece,Ewe', comments = '')

    # The second method is saving the data as a .json file
    data = {'freq':freq.tolist(),'abs_Ewe':abs_Ewe.tolist(),'abs_I':abs_I.tolist(),'Phase_Zwe':Phase_Zwe.tolist(),'abs_Ece':abs_Ece.tolist(),
            'abs_Ice':abs_Ice.tolist(),'Phase_Zce':Phase_Zce.tolist(),'Ece':Ece.tolist()}
    with open('SP150_SPEIS_Main.json', 'w') as json_file:
        json.dump(data, json_file)
    print(data)

    sp150.stop_channel(0)
    sp150.disconnect()


if __name__ == '__main__':
    run_speis()

#Below is a function to get the iR of the acquired impedance data
#The iR is determined at the ~0 phase region, where the resistance corresponds to the solution (iR) resistance
#This value we need to be used for post processing correction of overpotential
def get_iR(data):
    #used to obtain the index value where the minimum Phase is found (representing phase = 0)
    #abs(i) for i in data['Phase_Zwe'] is to make all values in the phase_Zwe array absolute value (no negative)
    #Pull out the index of the smallest absolute value. This is to avoid the pulled min value (due to abs) reversing sign
     #and not found in the original data['Phase_Zwe']
    index = [abs(i) for i in data['Phase_Zwe']].index(min((abs(i)) for i in data['Phase_Zwe']))
    E_phase0 = data['abs_Ewe'][index]
    I_phase0 = data['abs_I'][index]
    iR = E_phase0/I_phase0
    return iR

#To obtain a nyquist plot, write code for the following:
def nyquist(data):
    abs_Z = np.divide(data['abs_Ewe'], data['abs_I'])
    #Note the obtained values are in degrees, so have to convert to radians
    Re_Z = abs_Z * (np.cos(np.radians(data['Phase_Zwe'])))
    Im_Z = abs_Z * (np.sin(np.radians(data['Phase_Zwe'])))

