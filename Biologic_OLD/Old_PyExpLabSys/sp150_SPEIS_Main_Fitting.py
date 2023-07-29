'''
RB Created July 15, 2020.
The following is RB utilizing the impedance library (https://impedancepy.readthedocs.io/en/latest/index.html) fit to real EChem
data to fit circuit elements and extract important features such as solution resistance, charge transfer resistance etc.

Refer to the above link for any specific documentation regarding the impedance library

This document also utilizes code written under sp150_SPEIS_Main, the main script to perform EIS measurements from the Bio-Logic

This is constantly updated to add more features and evaluations

Future additions to make:
- Preprocessing on numpy arrays
- Weave with sp150_SPEIS_Main, either as a class or a function, to obtain and perform post-processing prior to circuit fitting
- Evaluate multiple EIS curves at different voltages to obtain capacitance and tafel slope
'''

import time
import numpy as np
import json
from impedance import preprocessing


#From data file rbnb2p86 - Characterization_Tafel_EIS_LowV_01_PEIS. Put here to use as raw data for evaluation
freq = np.array([2.00e+05, 1.35e+05, 9.17e+04, 6.21e+04, 4.21e+04, 2.85e+04,
       1.93e+04, 1.31e+04, 8.86e+03, 6.00e+03, 4.06e+03, 2.75e+03,
       1.86e+03, 1.26e+03, 8.53e+02, 5.78e+02, 3.91e+02, 2.65e+02,
       1.79e+02, 1.22e+02, 8.23e+01, 5.57e+01, 3.77e+01, 2.56e+01,
       1.73e+01, 1.17e+01, 7.94e+00, 5.37e+00, 3.64e+00, 2.47e+00,
       1.67e+00, 1.13e+00, 7.66e-01, 5.19e-01, 3.51e-01, 2.38e-01,
       1.61e-01, 1.09e-01, 7.39e-02, 5.00e-02])

time = np.array([  0.883,   1.3  ,   1.72 ,   2.14 ,   2.56 ,   2.98 ,   3.4  ,
         3.82 ,   4.26 ,   4.66 ,   5.13 ,   5.59 ,   6.05 ,   6.73 ,
         7.19 ,   7.66 ,   8.12 ,   8.58 ,   9.04 ,   9.5  ,   9.95 ,
        10.4  ,  10.9  ,  11.3  ,  11.7  ,  12.1  ,  12.7  ,  13.1  ,
        13.8  ,  15.1  ,  16.4  ,  18.3  ,  21.1  ,  25.2  ,  31.2  ,
        40.   ,  53.1  ,  72.5  , 101.   , 143.   ])

abs_I = np.array([1.78e-04, 1.93e-04, 1.93e-04, 1.93e-04, 1.92e-04, 1.91e-04,
       1.88e-04, 1.87e-04, 1.87e-04, 1.95e-04, 1.99e-04, 2.01e-04,
       2.02e-04, 1.86e-04, 1.86e-04, 1.86e-04, 1.86e-04, 1.86e-04,
       1.86e-04, 1.85e-04, 1.85e-04, 1.84e-04, 1.84e-04, 1.83e-04,
       1.82e-04, 1.81e-04, 1.79e-04, 1.77e-04, 1.74e-04, 1.70e-04,
       1.63e-04, 1.55e-04, 1.42e-04, 1.24e-04, 1.05e-04, 8.78e-05,
       7.32e-05, 6.36e-05, 5.74e-05, 5.32e-05])

abs_Ewe = np.array([0.00987, 0.0106 , 0.0106 , 0.0105 , 0.0105 , 0.0104 , 0.0102 ,
       0.0102 , 0.0101 , 0.0106 , 0.0108 , 0.0109 , 0.011  , 0.0101 ,
       0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101 ,
       0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101 ,
       0.0101 , 0.0101 , 0.0101 , 0.0102 , 0.0102 , 0.0101 , 0.0101 ,
       0.0101 , 0.0101 , 0.0101 , 0.0101 , 0.0101])

Phase_Zwe = np.array([9.66e-01,  5.82e-01,  3.54e-01,  2.18e-01,  1.09e-01,  5.64e-02,
        2.13e-02, -1.58e-02, -5.64e-02, -3.74e-02, -8.84e-02, -8.33e-02,
       -1.01e-01, -1.24e-01, -1.81e-01, -1.85e-01, -3.01e-01, -3.38e-01,
       -5.66e-01, -6.64e-01, -9.18e-01, -1.15e+00, -1.55e+00, -1.98e+00,
       -2.55e+00, -3.30e+00, -4.33e+00, -5.64e+00, -7.39e+00, -9.94e+00,
       -1.33e+01, -1.79e+01, -2.20e+01, -2.61e+01, -2.83e+01, -2.75e+01,
       -2.49e+01, -2.11e+01, -1.75e+01, -1.45e+01])

#For completeness sake, put into a dictionary
data = {'freq':freq.tolist(),'abs_Ewe':abs_Ewe.tolist(),'abs_I':abs_I.tolist(),'Phase_Zwe':Phase_Zwe.tolist()}

abs_Z = np.divide(data['abs_Ewe'], data['abs_I'])
Re_Z = abs_Z * (np.cos(np.radians(data['Phase_Zwe'])))
Im_Z = abs_Z * (np.sin(np.radians(data['Phase_Zwe'])))
df = (freq,Re_Z,Im_Z)

#The data is saved to a .csv file due to the preprocessing step. RB needs to find a way to utilize preprocessing directly on numpy arrays
np.savetxt("Fitting_Spit.csv", np.transpose(df), delimiter=",", comments = '')
frequencies, Z = preprocessing.readCSV('Fitting_Spit.csv')

from impedance.models.circuits import CustomCircuit
#Here a classic circuit is used to fit catalyst data
circuit = 'R0-p(R1-p(R2,CPE2),CPE1)'
initial_guess = [.01, .01, 100, .01, .05, 100, 1]

circuit = CustomCircuit(circuit, initial_guess=initial_guess)

circuit.fit(frequencies,Z)

results = circuit.parameters_
R0 = results[0]
R1 = results[1]
R2 = results[2]
Q1 = results[5]
a1 = results[6]
Q2 = results[3]
a2 = results[4]
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
print(rmse)
