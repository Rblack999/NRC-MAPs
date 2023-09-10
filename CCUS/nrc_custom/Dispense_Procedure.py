from north_c9 import NorthC9
import time

class DispenseProcedure:
    # **********************************************************************************************
    # Constructor definition
    def __init__(self,pumpnum,target_wgt,carouselsink,carouseldump, c9):
        
        self.pumpnum = pumpnum # 9
        self.target_wgt = target_wgt
        
        self.carouselsink = carouselsink #3 - Count from 1.  Sink position changes depending on which sink port we want to dispense.
        self.carouseldump = carouseldump #2 - Count from 1.  Dump position does not change 
        self.c9 = c9

    # **********************************************************************************************
    # Function definition
    
    # Desc : Reports the settings going into the object made by the Constructor
    def ReportSettings(self):
        print("Object Created : Pump Number {0} is active and Target Weight {1} is requested.".format(self.p1.pumpnum,self.p1.target_wgt))

    # Desc : Moves carousel's axes (rotation and elevation) as defined by incoming variables
    def move_carousel(self, rot_deg, z_mm, vel=None, accel=None):
        #self.rot_deg = rot_deg
        #self.z_mm = z_mm
        #self.vel = vel
        #self.accel = accel

        CAROUSEL_ROT = 4 # rotary
        CAROUSEL_Z = 6 # elevationt
        
        if ((rot_deg > 330) or (z_mm > 160)):
            return
        self.c9.move_axis(CAROUSEL_Z, 0, vel, accel)
        self.c9.move_axis(CAROUSEL_ROT, int(rot_deg*(51000/360)), vel, accel)
        self.c9.move_axis(CAROUSEL_Z, int(z_mm*(40000/160)), vel, accel) # vel = counts/sec, accel = counts/sec2

    # Desc : Obtain stable weight of liquid in vial.  Note - mass balance has to be zeroed first.
    def measure_weight(self):
        self.c9.clear_scale()
        self.c9.delay(2) # delay enables any drops travelling down the tube fall into the vial
        st = self.c9.read_steady_scale()
        print(st)
        index = 0
        weight = 0
        
        self.c9.delay(2)
        weight = st
            
        print("\nFinal stable weight : ", weight)
        return weight

    # Desc : Rotates carousel port to positioned defined by incoming variable.
    #        Checks should be added to function below and tested to ensure port numbers range between 1 and 7 (i.e. not out of range)
    def set_carousel_port(self, pos):
        # pos represents the position of the carousel dispenser from 1 to 7
        self.move_carousel((pos * 45) + 3, 127) # note : the +3 is for the azimuth offset error.  (max vals are 330.0 and 155)
        
    # Desc : Returns carousel axes positions to its home.
    def home_carousel_axis(self):
        # base - rotary (4)
        # top - up/down aka elevation (6)
        self.c9.home_axis(4)
        self.c9.home_axis(6)

    # Desc : Clears and zeroes the mass balance.    
    def zero_weigh_scale(self):
        self.c9.delay(1)
        self.c9.clear_scale()
        self.c9.zero_scale()
    
#     def catalyst_procedure(self): # blank holder for catalyst procedure
#         pass

