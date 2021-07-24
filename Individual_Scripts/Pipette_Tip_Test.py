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
c9.goto_safe(MT_upper_pip_rack_Up)
c9.delay(1)
c9.goto(MT_upper_pip_rack_Down)
c9.delay(1)
c9.goto(MT_upper_pip_rack_withPip_Up)
c9.delay(1)
c9.goto_safe(after_grab_home) #To avoid collision with ECell on next movement

# go to clamp (with pippet) to position over vial and then plunge into vial.
c9.goto_safe(MT_Vial_Up)
c9.delay(1)
c9.goto(MT_Vial_Down)
c9.delay(1)

# suck up 1.0 ml from vial
c9.set_pump_valve(0,0)
c9.delay(1)
c9.aspirate_ml(0,1.0)

# move arm up with pippet holding 1 mL
c9.delay(1)
c9.goto_safe(MT_Vial_Up)
c9.delay(1)

# move arm down with pippet holding 1 mL and dispense into vial
c9.goto(MT_Vial_Down)
c9.delay(1)
c9.set_pump_valve(0,0)
c9.delay(1)
c9.dispense_ml(0,1.0)
c9.delay(1)

# pippet back up
c9.goto_safe(MT_Vial_Up)
c9.delay(1)

c9.goto_safe(after_grab_home) #To avoid collision with ECell





