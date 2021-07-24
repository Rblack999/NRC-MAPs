from north_c9 import NorthC9
from Locator import *
from ftdi_serial import Serial
import time # needed for time.sleep

print(Serial.list_device_serials())

c9 = NorthC9('A')

# Desc : Code Snippet A
# this is for setting the pressure on the compressor
# note : it has to be set when the bernoulli gripper is on.
# c9.bernoulli_on()
# time.sleep(20)
# c9.bernoulli_off()

# Desc : Code Snippet B
# this is for closing the robot gripper to hold the vacuum gripper for location acquisition
# time.sleep(8)
# c9.close_gripper()

# ---- VACUUM GRIPPER ----
# Desc : This program uses the Vacuum gripper to pick up a glass slide from the top right
# hand corner of the slide hotel and deposits it into the Characterization cell of the
# stepper slider when the slider is at its HOME (down) position.

# Things to setup before running the program
#          : Uncomment the block up top labelled "Code Snippet A" and the Vacuum gripper should
#            be running.  Set the pressure at the Compressor to 70 psi _when running_.  Vacuum
#            gripper will then turn off after 20 seconds and pressure on the Compressor when
#            Vacuum gripper is not running should read 90 psi.  High pressure is needed for the
#            Vacuum gripper to pick up a slide successfully from its edge apparently.

# Things to remember before you run the program
#          : Make sure you have placed a slide in the top right of the slide hotel.
#          : Make sure you remove the slide from the Characterization cell
#          : Make sure the vacuum gripper is in its holder
#          : Make sure the chacterization cell is at its home position



# ***********************************************************************************************
# We are now at the Home position

c9.home_robot() # home robot
time.sleep(1)

# ***********************************************************************************************
# We are now at the vacinity of the Vacuum Gripper holder

c9.goto_safe(Vacuum_Grip_Pickup) # lets go pick up the vacuum gripper
time.sleep(1)

c9.close_gripper() # ok we've picked it up
time.sleep(1)

# ***********************************************************************************************
# We are now at the Slide Hotel - more specifically the top right corner to pick up a slide

c9.goto_safe(Vacuum_SlideHotel_Pickup_Exit_TR) # navigate to stand off point at slide hotel for slide pickup
time.sleep(2)

time.sleep(1)
c9.goto(Vacuum_SlideHotel_Pickup_Entry_TR) # lets move into the room housing the slide of the slide hotel
time.sleep(1)

time.sleep(1)
c9.bernoulli_on()

c9.goto(Vacuum_SlideHotel_Pickup_Entry_Down_TR) # turn on the vacuum gripper and make contact with the slide.
time.sleep(2)  # this delay is to ensure a good vacuum grip before we try to lift the slide.

c9.goto(Vacuum_SlideHotel_Pickup_Entry_TR) # pick up the slide vertically by moving back up to our initial position 
time.sleep(2)

time.sleep(1)
c9.goto(Vacuum_SlideHotel_Pickup_Exit_TR) # back out to stand off point at slide hotel
time.sleep(2)

# ***********************************************************************************************
# We are now at the Stepper Slider - more specifically the Characterization Cell

c9.goto_safe(Stepper_Slider_A_Exit) 
time.sleep(2)

c9.goto(Stepper_Slider_A_Enter)
time.sleep(2)

c9.bernoulli_off()
time.sleep(2)

c9.goto(Stepper_Slider_A_Exit)
time.sleep(2)

c9.goto_safe(Vacuum_Grip_Pickup)
time.sleep(1)

c9.open_gripper()
time.sleep(1)

# ***********************************************************************************************
# We are now at the Home position

c9.home_robot()


