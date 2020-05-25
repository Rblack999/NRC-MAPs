# -*- coding: utf-8 -*-
"""
Created on Sun May  3 18:37:20 2020

@author: Blackr

The following is a script I wrote to automatically find the tafel data
a .csv file with the appropriate I, Ewe, and time columns
time = s
I = mA
E = V

This is mostly used as a coding excerise for post processing. Re-evaluate when it is time to write more post-processing scripts
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv('March5_2020_Cell4.csv')

#Drop columns that have all NaN (.csv problem?)
df.dropna(axis =1, how ='all', inplace = True)

#Determine what Ewe data is "stable" compared to transition noise and drop the "noise" data
df['Ewe'].value_counts()
#Explanation of how the code below works is here: 
#https://stackoverflow.com/questions/34913546/remove-low-counts-from-pandas-data-frame-column-on-condition
s = df['Ewe'].value_counts()
dfclean = df[df.isin(s.index[s >= 100]).values]

#MDetermine median value of I vs. t curves
#Create an array of unique Ewe values
unique = dfclean['Ewe'].unique()

#For loop to create an array of median values corresponding to the median aggregate of each unique Ewe
median_values = []
for x in unique:
    df2 = df[df['Ewe'] == x]
    median_value = df2['I'].median()
    median_values.append(median_value)

#Convert unique and median_value variables into Series following by a dataframe
median_values = pd.Series(median_values)
unique = pd.Series(unique)
d = {'Ewe': unique,'I': median_values}
df_median = pd.DataFrame(d)

#Various corrections to the data
#df_media current data to A instead of mA
df_median['I'] = df_median['I']/1000

#Reference electrode data - need to add appropriate reference data to make vs. NHE
ref_electrode = {'Ag_AgCl':0.197}

#Determination of solution resistance via EIS file
#EIS file generated from sp150_SPEIS_export.py
#Call the database and return row for minimum abs value of phase (closest to phase = 0)
#Obtain resistance through R = V/I, and since phase ~0 this is the solution resistance
#The to_numpy was used because without resistance would be an indexed panda series
dfr = pd.read_csv('EISdata.csv')
dfrmin = dfr[dfr['Phase_Zwe'] == min(abs(dfr['Phase_Zwe']))]
resistance = (dfrmin['abs_Ewe']/dfrmin['abs_I']).to_numpy()

#IR correction of the data
df_median['EweIR'] = df_median['Ewe'] - (df_median['I']*resistance)


#Ewe vs. NHE data
df_median['EweNHE'] = df_median['Ewe']+ref_electrode['Ag_AgCl']

#Add Overpotential column
pH = 7 #Figure out how to add this automatically?
df_median['Overpotential'] = df_median['EweNHE'] - (1.23-(0.059*pH))

#Adding a Log column for I
import math
df_median['LogI'] = df_median['I'].apply(math.log10)

#Selection and plotting of the tafel plot slope, r_value, and intercept
#First obtain the number of rows
df_median['EweNHE'].count()
#Iterate up to this value over sections of 5 points each and perform linear analysis
count = 0
df_r_value = []
df_slope = []
df_intercept = []
#Linear Regression Analysis Using Linear Region Points. y = mx+b
#Note that the range has a -4 added to it. This is to ensure the measured range includes 5 points. Without this
  #the line would be taken for the last 4,3,2, and 1 points separately and give false lines. This will make the
  #slope and r_value df's 4 rows shorter than the parent dataframe.
  #This can be adjusted as necessary if more points are needed!
#for x in range(0,df_median['EweNHE'].count()):
for x in range(0,(df_median['EweNHE'].count())-4):
    x = df_median['LogI'][count:(count+5)]
    y = df_median['EweNHE'][count:(count+5)]
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    y_fit = slope*x + intercept
    df_r_value.append(r_value)
    df_slope.append(slope)
    df_intercept.append(intercept)
    count += 1
#Fill in last four rows with nan to make same size as parent matrix
n = float('nan')
num = [0,1,2,3]
for x in num:
    df_r_value.append(n)
    df_slope.append(n)
    df_intercept.append(n)

#Add r_value and slope to parent dataframe. Note that the row corresponds to the value first and pass 5 points
#eg. r_value for Ewe = 1.34 corresponds to the value fit for Ewe = [1.34 - 1.28]
df_median['r_value'] = df_r_value
df_median['slope'] = df_slope
df_median['intercept'] = df_intercept

#The following code was used to determine the minimum slope value in the series
df_median[df_median['slope'] == df_median['slope'].min()]['LogI']
line_index = df_median[df_median['slope'] == df_median['slope'].min()]['LogI'].index.values.astype(int)

#Definitiation of slope and intercept corresponding to the minimum point
s = df_median['slope'][line_index[0]]
i = df_median['intercept'][line_index[0]]

# Variable y_plot (Ewe) for generation of the straight (Tafel) line
y_plot = df_median['LogI'][line_index[0]:line_index[0]+5].apply(lambda x:(s*x)+i)

#Plot the figure
fig = plt.figure()

plt.scatter(df_median['LogI'],df_median['EweNHE'])
plt.plot(df_median['LogI'][line_index[0]:line_index[0]+5],y_plot)
plt.xlabel('Log i (A/cm2)')
plt.ylabel('E vs. NHE (V)')
plt.xlim(-6.5,-2.5)
plt.yticks([0.8,1,1.2,1.4,1.6])
plt.xticks([-6,-5,-4,-3])
plt.title('30 second Tafel')

s = str(round(s, 3))
rr_value = str(round(df_median['r_value'][line_index[0]],3))

fig.text(0.65, 0.775, f'{s} V/dec \nR-squared = {rr_value}', style='italic',
        bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 5})

plt.show()

#To add in the future
#- Something to filter bad R2 values because sometimes the best slope is the
#worst r-value 
