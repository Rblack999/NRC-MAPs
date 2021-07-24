from north_c9 import NorthC9
from Locator import *
from ftdi_serial import Serial
import time # needed for time.sleep

print(Serial.list_device_serials())

c9 = NorthC9('A')

c9.pumps[3]['volume']=12.5
c9.home_pump(3)
c9.delay(1)
c9.set_pump_valve(3,1)
c9.delay(1)
c9.aspirate_ml(3,12.5)

c9.delay(1)
c9.set_pump_valve(3,2)
c9.delay(1)
c9.dispense_ml(3,12.5)
c9.delay(60)

c9.aspirate_ml(3,12.5)
c9.delay(1)
c9.set_pump_valve(3,1)
time.sleep(1)
c9.dispense_ml(3,12.5)