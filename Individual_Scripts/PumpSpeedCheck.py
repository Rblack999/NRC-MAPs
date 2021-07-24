from north_c9 import NorthC9
from Locator import *
from nrc_custom.Ecell_package import ECell
from nrc_custom.Potentiostat import Technique
import csv
import json
import time

c9 = NorthC9('A')
c9.set_pump_speed(0, 15)
c9.set_pump_speed(5, 15)
time.sleep(1)
c9.set_pump_speed(6, 15)
time.sleep(1)