# **********************************************************************************************
    def prime_pumps(self,p1):
        # pos represents the position of the carousel dispenser from 1 to 7
        p1.set_carousel_port(p1.carouseldump) 

        # --------------------------------------------------------------------
        # Prime the pump - this is on the Source side

        # First, set the pump and valve to the default valve position
        # NOTE : Default valve position has the valve to the source tank open.
        self.c9.set_pump_valve(p1.pumpnum,0)

        self.c9.delay(5)
        self.c9.home_pump(p1.pumpnum)

        # home the pump (again?!)
        #c9.delay(5)
        #c9.set_pump_valve(p1.pumpnum,0)

        # suck up X ml from vial
        self.c9.delay(5)
        self.c9.aspirate_ml(p1.pumpnum,0.5) # 1 was 0.5
        self.c9.delay(15) # almost certainly need this delay for the fluid to be sucked up fully with the negative pump pressure

        # set the pump and switch the valve to the dispense position
        self.c9.set_pump_valve(p1.pumpnum,1)

        # dispense X ml from vial
        self.c9.delay(5)
        self.c9.dispense_ml(p1.pumpnum,0.5)
        self.c9.delay(15) # need this delay as there are still some drops falling as the tube dispenses the fluid with positive pump pressure

        # set the pump and switch the valve back to default valve position
        self.c9.set_pump_valve(p1.pumpnum,0)
        self.c9.delay(5)
        
    def catalyst_procedure(self, dispense_num,p1):
        # Move Carousel to position where it will Dispense into Vial
        # dispense_num is for tracking and recording the weights
        p1.set_carousel_port(p1.carouselsink)

        # --------------------------------------------------------------------
        # Have the pump suck up a full cylinder of fluid from Source

        # First, set the pump and valve to the default valve position (just in case)
        # NOTE : Default valve position has the valve to the source tank open.
        self.c9.set_pump_valve(p1.pumpnum,0)
        self.c9.delay(5)

        # suck up X ml from source
        self.c9.aspirate_ml(p1.pumpnum,0.5) # 1 was 0.5
        self.c9.delay(10) # almost certainly need this delay for the fluid to be sucked up fully with the negative pump pressure
        # set the pump and switch the valve to the dispense position
        self.c9.set_pump_valve(p1.pumpnum,1)
        self.c9.delay(2)

        # -------------------------------------------------------------

        # Zero the weight scale with the empty vial
        # We are about to measure (by weight) how much liquid we have dispensed  
        #Alex added 5 sec of sleep before and after due to packet error
        time.sleep(5)
        p1.zero_weigh_scale()
        time.sleep(10)
        # -------------------------------------------------------------
        # Measuring weight of (incrementally) dispensed fluid on mass balance in a closed feedback loop manner till it hits the weight target.
        # Dispensation quantity of fluid from the pump is stepped down as mass balance approaches its target of 0.050 mL.
        # For distilled water, there is a 1:1 relationship between fluid weight and fluid volume (i.e. 1.000 g = 1.000 mL).
        # Would need to calculate the ratio for fluids of different chemicals accordingly using their concentration (i.e. molar mass).
        # If the fluid pump has already dispensed more than 3/4 of the quantity of fluid in the cylinder, the pump is refilled (re-primed).

        wgt = p1.measure_weight()
        addon_disp = 0
        # p1.target_wgt = 1.000  # use this if you want to over-ride the setting made in the constructor (way up above)
        dispvar = 0.025  # by default, dispense this much mL (the smallest displacement as seen below in the while)

        # we are attempting to hit the targeted weight within 0.01 of the vial's weight reading
        # whereupon we stop dispensing fluid.
        while ((p1.target_wgt - wgt) > 0.005):
            # dispense X ml from vial    
            if (p1.target_wgt - wgt > 0.50):
                dispvar = 0.45     
            elif (p1.target_wgt - wgt > 0.35):
                dispvar = 0.32   
            elif (p1.target_wgt - wgt > 0.15):
                dispvar = 0.12
            elif (p1.target_wgt - wgt > 0.05):
                dispvar = 0.04
            elif (p1.target_wgt - wgt > 0.02):
                dispvar = 0.025
            else:
                dispvar = 0.025

            addon_disp += dispvar

            self.c9.dispense_ml(p1.pumpnum,dispvar)

            wgt = p1.measure_weight()
            #print(wgt)

            # if pump has dispensed more than 3/4 of its volume, dump the remainder and refill (re-prime) the pump
            if(addon_disp > 0.9):     
                p1.set_carousel_port(p1.carouseldump) # move to the position of the fluid dump receptical

                self.c9.delay(5)
                self.c9.home_pump(p1.pumpnum)

                self.c9.delay(5)
                self.c9.set_pump_valve(p1.pumpnum,0)

                # suck up X ml from source
                self.c9.aspirate_ml(p1.pumpnum, 0.5) # fill full cylinder #was 1 now 0.5
                self.c9.delay(10) # almost certainly need this delay for the fluid to be sucked up fully with the negative pump pressure

                # move carousel back over vial
                p1.set_carousel_port(p1.carouselsink)

                # return back to dispensing valve position
                self.c9.delay(5)
                self.c9.set_pump_valve(p1.pumpnum,1) 
                self.c9.delay(5)            

                addon_disp = 0 # reset the adddon_disp variable since we have filled up the cylinder to 100%
                # we are ready to continue

        print(f'mass = {wgt}')
        #dict[f'{experiment_name}'][f'Test_{exp_count}']['Metric']['X_mass'][dispense_num] = wgt # Add final weight to dictionary for tracking

        # --------------------------------------------------------------------

        # Set the pump and switch the valve back to default valve position.
        self.c9.delay(0)
        self.c9.set_pump_valve(p1.pumpnum,0)
        self.c9.delay(2)

        # --------------------------------------------------------------------

        # Move to the fluid dump receptical to dump remainder fluid in the pump's cylinder.
        p1.set_carousel_port(p1.carouseldump)

        # --------------------------------------------------------------------

        # Perform the dump of fluid into the fluid dump receiptical.
        self.c9.home_pump(p1.pumpnum)
        self.c9.delay(5)

        # --------------------------------------------------------------------

        # Return the carousel rotation and elevation axis to its home position.
        # p1.home_carousel_axis()

    # --------------------------------------------------------------------
    # END