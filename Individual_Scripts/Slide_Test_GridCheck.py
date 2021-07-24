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
c9.goto_safe(slide_hotel_new_out_zup_grid2[0])

for i in [0,7,14,21,35]:
    c9.goto(slide_hotel_new_out_zup_grid2[i]) # Grab first slide
    time.sleep(1)
    c9.goto(slide_hotel_new_zup_grid2[i])
    time.sleep(1)
    c9.goto(slide_hotel_new_zdown_grid2[i])
    time.sleep(0.5)
    c9.bernoulli_on()
    time.sleep(1)
    c9.goto(slide_hotel_new_zup_grid2[i])
    time.sleep(0.5)
    c9.goto(slide_hotel_new_out_zup_grid2[i])
    time.sleep(0.5)
    
    c9.goto_safe(ECell_depo_out)
    time.sleep(0.5)
    c9.goto(ECell_depo)
    time.sleep(0.5)
    c9.bernoulli_off()
    time.sleep(5)
    c9.bernoulli_on()
    time.sleep(1)
    c9.goto(ECell_depo_out)

    c9.goto(slide_hotel_new_out_zup_grid2[i]) # Return to first slide position
    time.sleep(0.5)
    c9.goto(slide_hotel_new_zup_grid2[i])
    time.sleep(0.5)
    c9.goto(slide_hotel_new_zdown_grid2[i])
    time.sleep(0.5)
    c9.bernoulli_off()
    c9.goto(slide_hotel_new_zup_grid2[i])
    time.sleep(0.5)
    c9.goto(slide_hotel_new_out_zup_grid2[i])
    time.sleep(0.5)

# for i in [7,21]:
#     c9.goto(slide_hotel_new_out_zup_grid2[i]) # Grab first slide
#     time.sleep(1)
#     c9.goto(slide_hotel_new_zup_grid2[i])
#     time.sleep(1)
#     c9.goto(slide_hotel_new_zdown_grid2[i])
#     time.sleep(0.5)
#     c9.bernoulli_on()
#     time.sleep(1)
#     c9.goto(slide_hotel_new_zup_grid2[i])
#     time.sleep(0.5)
#     c9.goto(slide_hotel_new_out_zup_grid2[i])
#     time.sleep(0.5)
#     
#     c9.goto_safe(ECell_char_out)
#     time.sleep(0.5)
#     c9.goto(ECell_char)
#     time.sleep(0.5)
#     c9.bernoulli_off()
#     time.sleep(5)
#     c9.bernoulli_on()
#     time.sleep(1)
#     c9.goto(ECell_char_out)

#     c9.goto(slide_hotel_new_out_zup_grid2[i]) # Return to first slide position
#     time.sleep(0.5)
#     c9.goto(slide_hotel_new_zup_grid2[i])
#     time.sleep(0.5)
#     c9.goto(slide_hotel_new_zdown_grid2[i])
#     time.sleep(0.5)
#     c9.bernoulli_off()
#     c9.goto(slide_hotel_new_zup_grid2[i])
#     time.sleep(0.5)
#     c9.goto(slide_hotel_new_out_zup_grid2[i])
#     time.sleep(0.5)