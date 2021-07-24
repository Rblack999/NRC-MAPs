from north_c9 import NorthC9
from Locator import *
import time # needed for time.sleep

c9 = NorthC9('A')

time.sleep(10)
c9.set_output(3,True)
time.sleep(2)
c9.set_output(3,False)