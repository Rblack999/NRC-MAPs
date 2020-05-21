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
    ocv = OCV(rest_time_T=5,
              record_every_dE=10.0,
              record_every_dT=0.2)

    # Load the technique onto channel 0 of the potentiostat and start it
    sp150.load_technique(0, ocv)
    sp150.start_channel(0)

    time.sleep(0.1)
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
        # print("Time:", data_out.time)
        # print("Ewe:", data_out.Ewe)

        # If numpy is installed, the data can also be retrieved as
        # numpy arrays
        print('Time:', data_out.time_numpy)
        print('Ewe:', data_out.Ewe_numpy)
        Ewe = numpy.append(Ewe, data_out.Ewe_numpy_numpy)
        Time = numpy.append(Time, data_out.time_numpy)
        time.sleep(0.2)

    # Reshaping the arrays into columns
    #Ewe = Ewe.reshape(-1, 1)
    #Time = Time.reshape(-1, 1)
    df = (Ewe,Time)
    #df2 = pandas.DataFrame(data = Ewe)
    # Printing out the final arrays for viewing
    print(f'The final dataframe is {df}')

    #Due to compatibility issues (in my head), writing data to a .csv for importing into pandas
    numpy.savetxt("test.csv", numpy.transpose(df), delimiter=",", header = 'Ewe,Time', comments = '')

    sp150.stop_channel(0)
    sp150.disconnect()


if __name__ == '__main__':
    run_ocv()
