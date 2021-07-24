from north_c9 import NorthC9
from Locator import *
import time # needed for time.sleep

c9 = NorthC9('A')
c9.home_robot() #just do this once

for i in range(0,1):
    c9.close_clamp()
    c9.goto_safe(p_rack_lower[i], vel = 20000)
#     c9.goto_safe(clamp_pipette_in)
#     c9.goto_safe(new_loc)
#     time.sleep(5)