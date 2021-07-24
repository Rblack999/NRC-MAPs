from north_c9 import NorthC9
from Locator import *
from ftdi_serial import Serial
import time # needed for time.sleep

print(Serial.list_device_serials())

c9 = NorthC9('A')

c9.home_robot() #just do this once

for i in [47]:
    c9.open_gripper()
    c9.goto_safe(vial_rack_all[i])
    c9.close_gripper()
    time.sleep(1)
    c9.goto_safe(after_grab_home)
    
    c9.goto_safe(vial_place_scale)
    c9.close_clamp()
    c9.uncap()
    c9.open_clamp()
    c9.move_z(200)
    time.sleep(5)
#    print(c9.read_scale())
    
    c9.close_clamp()
    c9.goto_safe(vial_place_scale_cap)
    c9.cap()
    c9.open_clamp()
    c9.goto_safe(after_grab_home)
    
    c9.goto_safe(vial_rack_all[i])
    c9.open_gripper()
    c9.move_z(200)
