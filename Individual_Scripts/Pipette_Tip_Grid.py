from north_c9 import NorthC9
from Locator import *
from ftdi_serial import Serial
import time # needed for time.sleep

print(Serial.list_device_serials())

c9 = NorthC9('A')

c9.home_robot() #just do this once
c9.pumps[0]['volume']=5 #Set pump parameters and home
c9.home_pump(0)
# close the clamp
c9.close_clamp(1)

# pick up a pippet from the pippet holder (1st position)
for i in [0,1,22,23]:

    c9.goto_safe(Pipette_rack_initial[i])
    c9.delay(1)
    c9.goto(Pipette_rack_drop[i])
    c9.delay(1)
    c9.goto(Pipette_rack_up[i])
    c9.delay(1)
    c9.goto_safe(after_grab_home) #To avoid collision with ECell on next movement

    # go to clamp (with pippet) to position over vial and then plunge into vial.
    c9.goto_safe(MT_Vial_Up)
    time.sleep(5)

    c9.goto_safe(after_grab_home) #To avoid collision with ECell
    c9.goto_safe(Pipette_remove_ready)
    c9.goto(Pipette_remove)
    c9.move_z(250)
    






