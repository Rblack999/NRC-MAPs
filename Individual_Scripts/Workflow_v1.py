from north_c9 import NorthC9
from Locator import *
import time
from nrc_custom.Ecell_package import ECell

#Initialize everything
c9 = NorthC9('A')
c9.home_robot()

c9.pumps[0]['volume']=5 # Set pump parameters and home for the pipette tip
c9.home_pump(0)

Ecell_char = ECell('characterization','COM2') # Initial connection to Ecell
#Ecell_char.cell_open() # Ensure cell is open prior to any experiment

for i in [0]:
    # 1. Grab slide and deposit into ECell
    
    # Grab tool
    c9.goto_safe(tool_mount_copy) 
    c9.close_gripper()
    c9.goto_safe(slide_hotel_new_out_zup_grid2[i])

    # Grab slide at index i 
    c9.goto(slide_hotel_new_out_zup_grid2[i]) 
    time.sleep(1)
    c9.goto(slide_hotel_new_zup_grid2[i])
    time.sleep(1)
    c9.goto(slide_hotel_new_zdown_grid2[i])
    time.sleep(0.5)
    c9.bernoulli_on() # Pick up slide
    time.sleep(1)
    c9.goto(slide_hotel_new_zup_grid2[i])
    time.sleep(0.5)
    c9.goto(slide_hotel_new_out_zup_grid2[i])
    time.sleep(0.5)
    
    # Deposit Slide at characterization cell
    c9.goto_safe(ECell_char_out)
    time.sleep(0.5)
    c9.goto(ECell_char)
    time.sleep(0.5)
    c9.bernoulli_off() # Drop slide
    time.sleep(1)
    c9.goto(ECell_char_out) # Move gripper out
    time.sleep(1)

    # Put bernoulli gripper back into place
    c9.goto_safe(tool_mount_copy) # Put slide back
    c9.open_gripper()
    c9.goto_safe(after_grab_home) # Put robot in safe position to avoid collisions on future actions

    # 2. Close ECell (w/slide)
    Ecell_char.cell_close_slide()

    # 3. Grab vial and load into weight scale
    # Ensure robot is in the right home position - check from previous gripper is open
    c9.goto_safe(vial_rack_all[i])
    c9.close_gripper()
    time.sleep(0.5)
    c9.goto_safe(after_grab_home) # Put robot in safe position to avoid collisions on future actions
    
    c9.open_clamp() # Ensure clamp is open prior to putting vial in
    c9.goto_safe(vial_place_scale) 
    c9.close_clamp()
    c9.uncap()
    c9.move_z(200) # Just move the robot arm up to clear space
    
    # TODO - Weigh balance stuff - would go into this workflow
    c9.open_clamp() 
    time.sleep(1)
    c9.close_clamp()


    # 4. Grab pipette tip and put contents into loaded ECell, remove tip
    c9.goto_safe(after_grab_home) # Put robot in safe position to avoid collisions on future actions

    # pick up a pippet from the pippette holder
    c9.goto_safe(Pipette_rack_initial[i])
    c9.delay(1)
    c9.goto(Pipette_rack_drop[i])
    c9.delay(1)
    c9.goto(Pipette_rack_up[i])
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
    c9.aspirate_ml(0,0.2)

    # move arm up with pippet holding 1 mL
    c9.delay(1)
    c9.goto_safe(MT_Vial_Up)
    c9.delay(1)

    # move pipette tip to ECell and deposit
    c9.goto_safe(char_cell_in) ####Want to rename?
    time.sleep(1)
    c9.dispense_ml(0,0.2)
    time.sleep(1)

    # Remove pipette tip
    c9.goto_safe(after_grab_home) #To avoid collision with ECell
    c9.goto_safe(Pipette_remove_ready)
    c9.goto(Pipette_remove)
    c9.move_z(250)
    c9.goto_safe(after_grab_home) #To avoid collision with ECell

    # 5. Put vial back and away
    c9.goto_safe(vial_place_scale_cap)
    c9.cap()
    c9.open_clamp()
    c9.goto_safe(after_grab_home)
    
    c9.goto_safe(vial_rack_all[i])
    c9.open_gripper()
    c9.move_z(200)

    c9.goto_safe(after_grab_home) #To avoid collision with ECell
    time.sleep(1)

    # Open cell
    Ecell_char.cell_open()