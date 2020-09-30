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
    print(f"Error Array = {error_array}")
    print(f'Slope Array = {slope_array}')
    print(f'Intercept = {intercept_array}')

    #From these linear fits, choose the best std_error slope and intercept to fit to the rest of the data
    #and obtain the tafel_slope
    index = np.where(error_array == np.min(error_array)) #Get the index of the lowest std_error
    fit_Ewe = slope_array[index]*current_values+intercept_array[index] #Get the fit values for curve

    #The following makes the final plot
    fig = plt.figure()

    plt.plot(current_values,fit_Ewe, linestyle = 'dashed')
    plt.scatter(current_values,Ewe_tafel)
    plt.title(f'Tafel Slope = {str(round(slope_array[index][0], 3))} V/dec')
    plt.ylabel('Ewe (V vs. NHE)')
    plt.xlabel('Log(I) (A)')
    fig.text(0.15, 0.775, f'Tafel = {str(round(slope_array[index][0], 3))} V/dec \nstd-err = {str(round(error_array[index][0], 6))}', style='italic',
            bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 5})
    plt.show()