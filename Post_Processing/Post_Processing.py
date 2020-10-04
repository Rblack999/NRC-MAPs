'''
The following is a post-processing script which contains functions for all the post-processing of data
Note there are two formats:
a) Import of a .csv file
b) Directly using the data form the potentiostat (as numpy arrays)

'''
import pandas as pd
import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt
from scipy import stats
from impedance import preprocessing

'''
#Below is a function to get the iR of the acquired impedance data
#The iR is determined at the ~0 phase region, where the resistance corresponds to the solution (iR) resistance
#This value we need to be used for post processing correction of overpotential

Data from the instrument will come in the following format:
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
'''

'''
Below is pulling the data from a .csv file that has the columns saved in the following format: 
*Note the indices are biologic standard with just the headers erased


df = pd.read_csv('March5_2020_Cell4.csv')
[0] = frequency (Hz)
[4] = Phase_Zwe
[12] = abs_Ewe
[13] = abs_I
'''

def get_iR(data):
    #used to obtain the index value where the minimum Phase is found (representing phase = 0)
    #abs(i) for i in data['Phase_Zwe'] is to make all values in the phase_Zwe array absolute value (no negative)
    #Pull out the index of the smallest absolute value. This is to avoid the pulled min value (due to abs) reversing sign
     #and not found in the original data['Phase_Zwe']
    #global iR #Setting the value for iR to be saved to be able to use in other functions
    df = genfromtxt(data, delimiter=',')
    df = np.transpose(df)
    index = [abs(i) for i in df[4]].index(min((abs(i)) for i in df[4]))
    E_phase0 = df[12][index]
    I_phase0 = df[13][index]
    iR = E_phase0/I_phase0
    return iR

# -*- coding: utf-8 -*-
"""
The following is a script I wrote to automatically find the tafel data
The data must be uploaded in the following format:
dict{'time':np.array(),'Ewe':np.array(),'I':np.array()}
time = s
I = mA
E = V
There is also scripts that can be uncommented to accept a .csv file of the as named columns
Below is for reading in the data from a "noisy" .csv file. Can be commented out when working directly with the potentiostat
"""
def tafel_fit(data):
    #Below is just to read in the data as a pd dataframe for easy conversion and format the data.
    #In the real script, data will exist and come in as a cleaner dictionary, although post-processing may be necessary
    df = pd.read_csv(data)
    #Drop columns that have all NaN (.csv problem?)
    df.dropna(axis =1, how ='all', inplace = True)

    #Determine what Ewe data is "stable" compared to transition noise and drop the "noise" data
    df['Ewe'].value_counts()
    #Explanation of how the code below works is here:
    #https://stackoverflow.com/questions/34913546/remove-low-counts-from-pandas-data-frame-column-on-condition
    s = df['Ewe'].value_counts()
    df = df[df.isin(s.index[s >= 5]).values]

    #For testing purposes, put data into a dictionary. From the potentiostat the data will come in this form, with the dict.values()
    #as numpy arrays
    dict = {'time':np.array(df['time']),'Ewe':(np.array(df['Ewe'])),'I':(np.array(abs(df['I'])/1000))} #Note unit conversions to put I = A and V = V vs. NHE
    plt.plot(dict['time'],dict['I'])
    plt.show()

    #This is only to ensure the data is clean
    #In the future when only working with np arrays, try something like this:
    #np.unique(a[1], return_counts = True)
    np.unique(dict['Ewe'], return_counts = True)

    #Make a matrix of the three keys for post processing
    a = np.array([dict['time'],dict['Ewe'],dict['I']])  #a[0] = time, a[1] = Ewe, a[2] = I

    #The following is a for loop to determine the last value of each Ewe step from the array
    #Use np.where to obtain the column index of for which the Ewe = given value
    #Use this array to index out the appropriate I, choosing the last value to remove any capacitive current capture
    #Make new array with the latest I, with appropriate corresponding E

    current_values = np.zeros(len(np.unique(a[1]))) #empty array to populate based on size of unique values of Ewe
    for i in range(len(current_values)):
        index = np.where(a[1] == np.unique(a[1])[i]) #For each value of Ewe == to unique Ewe, gives index
        current_values[i] = a[2][index][-5] #Set the corresponding np.zero array to the last(ish) value of current
    current_values = np.log10(current_values) #Convert to log scale
    Ewe_tafel = np.unique(a[1]) #Make this a variable for next sections

    '''Add in some IR correction at this stage, have it link back to previous function'''
    '''Add information about the pH to adjust for Ewe'''
    #Next step we do iR and environment corrections
    #ir = 30 #Note this should link to previous function
    Ewe_tafel = Ewe_tafel+.197-(iR*(10**current_values))

    #The next steps are to iterate over 5 data points to find the best curve fit
    #Use scipy.stats linregressand use std.err to evaluate the best fit
    error_array = np.zeros(len(current_values)-4) #Note -5 because will be using 5 points at a time for analysis
    slope_array = np.zeros(len(current_values)-4)
    intercept_array = np.zeros(len(current_values)-4)
    for i in range(len(current_values)-4):
        slope, intercept, r_value, p_value, std_err = stats.linregress(current_values[i:i+5],Ewe_tafel[i:i+5])
        error_array[i] = std_err
        slope_array[i] = slope
        intercept_array[i] = intercept
    print("Error Array = {}".format(error_array))
    print('Slope Array = {}'.format(slope_array))
    print('Intercept = {}'.format(intercept_array))

    #From these linear fits, choose the best std_error slope and intercept to fit to the rest of the data
    #and obtain the tafel_slope
    index = np.where(error_array == np.min(error_array)) #Get the index of the lowest std_error
    fit_Ewe = slope_array[index]*current_values+intercept_array[index] #Get the fit values for curve

    #The following makes the final plot
    fig = plt.figure()

    plt.plot(current_values,fit_Ewe, linestyle = 'dashed')
    plt.scatter(current_values,Ewe_tafel)
    plt.title('Tafel Slope = {} V/dec'.format(str(round(slope_array[index][0], 3))))
    plt.ylabel('Ewe (V vs. NHE)')
    plt.xlabel('Log(I) (A)')
    fig.text(0.15, 0.775, 'Tafel = {} V/dec \nstd-err = {}'.format(str(round(slope_array[index][0], 3)),str(round(error_array[index][0], 6))), style='italic',
            bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 5})
    plt.show()

