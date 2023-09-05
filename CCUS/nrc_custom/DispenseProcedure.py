from north_c9 import NorthC9
from Locator import *
from ftdi_serial import Serial
import time # needed for c9.delay

class DispenseProcedure:
    # **********************************************************************************************
    # Constructor definition
    def __init__(self,pumpnum,target_wgt,carouselsink,carouseldump):
        
        self.pumpnum = pumpnum # 9
        self.target_wgt = target_wgt
        
        self.carouselsink = carouselsink #3 - Count from 1.  Sink position changes depending on which sink port we want to dispense.
        self.carouseldump = carouseldump #2 - Count from 1.  Dump position does not change 

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
        
        if ((rot_deg > 330) or (z_mm > 160)):
            return
        c9.move_axis(CAROUSEL_Z, 0, vel, accel)
        c9.move_axis(CAROUSEL_ROT, int(rot_deg*(51000/360)), vel, accel)
        c9.move_axis(CAROUSEL_Z, int(z_mm*(40000/160)), vel, accel) # vel = counts/sec, accel = counts/sec2

    # Desc : Obtain stable weight of liquid in vial.  Note - mass balance has to be zeroed first.
    def measure_weight(self):
        c9.clear_scale()
        c9.delay(2) # delay enables any drops travelling down the tube fall into the vial
        st = c9.read_steady_scale()
        print(st)
        index = 0
        weight = 0
        
        c9.delay(2)
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
        c9.home_axis(4)
        c9.home_axis(6)

    # Desc : Clears and zeroes the mass balance.    
    def zero_weigh_scale(self):
        c9.delay(1)
        c9.clear_scale()
        c9.zero_scale()
    
#     def catalyst_procedure(self): # blank holder for catalyst procedure
#         pass

# **********************************************************************************************

    def catalyst_procedure(self):
        # --------------------------------------------------------------------
        # Home Both Rotary and Elevation Axis
        #p1.home_carousel_axis()

        # pos represents the position of the carousel dispenser from 1 to 7
        p1.set_carousel_port(p1.carouseldump) 

        # --------------------------------------------------------------------
        # Prime the pump - this is on the Source side

        # First, set the pump and valve to the default valve position
        # NOTE : Default valve position has the valve to the source tank open.
        c9.set_pump_valve(p1.pumpnum,0)

        c9.delay(1)
        c9.home_pump(p1.pumpnum)

        # home the pump (again?!)
        c9.delay(1)
        c9.set_pump_valve(p1.pumpnum,0)

        # suck up X ml from vial
        c9.delay(1)
        c9.aspirate_ml(p1.pumpnum,1) # 1 was 0.5
        c9.delay(2) # almost certainly need this delay for the fluid to be sucked up fully with the negative pump pressure

        # set the pump and switch the valve to the dispense position
        c9.set_pump_valve(p1.pumpnum,1)

        # dispense X ml from vial
        c9.delay(1)
        c9.dispense_ml(p1.pumpnum,1)
        c9.delay(2) # need this delay as there are still some drops falling as the tube dispenses the fluid with positive pump pressure

        # set the pump and switch the valve back to default valve position
        c9.set_pump_valve(p1.pumpnum,0)
        c9.delay(1)

        # --------------------------------------------------------------------
        # Move to the Sink

        # Move Carousel to position where it will Dispense into Vial
        p1.set_carousel_port(p1.carouselsink)

        # --------------------------------------------------------------------
        # Have the pump suck up a full cylinder of fluid from Source

        # First, set the pump and valve to the default valve position (just in case)
        # NOTE : Default valve position has the valve to the source tank open.
        c9.set_pump_valve(p1.pumpnum,0)
        c9.delay(1)

        # suck up X ml from source
        c9.aspirate_ml(p1.pumpnum,1) # 1 was 0.5
        c9.delay(2) # almost certainly need this delay for the fluid to be sucked up fully with the negative pump pressure

        # set the pump and switch the valve to the dispense position
        c9.set_pump_valve(p1.pumpnum,1)
        c9.delay(1)

        # -------------------------------------------------------------

        # Zero the weight scale with the empty vial
        # We are about to measure (by weight) how much liquid we have dispensed  
        p1.zero_weigh_scale()

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

            c9.dispense_ml(p1.pumpnum,dispvar)

            wgt = p1.measure_weight()
            #print(wgt)

            # if pump has dispensed more than 3/4 of its volume, dump the remainder and refill (re-prime) the pump
            if(addon_disp > 0.9):     
                p1.set_carousel_port(p1.carouseldump) # move to the position of the fluid dump receptical

                c9.delay(1)
                c9.home_pump(p1.pumpnum)

                c9.delay(1)
                c9.set_pump_valve(p1.pumpnum,0)

                # suck up X ml from source
                c9.aspirate_ml(p1.pumpnum,1) # fill full cylinder
                c9.delay(2) # almost certainly need this delay for the fluid to be sucked up fully with the negative pump pressure

                # move carousel back over vial
                p1.set_carousel_port(p1.carouselsink)

                # return back to dispensing valve position
                c9.delay(2)
                c9.set_pump_valve(p1.pumpnum,1)
                c9.delay(2)            

                addon_disp = 0 # reset the addon_disp variable since we have filled up the cylinder to 100%
                # we are ready to continue

        print(wgt)

        # --------------------------------------------------------------------

        # Set the pump and switch the valve back to default valve position.
        c9.delay(0.5)
        c9.set_pump_valve(p1.pumpnum,0)
        c9.delay(2)

        # --------------------------------------------------------------------

        # Move to the fluid dump receptical to dump remainder fluid in the pump's cylinder.
        p1.set_carousel_port(p1.carouseldump)

        # --------------------------------------------------------------------

        # Perform the dump of fluid into the fluid dump receiptical.
        c9.home_pump(p1.pumpnum)
        c9.delay(3)

        # --------------------------------------------------------------------

        # Return the carousel rotation and elevation axis to its home position.
        # p1.home_carousel_axis()

    # --------------------------------------------------------------------
    # END

p1 = DispenseProcedure(4,0,0,0) #RB NOTE - is this just an initialization?
p1.home_carousel_axis()
# Create objects of the class
# Pumps - 4, 2, 1, 3, 0

px = []
# px.append(Procedures(4,0.4,1,0)) # pumpnum,target_wgt,carouselsink,carouseldump
# px.append(Procedures(2,0.1,2,1))
# px.append(Procedures(2,0.2,2,1))
px.append(DispenseProcedure(1,0.3,3,2))
#px.append(DispenseProcedure(3,0.2,4,3))

for vial in range(len(px)):  # must match the above
    print("\n\n*** Pump usage : " + str(vial + 100))
    p1 = px[vial]
    p1.catalyst_procedure()
    c9.delay(2)

#p1 = DispenseProcedure(4,0,0,0)
p1.home_carousel_axis()

px = []
# px.append(Procedures(4,0.4,1,0)) # pumpnum,target_wgt,carouselsink,carouseldump
# px.append(Procedures(2,0.1,2,1))
# px.append(Procedures(2,0.2,2,1))
# px.append(DispenseProcedure(1,0.3,3,2))
px.append(DispenseProcedure(3,0.2,4,3))

for vial in range(len(px)):  # must match the above
    print("\n\n*** Pump usage : " + str(vial + 100))
    p1 = px[vial]
    p1.catalyst_procedure()
    c9.delay(2)

#p1 = DispenseProcedure(4,0,0,0)
p1.home_carousel_axis()
# **********************************************************************************************