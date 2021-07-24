from north_c9 import NorthC9
from Locator import *
from ftdi_serial import Serial
import time # needed for time.sleep

print(Serial.list_device_serials())

c9 = NorthC9('A', verbose = True)

c9.zero_scale()
time.sleep(1)
c9.clear_scale()
time.sleep(1)