def EIS_fit(data):
    #From data file rbnb2p86 - Characterization_Tafel_EIS_LowV_01_PEIS. Put here to use as raw data for evaluation. Keep this as comments for when need to test the script.
    #frequencies = np.array([2.00e+05, 1.35e+05, 9.17e+04, 6.21e+04, 4.21e+04, 2.85e+04,
           #1.93e+04, 1.31e+04, 8.86e+03, 6.00e+03, 4.06e+03, 2.75e+03,
           #1.86e+03, 1.26e+03, 8.53e+02, 5.78e+02, 3.91e+02, 2.65e+02,
           #1.79e+02, 1.22e+02, 8.23e+01, 5.57e+01, 3.77e+01, 2.56e+01,
           #1.73e+01, 1.17e+01, 7.94e+00, 5.37e+00, 3.64e+00, 2.47e+00,
           #1.67e+00, 1.13e+00, 7.66e-01, 5.19e-01, 3.51e-01, 2.38e-01,
           #1.61e-01, 1.09e-01, 7.39e-02, 5.00e-02])

    #time = np.array([  0.883,   1.3  ,   1.72 ,   2.14 ,   2.56 ,   2.98 ,   3.4  ,
             #3.82 ,   4.26 ,   4.66 ,   5.13 ,   5.59 ,   6.05 ,   6.73 ,
             #7.19 ,   7.66 ,   8.12 ,   8.58 ,   9.04 ,   9.5  ,   9.95 ,
            #10.4  ,  10.9  ,  11.3  ,  11.7  ,  12.1  ,  12.7  ,  13.1  ,
            #13.8  ,  15.1  ,  16.4  ,  18.3  ,  21.1  ,  25.2  ,  31.2  ,
            #40.   ,  53.1  ,  72.5  , 101.   , 143.   ])

    #abs_I = np.array([1.78e-04, 1.93e-04, 1.93e-04, 1.93e-04, 1.92e-04, 1.91e-04,
           #1.88e-04, 1.87e-04, 1.87e-04, 1.95e-04, 1.99e-04, 2.01e-04,
           #2.02e-04, 1.86e-04, 1.86e-04, 1.86e-04, 1.86e-04, 1.86e-04,
           #1.86e-04, 1.85e-04, 1.85e-04, 1.84e-04, 1.84e-04, 1.83e-04,
           #1.82e-04, 1.81e-04, 1.79e-04, 1.77e-04, 1.74e-04, 1.70e-04,
           #1.63e-04, 1.55e-04, 1.42e-04, 1.24e-04, 1.05e-04, 8.78e-05,
           #7.32e-05, 6.36e-05, 5.74e-05, 5.32e-05])

    #abs_Ewe = np.array([0.00987, 0.0106 , 0.0106 , 0.0105 , 0.0105 , 0.0104 , 0.0102 ,
           #0.0102 , 0.0101 , 0.0106 , 0.0108 , 0.0109 , 0.011  , 0.0101 ,
           #0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101 ,
           #0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101 ,
           #0.0101 , 0.0101 , 0.0101 , 0.0102 , 0.0102 , 0.0101 , 0.0101 ,
           #0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101])

    #Phase_Zwe = np.array([9.66e-01,  5.82e-01,  3.54e-01,  2.18e-01,  1.09e-01,  5.64e-02,
            #2.13e-02, -1.58e-02, -5.64e-02, -3.74e-02, -8.84e-02, -8.33e-02,
           #-1.01e-01, -1.24e-01, -1.81e-01, -1.85e-01, -3.01e-01, -3.38e-01,
           #-5.66e-01, -6.64e-01, -9.18e-01, -1.15e+00, -1.55e+00, -1.98e+00,
           #-2.55e+00, -3.30e+00, -4.33e+00, -5.64e+00, -7.39e+00, -9.94e+00,
           #-1.33e+01, -1.79e+01, -2.20e+01, -2.61e+01, -2.83e+01, -2.75e+01,
           #-2.49e+01, -2.11e+01, -1.75e+01, -1.45e+01])

    #Below is pulling data from a .csv file
    #Note that the data, in particular at high frequency, is quite messy!
    data = genfromtxt(data, delimiter=',')
    data = np.transpose(data)
    frequencies = data[0]
    abs_Ewe = data[12]
    abs_I = data[13]
    Phase_Zwe = data[4]

    #For completeness sake, put into a dictionary
    data = {'frequencies':frequencies.tolist(),'abs_Ewe':abs_Ewe.tolist(),'abs_I':abs_I.tolist(),'Phase_Zwe':Phase_Zwe.tolist()}

    abs_Z = np.divide(data['abs_Ewe'], data['abs_I'])
    Re_Z = abs_Z * (np.cos(np.radians(data['Phase_Zwe'])))
    Im_Z = abs_Z * (np.sin(np.radians(data['Phase_Zwe'])))
    #Convert Re_Z and Im_Z into a single complex numpy array
    Z = Re_Z + 1j*Im_Z

    #Below is built in library to cut frequencies below x-axis
    frequencies, Z = preprocessing.ignoreBelowX(frequencies,Z)

    from impedance.models.circuits import CustomCircuit
    # A different circuit
    circuit = 'R0-p(R1,CPE1)-p(R2,CPE2)'
    initial_guess = [1000, 100, 1E-6, 0.7, 10, 0.1E-6, 0.6]

    circuit = CustomCircuit(circuit, initial_guess=initial_guess)
    print(circuit)

    circuit.fit(frequencies,Z)

    results = circuit.parameters_
    R0 = results[0]
    R1 = results[1]
    R2 = results[4]
    Q1 = results[2]
    a1 = results[3]
    Q2 = results[5]
    a2 = results[6]
    print(f'R0 = {R0} ohms')
    print(f'R1 = {R1} ohms')
    print(f'R2 = {R2} ohms')
    print(f'Q1 = {Q1} F.s^(a-1)')
    print(f'a1 = {a1}')
    print(f'Q2 = {Q2} F.s^(a-1)')
    print(f'a2 = {a2}')

    Z_fit = circuit.predict(frequencies)

    import matplotlib.pyplot as plt
    from impedance.visualization import plot_nyquist

    fig, ax = plt.subplots()
    plot_nyquist(ax, Z, fmt='o')
    plot_nyquist(ax, Z_fit, fmt='-')

    plt.legend(['Data', 'Fit'])
    plt.show()

#Examples to run
#iR = get_iR('C:\\Users\\Blackr\\Documents\\Data Main\\NRC-M MAPs\\Experimental\\rbnb2p107\\TestB\\TestB_Char_initial_EIS_C01.csv')
#tafel_fit('C:\\Users\\Blackr\\Documents\\Data Main\\NRC-M MAPs\\Experimental\\rbnb2p107\\TestB\\TestB_Char_initial_Tafel_C01.csv')
EIS_fit('C:\\Users\\Blackr\\Documents\\Data Main\\NRC-M MAPs\\Experimental\\rbnb2p107\\TestA_Char_AfterTafel_EISTafel_1d08_C01.csv')