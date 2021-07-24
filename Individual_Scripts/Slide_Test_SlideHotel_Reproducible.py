from north_c9 import NorthC9
from Locator import *
from ftdi_serial import Serial
import time # needed for time.sleep

print(Serial.list_device_serials())

c9 = NorthC9('A')

c9.home_robot() #just do this once
time.sleep(1)
c9.goto_safe(tool_mount_copy) #Grab tool
c9.close_gripper()


c9.goto_safe(slide_hotel_new_out_zup) # Grab first slide
time.sleep(1)
c9.goto(slide_hotel_new_zup)
time.sleep(1)
c9.goto(slide_hotel_new)
time.sleep(1)
c9.bernoulli_on()
time.sleep(1)
c9.goto(slide_hotel_new_zup)
time.sleep(1)
c9.goto(slide_hotel_new_out_zup)
time.sleep(1)

c9.goto_safe(ECell_out)

c9.goto(ECell)
c9.bernoulli_off()
time.sleep(5)
c9.bernoulli_on()
time.sleep(1)

c9.goto(ECell_out)
# 
# c9.goto_safe(slide_hotel_new_out) # Grab first slide
# c9.move_z(119.5)
# c9.goto(slide_hotel_new)
# c9.bernoulli_off()
# time.sleep(1)
# c9.goto(slide_hotel_new_out)

# c9.goto_safe(tool_mount_copy) # Put tool away
# c9.open_gripper()

