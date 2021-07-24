from north_c9 import NorthC9
from Locator import *
from ftdi_serial import Serial
import time # needed for time.sleep

print(Serial.list_device_serials())

c9 = NorthC9('A')

c9.home_robot() #just do this once

for i in range(0,5):
    c9.goto_safe(vial_rack_all[i])
    c9.close_gripper()
    c9.move_z(200)
    c9.goto_safe(vial_rack_all[i])
    c9.open_gripper()
    c9.move_z(200)