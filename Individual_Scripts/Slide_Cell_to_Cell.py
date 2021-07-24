from north_c9 import NorthC9
from Locator import *
import time
#from nrc_custom.Ecell_package import ECell

#Initialize everything
c9 = NorthC9('A')
c9.home_robot()

# Grab tool
c9.goto_safe(tool_mount_copy) 
c9.close_gripper()
    
for i in [0,7,21,35]:
    # 1. Grab slide and deposit into ECell
    # Grab slide at index i 
    c9.goto_safe(slide_hotel_new_out_zup_grid2[i]) 
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
    c9.goto_safe(ECell_char_out_copy)
    time.sleep(0.5)
    c9.goto(ECell_char_copy)
    time.sleep(0.5)
    c9.bernoulli_off() # Drop slide
    time.sleep(1)
    c9.goto(ECell_char_out_copy) # Move gripper out
    time.sleep(1)

    # Pick slide up again on char cell
    c9.goto(ECell_char_copy)
    time.sleep(0.50)
    c9.bernoulli_on() # Pick up slide
    time.sleep(1)
    c9.goto(ECell_char_out_copy) # Move gripper out

    # Move to deposition cell and drop slide
    c9.goto(ECell_depo_out)
    time.sleep(1)
    c9.goto(ECell_depo)
    time.sleep(0.5)
    c9.bernoulli_off()
    time.sleep(1)
    c9.goto(ECell_depo_out)
    time.sleep(0.5)

    # Pick slide up again on depo cell and return to slide hotel
    c9.goto(ECell_depo)
    time.sleep(1)
    c9.bernoulli_on()
    time.sleep(1)
    c9.goto(ECell_depo_out)

    # Return slide from depo cell back to spot in slide hotel
    c9.goto(slide_hotel_new_out_zup_grid2[i]) 
    time.sleep(1)
    c9.goto(slide_hotel_new_zup_grid2[i])
    time.sleep(1)
    c9.goto(slide_hotel_new_zdown_grid2[i])
    time.sleep(0.5)
    c9.bernoulli_off() # Pick up slide
    time.sleep(1)
    c9.goto(slide_hotel_new_zup_grid2[i])
    time.sleep(0.5)
    c9.goto(slide_hotel_new_out_zup_grid2[i])
    time.sleep(0.5)