from north_c9 import NorthC9
#from Locator import *
from ftdi_serial import Serial
from nrc_custom.Ecell_package import ECell
from nrc_custom.Dispense_Procedure import DispenseProcedure
from nrc_custom.PStatRun import pstat_run
import time
import json
import asyncio
from alicat import FlowController

class N9_Workflow: 
    def __init__(self, 
                 c9, 
                 root_path: str,
                 experiment_name: str,
                 exp_count, 
                 dispense_concentration: float, 
                 com_port_Ecell: str, 
                 depo_flow_controller_com_port: str):
        
        self.root_path = root_path
        self.experiment_name = experiment_name
        self.exp_count = exp_count
        self.c9 = c9
        self.com_port_Ecell = com_port_Ecell
        self.depo_flow_controller_com_port = depo_flow_controller_com_port
        self.dispense_concentration = dispense_concentration
        
        if type(self.dispense_concentration) != float:
                raise TypeError('dispense_concentration must be a float')

    def homing_procedure(self):

        #home robot
        print("homing robot")
        self.c9.home_robot()

        #declare pump 0
        self.c9.pumps[0]['volume'] = 5
        print("Declare pump0")
        self.c9.home_pump(0)
        self.c9.delay(5)
        print("pump0 homed")

        #declare pump 4
        self.c9.pumps[4]['volume'] = 0.5
        print("Declare pump4")
        self.c9.home_pump(4)
        self.c9.delay(5)
        print("pump4 homed")

        #declare pump 5 (deposition)
        self.c9.pumps[5]['volume'] = 12
        print("Declare pump5")
        self.c9.home_pump(5)
        self.c9.delay(5)
        print("pump5 homed")

        #declare pump 7 (Wash)
        self.c9.pumps[7]['volume'] = 12
        print("Declare pump7")
        self.c9.home_pump(7)
        self.c9.delay(5)
        print("pump7 homed")

        #declare pump 6 (Characterization)
        self.c9.pumps[6]['volume'] = 12
        print("Declare pump6")
        self.c9.home_pump(6)
        self.c9.delay(5)
        print("pump6 homed")

        #Fully open the deposition and characterization cell
        self.open_depo()
        self.open_char()
    
    def open_depo(self):
        depo = ECell("characterization", f'{self.com_port_Ecell}')
        depo.cell_open()
        time.sleep(7)
        depo.disconnect
    
    def open_char(self):
        depo = ECell("deposition", f'{self.com_port_Ecell}')
        depo.cell_open()
        time.sleep(7)
        depo.disconnect
    
    def load_depo(self):
        #Declare deposition cell stepper slider
        depo = ECell("characterization", f'{self.com_port_Ecell}')
        depo.cell_open()

        while True:

            user_input = input("Is cell loaded? Type 'continue' to proceed: ")

            if user_input.lower() == 'continue':

                break

            else:

                print("You need to type 'continue' to proceed.")

        depo.cell_close_slide()
        depo.disconnect()
    
    def load_char(self):
        #Declare deposition cell stepper slider
        char = ECell("deposition", f'{self.com_port_Ecell}')
        char.cell_open()
       
        while True:

            user_input = input("Is cell loaded? Type 'continue' to proceed: ")

            if user_input.lower() == 'continue':

                break

            else:

                print("You need to type 'continue' to proceed.")
        
        char.cell_close_slide()
        char.disconnect()

    def remove_char(self):
        #Declare deposition cell stepper slider
        char = ECell("deposition", f'{self.com_port_Ecell}')
        
        while True:

            user_input = input("Remove solution in cell - Type 'continue' to proceed: ")

            if user_input.lower() == 'continue':

                break

            else:

                print("You need to type 'continue' to proceed.")
        
        char.cell_open()
        time.sleep(5)
        char.disconnect()
    
    def remove_depo(self):
        #Declare deposition cell stepper slider
        depo = ECell("characterization", f'{self.com_port_Ecell}')
       
        while True:

            user_input = input("Remove solution in cell - Type 'continue' to proceed: ")

            if user_input.lower() == 'continue':

                break

            else:

                print("You need to type 'continue' to proceed.")

        depo.cell_open()
        time.sleep(5)
        depo.disconnect()

    def run_pstat_depo(self):
        pstat_run(self.experiment_name, 'depo')

    def run_pstat_char(self):
        pstat_run(self.experiment_name, 'char')

    def run_pstat_perf(self):
        pstat_run(self.experiment_name, 'perf')

    def auto_deposition(self):
        #Need to import the Locator table within this function to have access to all of the variables for N9 item positions, can't use * as that is only at the module level
        #In the future consider wrapping this into a dictionary and assign to a single variable as opposed to importing each individual variable fromt the list
        from nrc_custom.Locator import WeighScale_Adj
        from nrc_custom.Locator import Final_loc
        from nrc_custom.Locator import PipetteRack_LowRow1
        from nrc_custom.Locator import Avoid_Sliderack
        from nrc_custom.Locator import WeighScale_Pipette
        from nrc_custom.Locator import Edep_Cell
        from nrc_custom.Locator import Avoid_Sliderack
        from nrc_custom.Locator import PipetteRemover_Preposition
        from nrc_custom.Locator import PipetteRemover
        from nrc_custom.Locator import PipetteRemover_Off
        from nrc_custom.Locator import WeighScale_Adj_Recap
        from nrc_custom.Locator import Vial_Rack

        p1 = DispenseProcedure(1, 0.5, 1, 0, self.c9)
        p1.home_carousel_axis()  # Initial homing of the carousel

        #Grabs a vial from exp_count position
        self.c9.goto_safe(Vial_Rack[self.exp_count])
        self.c9.delay(5)
        self.c9.close_gripper()

        #Deliver vial to weighscale
        self.c9.goto_safe(WeighScale_Adj)
        self.c9.delay(5)
        self.c9.close_clamp()
        self.c9.delay(5)
        self.c9.uncap()
        self.c9.goto_safe(Final_loc)
        self.c9.open_clamp()

        #weighing and pumping procedure here

        # TODO - add the update based on the experimental output
        # Below does the carousal and liquid dispensing into a vial

        px = []
        px.append(DispenseProcedure(4, self.dispense_concentration, 1, 0, self.c9))

        for dispense_num in range(len(px)):  # must match the above
            print("\n\n*** Pump usage : " + str(dispense_num + 100))
            p1 = px[dispense_num]
            p1.catalyst_procedure(dispense_num, p1)
            time.sleep(2)

        p1.home_carousel_axis()
        self.c9.delay(5)

        self.load_depo()
        print("Closing deposition cell")
        time.sleep(5)
        print("deposition cell closed")
        
        #Pipettes from weightscale
        self.c9.goto_safe(PipetteRack_LowRow1[self.exp_count])  # origin should be PipetteTip_0
        self.c9.delay(5)
        self.c9.goto_safe(Avoid_Sliderack)
        self.c9.delay(1)
        self.c9.close_clamp()
        self.c9.delay(1)
        self.c9.goto_safe(WeighScale_Pipette)  # account for pipette position
        
        #injection procedure into deposition chamber
        #No need to change valves. Just aspirate and dispense
        self.c9.set_pump_valve(0,0)
        self.c9.delay(5)
        self.c9.aspirate_ml(0,1)  # Syringe open. Draws in liquid
        print("drawing solution")
        self.c9.delay(5)
        self.c9.goto_safe(Final_loc)
        self.c9.delay(2)
        self.c9.open_clamp()
        self.c9.delay(2)
        self.c9.goto_safe(Edep_Cell)  # put Edep hole here
        self.c9.delay(2)
        self.c9.dispense_ml(0,1)  # Syringe closed
        print("dispensing solution")
        self.c9.delay(5)
        print("Homing pump")
        self.c9.home_pump(0)
        print("Done injection")

        #Dilution with HCl, deposition, washing
        self.c9.set_pump_valve(5,0)
        self.c9.delay(5)
        self.c9.aspirate_ml(5,9)
        self.c9.delay(5)
        self.c9.set_pump_valve(5,1)
        self.c9.delay(5)
        self.c9.dispense_ml(5,9)
        self.c9.delay(5)
        self.c9.set_pump_speed(5,5)
        self.c9.delay(5)

        print("running pulse protocol")
        for pulse_num in range(3):
            self.c9.aspirate_ml(5,5)
            self.c9.delay(3)
            self.c9.dispense_ml(5,5)
            self.c9.delay(3)

        self.c9.set_pump_speed(5,10)
        pstat_run(self.experiment_name, 'depo')
        print("electrodeposition complete")

        #Puts deposition solution into waste
        self.c9.aspirate_ml(7, 12)
        self.c9.delay(5)
        self.c9.set_pump_valve(7, 2)
        self.c9.delay(5)
        self.c9.dispense_ml(7, 12)

        print("Wash cycle commencing")
        #7 is wash pump in depo
        
        Wash_Cycle_Done = 3

        for Wash_Cycle_Num in range(Wash_Cycle_Done):
            self.c9.delay(5)
            self.c9.set_pump_valve(7, 0)
            self.c9.delay(5)
            self.c9.aspirate_ml(7, 12)
            self.c9.delay(5)
            self.c9.set_pump_valve(7, 1)
            self.c9.delay(5)
            self.c9.dispense_ml(7, 12)
            self.c9.delay(5)
            self.c9.aspirate_ml(7, 12)
            self.c9.delay(5)
            self.c9.set_pump_valve(7, 2)
            self.c9.delay(5)
            self.c9.dispense_ml(7, 12)
            Wash_Cycle_Num += 1
            print("Wash cycle" + str(Wash_Cycle_Num))

        Wash_Cycle_Num = 0  # resets the wash cycle number to zero
        self.c9.delay(5)
        self.c9.home_pump(7)
        self.c9.delay(5)

        #open deposition cell
        self.remove_depo()
        print("deposition cell open")

        #Pipette removal procedures
        self.c9.goto_safe(Avoid_Sliderack)
        self.c9.delay(1)
        self.c9.goto_safe(PipetteRemover_Preposition)
        print("Prepositioning near pipette remover")
        self.c9.goto(PipetteRemover)
        print("Moving into position")
        self.c9.goto(PipetteRemover_Off)
        print("Pipette tip removed")
        self.c9.delay(3)

        #Recapping and homing
        self.c9.close_clamp()
        self.c9.goto_safe(WeighScale_Adj_Recap)
        self.c9.cap()
        print("capping")
        self.c9.open_clamp()
        print("returning vial")
        self.c9.goto_safe(Vial_Rack[self.exp_count])
        self.c9.open_gripper()

        while True:

            user_input = input("Type 'continue' to proceed: ")

            if user_input.lower() == 'continue':

                break

            else:

                print("You need to type 'continue' to proceed.")
                    

    def auto_char(self):
        
        #code here to load cell
        self.load_char()

        #Fill Characterization Chamber with 0.5 M KHCO3
        self.c9.set_pump_valve(6, 0)
        self.c9.aspirate_ml(6, 12)
        self.c9.delay(5)
        self.c9.set_pump_valve(6, 1)
        self.c9.delay(5)
        self.c9.dispense_ml(6, 12)
        self.c9.delay(10)
        
        # The following is to turn the flow controller on and off
        #await self.depo_flow_cont.set_flow_rate(20)
        #time.sleep(10)
        #await self.depo_flow_cont.set_flow_rate(0)
        #await self.depo_flow_cont.close()
        
        print("purging resevoir with CO2 for 720s")
        self.auto_purge()
        self.c9.delay(5)
        #there seems to be an error here causing a buffer overload
        #self.c9.set_pump_speed(6,5)
        #self.c9.delay(5)

        #Pulsing protocol
        print("running pulse protocol")
        for pulse_num in range(3):
            self.c9.aspirate_ml(6,3)
            self.c9.delay(7)
            self.c9.dispense_ml(6,3)
            self.c9.delay(7)

        self.c9.delay(3)
        pstat_run(self.experiment_name, 'char')
        print("ECSA and CO2R complete")
        
        #self.c9.set_pump_speed(6,10)
        #self.c9.delay(5)
        
        #Remove solution and home
        self.c9.aspirate_ml(6,12)
        self.c9.delay(5)
        self.c9.set_pump_valve(6,2)
        self.c9.delay(5)
        self.c9.dispense_ml(6,12)
        self.c9.delay(5)
        self.c9.home_pump(6)
        
        #Human in loop. Remove solution with a dropper and let the cell open
        self.remove_char()
        

    #For some reason, the flow controller goes through com 13 rather than com 3. The location of the USB hub.
    async def CO2purge(self):
        async with FlowController('COM13') as flow_controller:
            print(await flow_controller.get())
            await flow_controller.set_gas('CO2')
            await flow_controller.set_flow_rate(20.0)
            await asyncio.sleep(5) #RB changed to 5 seconds to save time
            await flow_controller.set_flow_rate(0)
            await flow_controller.close()

    def auto_purge(self):
        asyncio.run(self.CO2purge())
        #await self.CO2purge()
    #    pass