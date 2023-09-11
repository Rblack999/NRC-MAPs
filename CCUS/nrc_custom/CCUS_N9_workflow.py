from north_c9 import NorthC9
#from Locator import *
from ftdi_serial import Serial
from nrc_custom.Ecell_package import ECell
from nrc_custom.Dispense_Procedure import DispenseProcedure
#from PStatRun import pstat_run
import time
import json
import asyncio
from alicat import FlowController

class N9_Workflow: 
    def __init__(self, 
                 c9, 
                 root_path: str,
                 experiment_name: str,
                 exp_count: int, 
                 dispense_concentration: int, 
                 com_port_Ecell: str, 
                 depo_flow_controller_com_port: str):
        
        self.root_path = root_path
        self.experiment_name = experiment_name
        self.exp_count = exp_count
        self.c9 = c9
        self.com_port_Ecell = com_port_Ecell
        self.depo_flow_controller_com_port = depo_flow_controller_com_port
        self.dispense_concentration = dispense_concentration
        
        if type(self.dispense_concentration) != int:
                raise TypeError('dispense_concentration must be an integer')

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
        depo = ECell("deposition", f'{self.com_port_Ecell}')
        depo.cell_open()
        time.sleep(7)
        depo.disconnect
    
    def open_char(self):
        depo = ECell("characterization", f'{self.com_port_Ecell}')
        depo.cell_open()
        time.sleep(7)
        depo.disconnect
    
    def load_depo(self):
        #Declare deposition cell stepper slider
        depo = ECell("deposition", f'{self.com_port_Ecell}')
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
        char = ECell("characterization", f'{self.com_port_Ecell}')
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
        char = ECell("characterization", f'{self.com_port_Ecell}')
        
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
        depo = ECell("deposition", f'{self.com_port_Ecell}')
       
        while True:

            user_input = input("Remove solution in cell - Type 'continue' to proceed: ")

            if user_input.lower() == 'continue':

                break

            else:

                print("You need to type 'continue' to proceed.")

        depo.cell_open()
        time.sleep(5)
        depo.disconnect()
    
    def auto_deposition(self):

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
        
        p1 = DispenseProcedure(1, 0.5, 1, 0, self.c9)
        p1.home_carousel_axis()  # Initial homing of the carousel

        px = []
        px.append(DispenseProcedure(4, self.dispense_concentration, 1, 0, self.c9))

        for dispense_num in range(len(px)):  # must match the above
            print("\n\n*** Pump usage : " + str(dispense_num + 100))
            p1 = px[dispense_num]
            if X_choice[dispense_num] == 0:
               pass
            p1.catalyst_procedure(dispense_num)
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
        self.c9.aspirate_ml(5,9)
        self.c9.delay(5)
        self.c9.set_pump_valve(5,1)
        self.c9.delay(5)
        self.c9.dispense_ml(5,9)
        self.c9.delay(5)
        self.c9.set_pump_speed(5,5)

        print("running pulse protocol")
        for pulse_num in range(3):
            self.c9.aspirate_ml(5, 3)
            self.c9.delay(3)
            self.c9.dispense_ml(5, 3)
            self.c9.delay(3)

        self.c9.set_pump_speed(5,15)
        pstat_run(campaign_name, 'depo')
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
        self.load_depo()
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
        self.c9.goto_safe(Vial_Rack[ExpNum])
        self.c9.open_gripper()

        while True:

            user_input = input("Type 'continue' to proceed: ")

            if user_input.lower() == 'continue':

                break

            else:

                print("You need to type 'continue' to proceed.")
                    

    def auto_char(self):
        
        #Fill Characterization Chamber with 0.5 M KHCO3
        self.c9.set_pump_valve(6, 0)
        self.c9.aspirate_ml(6, 12)
        self.c9.delay(5)
        self.c9.set_pump_valve(6, 1)
        self.c9.delay(5)
        self.c9.dispense_ml(6, 12)
        self.c9.delay(5)
        
        # The following is to turn the flow controller on and off
        # await self.depo_flow_cont.set_flow_rate(20)
        # time.sleep(10)
        # await self.depo_flow_cont.set_flow_rate(0)
        # await self.depo_flow_cont.close()

        self.c9.set_pump_speed(6, 5)

        #Pulsing protocol
        print("running pulse protocol")
        for pulse_num in range(3):
            self.c9.aspirate_ml(6, 3)
            self.c9.delay(3)
            self.c9.dispense_ml(6, 3)
            self.c9.delay(3)

        self.c9.delay(3)
        pstat_run(campaign_name,'char')
        print("ECSA and CA complete")
        
        self.c9.set_pump_speed(6,10)
        self.c9.delay(5)
        
        #Remove solution and home
        self.c9.aspirate_ml(6,12)
        self.c9.delay(5)
        self.c9.set_pump_valve(6,2)
        self.c9.delay(5)
        self.c9.dispense_ml(6,12)
        self.c9.delay(5)
        self.c9.home_pump(6)
        
        #Human in loop. Remove solution with a dropper and let the cell open
        print("60s delay to remove remaining solution and open cell remotely")
        self.c9.delay(60)
        #work in a cell open and close button for this.

    async def CO2purge(self):
        async with FlowController(f'{self.depo_flow_controller_com_port}') as flow_controller:
            print(await flow_controller.get())
            await flow_controller.set_gas('CO2')
            await flow_controller.set_flow_rate('20.0')
            await asyncio.sleep(10)
            await flow_controller.set_flow_rate('0')
            await flow_controller.close()

    def auto_purge(self):
        asyncio.run(self.CO2purge())
    #     #await self.CO2purge()
    #    pass
    
    # def run_workflow():
    #     N9_workflow.homing_procedure()
    #     N9_workflow.load_char()
    #     N9_workflow.auto_deposition()
    #     N9_workflow.remove_char()
    #     N9_workflow.load_depo()
    #     N9_workflow.auto_char()
    #     N9_workflow.remove_depo()