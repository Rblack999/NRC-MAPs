# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 12:43:51 2019

@author: Blackr
"""
"""OCV example"""
'''A program to run a typical OCV experiment and export the data to a .csv file'''
'''Currently have 32-bit vs. 64-bit interpreter problems with pandas library, so dump to .csv and use other to put into pandas database'''
import time
import numpy
from bio_logic import SP150, OCV
import json

def run_ocv():
    """Test the OCV technique"""
    ip_address = 'USB0' # Instantiate the instrument and connect to it
    sp150 = SP150(ip_address,  'C:\\EC-Lab Development Package\\EC-Lab Development Package\\EClib.dll')
    sp150.connect()
    sp150.load_firmware([1])
    # Instantiate the technique. Make sure to give values for all the
    # arguments where the default values does not fit your purpose. The
    # default values can be viewed in the API documentation for the
    # technique.
    ocv = OCV(rest_time_T=1,
              record_every_dE=10.0,
              record_every_dT=0.1)

    # Load the technique onto channel 0 of the potentiostat and start it
    sp150.load_technique(0, ocv)
    sp150.start_channel(0)

    time.sleep(0.1)

    #Making empty numpy arrays to append each data point
    Time = numpy.array([])
    Ewe = numpy.array([])
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
        #print("Time:", data_out.time)
        #print("Ewe:", data_out.Ewe)


        # If numpy is installed, the data can also be retrieved as
        # numpy arrays
        #print('Time:', data_out.time_numpy)
        #print('Ewe:', data_out.Ewe_numpy)
        Ewe = numpy.append(Ewe, data_out.Ewe_numpy)
        Time = numpy.append(Time, data_out.time_numpy)

    #Below are two methods of saving the output data
    #First method is saving the data as columns in a .csv file
    df = (Ewe,Time)
    numpy.savetxt("SP150_OCV_Main.csv", numpy.transpose(df), delimiter=",", header = 'Ewe,Time', comments = '')

    #The second method is saving the data as a .json file
    data = {'Time': Time.tolist(),'Ewe': Ewe.tolist()}
    with open("SP150_OCV_Main.json", "w") as outfile:
        json.dump(data, outfile)

    print(data)
    sp150.stop_channel(0)
    sp150.disconnect()


if __name__ == '__main__':
    run_ocv()
