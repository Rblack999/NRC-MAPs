from north_c9 import NorthC9
from Locator import *
from nrc_custom.Ecell_package import ECell
from nrc_custom.Potentiostat import Technique
import csv
import json
import time

#Initialize robot
c9 = NorthC9('A')

#Initialize pumps
c9.pumps[6]['volume'] = 12.5
c9.home_pump(6)
c9.set_pump_speed(6, 15)

Ecell_char = ECell('characterization','COM2') # Initial connection to Ecell
Ecell_char.cell_close_slide() # Ensure cell is open prior to any experiment

 
#Add liquid to ECell and let equilibrate #TODO - how long let sit and run? 
for i in range(0,1):
    c9.set_pump_valve(6,0)
    c9.delay(1)
    c9.aspirate_ml(6,12.5)
    c9.delay(1)
    c9.set_pump_valve(6,2)
    c9.delay(1)
    c9.dispense_ml(6,12.5)
    c9.aspirate_ml(6,12.5)
    time.sleep(1)
    c9.set_pump_valve(6,1)
    time.sleep(1)
    c9.dispense_ml(6,12.5)
    time.sleep(1)

Ecell_char.cell_open()