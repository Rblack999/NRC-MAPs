#Below is a function to get the iR of the acquired impedance data
#The iR is determined at the ~0 phase region, where the resistance corresponds to the solution (iR) resistance
#This value we need to be used for post processing correction of overpotential
def get_iR(data):
    index = data['Phase_Zwe'].index(min((abs(i)) for i in data['Phase_Zwe']))
    E_phase0 = data['abs_Ewe'][index]
    I_phase0 = data['abs_I'][index]
    iR = E_phase0/I_phase0
    return iR