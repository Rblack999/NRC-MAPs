import serial
import struct
import time
# Try to keep consistent with c9. structure

# Initiate with something like depo = ECell(deposition)
# Then call methods on cell, depo.open(), depo.close() etc.

cell_list =  ['deposition',
              'characterization']

class ECell:       
    #Check if proper cell name is added
    def __init__(self, cell_name, com_port):
        
        self.com_port = com_port

        if cell_name in cell_list:
            self.cell_name = cell_name 
        else:
            raise NameError(f'cell name not recognized, please select from {cell_list}')
        
        # commands for stepper slider
        self.command_GetVersion_Query = b'\x10\x02\x00\x88\x07\x01\xA2'

        self.command_StepperSlider_Deposition_Set = b'\x10\x02\x00\x88\x08\x0c\x00\xAE'
        self.command_StepperSlider_Characterization_Set = b'\x10\x02\x00\x88\x08\x0c\x01\xAF'
        self.command_TravelSettings_BothSafe_Set = b'\x10\x02\x00\x88\x1A\x07\x00\x00\x00\x00\x00\x00\x00\x88\xb8\x00\x00\xff\x00\x00\x00\x64\x00\x9c\x40\x3a'
        self.command_TravelSettings_Characterization_Set = b'\x10\x02\x00\x88\x1A\x07\x00\x00\x00\x00\x00\x00\x00\xA0\x28\x00\x00\xff\x00\x00\x00\x64\x00\xAC\xA8\x3A'
        self.command_TravelSettings_Deposition_Set = b'\x10\x02\x00\x88\x1A\x07\x00\x00\x00\x00\x00\x00\x00\xA3\x48\x00\x00\xff\x00\x00\x00\x64\x00\xA5\xA0\x4E'
        #self.command_TravelSettings_Deposition_Set = b'\x10\x02\x00\x88\x1A\x07\x00\x00\x00\x00\x00\x00\x00\x99\x20\x00\x00\xff\x00\x00\x00\x64\x00\xA5\xA0\x1c' - this has depo slide = 39200
        # Current settings - Char Full = 44200, Char Slide = 41000
        # Current settings - Depo Full = 42400, Depo Slide = 41800
        # Consult Manish's instructions to figure out where the high and mid byte go, and use calc go decimial (eg. 39200) --> hex (99/20)
        # When setting the strings, the last hex number is the CR and checks the summation of all previous hex values
        # 1. Add up all the numbers in the string except the last, change to decimal, use mod --> 256 on the calc, and then the last hex number is added to the string
        self.command_MoveCommand_JogPlus_Exe = b'\x10\x02\x00\x88\x08\x04\x10\xB6'
        self.command_MoveCommand_JogMinus_Exe = b'\x10\x02\x00\x88\x08\x04\x20\xC6'
        self.command_MoveCommand_Stop_Exe = b'\x10\x02\x00\x88\x08\x04\x02\xa8'
        self.command_MoveCommand_Home_Exe = b'\x10\x02\x00\x88\x08\x04\x04\xaa'
        self.command_MoveCommand_PinSlide_Exe = b'\x10\x02\x00\x88\x08\x04\x08\xae'
        self.command_MoveCommand_FullClose_Exe = b'\x10\x02\x00\x88\x08\x04\x40\xe6'

        # Tuple couplings of commands above
        self.tuple_GetVersion_Query = (self.command_GetVersion_Query, 11) # x0B

        self.tuple_StepperSlider_Deposition_Set = (self.command_StepperSlider_Deposition_Set, 0)
        self.tuple_StepperSlider_Characterization_Set = (self.command_StepperSlider_Characterization_Set, 0)
        self.tuple_TravelSettings_BothSafe_Set = (self.command_TravelSettings_BothSafe_Set, 26) # x1A
        self.tuple_TravelSettings_Characterization_Set = (self.command_TravelSettings_Characterization_Set, 26) # x1A
        self.tuple_TravelSettings_Deposition_Set = (self.command_TravelSettings_Deposition_Set, 26) # x1A

        self.tuple_Command_MoveCommand_JogPlus_Exe = (self.command_MoveCommand_JogPlus_Exe, 0)
        self.tuple_Command_MoveCommand_JogMinus_Exe = (self.command_MoveCommand_JogMinus_Exe, 0)
        self.tuple_Command_MoveCommand_Stop_Exe = (self.command_MoveCommand_Stop_Exe, 0)
        self.tuple_Command_MoveCommand_Home_Exe = (self.command_MoveCommand_Home_Exe, 0)

        self.tuple_Command_MoveCommand_PinSlide_Exe = (self.command_MoveCommand_PinSlide_Exe, 0)
        self.tuple_Command_MoveCommand_FullClose_Exe = (self.command_MoveCommand_FullClose_Exe, 0)

        # -----Initiate stepper slider-------
        # Connect via comport indicated TODO - how to check if comport is open
        self.ser = serial.Serial(
                port=self.com_port,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
        print(self.ser.isOpen())

        time.sleep(5) # Give time to open communication

        # --- Sending of proper settings to control the cell
        # TODO - print the responses a little more clear of the step this does
    def set_up_deposition(self):
        
        data = self.tuple_StepperSlider_Deposition_Set

        self.ser.write(data[0])
        if(data[1] != 0):
            print("Received")
            s = self.ser.read(data[1])
            print(s)
        else:
            print("Sent")

        time.sleep(1)

        data = self.tuple_TravelSettings_Deposition_Set

        self.ser.write(data[0])
        if (data[1] != 0):
            print("Received")
            s = self.ser.read(data[1])
            print(s)
        else:
            print("Sent")
            
        time.sleep(1)

    def set_up_characterization(self):
        
        data = self.tuple_StepperSlider_Characterization_Set

        self.ser.write(data[0])
        if(data[1] != 0):
            print("Received")
            s = self.ser.read(data[1])
            print(s)
        else:
            print("Sent")

        time.sleep(1)

        data = self.tuple_TravelSettings_Characterization_Set

        self.ser.write(data[0])
        if (data[1] != 0):
            print("Received")
            s = self.ser.read(data[1])
            print(s)
        else:
            print("Sent")
            
        time.sleep(1)

    def check_ID(self):
        print(f'Currently connected to cell {self.cell_name}')

    def cell_open(self):  # Open the cell to home position
        
        if self.cell_name == 'deposition':

            self.set_up_deposition()

        if self.cell_name == 'characterization':

            self.set_up_characterization() #Set up deposition travel settings
            
        data = self.tuple_Command_MoveCommand_Home_Exe # Cell will move to home position

        self.ser.write(data[0])
        if (data[1] != 0):
            print("Received")
            s = self.ser.read(data[1])
            print(s)
        else:
            print("Sent")
                
        time.sleep(10) #Time to let the cell move into position


    def cell_close_slide(self):
        # String command to close the cell to heigh with slide in it
        # Cell will move to correct position based on initial cell ID during Ecell object instantiation

        if self.cell_name == 'deposition':

            self.set_up_deposition() #Set up deposition travel settings

        if self.cell_name == 'characterization':

            self.set_up_characterization() #Set up deposition travel settings

        data = self.tuple_Command_MoveCommand_PinSlide_Exe

        self.ser.write(data[0])
        if (data[1] != 0):
            print("Received")
            s = self.ser.read(data[1])
            print(s)
        else:
            print("Sent")
            
        time.sleep(10) #Time to let the cell move into position


    def cell_close_full(self):
        # String command to fully close the cell
        # Cell will move to correct position based on initial cell ID during Ecell object instantiation
        
        if self.cell_name == 'deposition':

            self.set_up_deposition() #Set up deposition travel settings

        if self.cell_name == 'characterization':

            self.set_up_characterization() #Set up deposition travel settings

        data = self.tuple_Command_MoveCommand_FullClose_Exe

        self.ser.write(data[0])
        if (data[1] != 0):
            print("Received")
            s = self.ser.read(data[1])
            print(s)
        else:
            print("Sent")
            
        time.sleep(10) #Time to let the cell move into position

    # TODO def cell_flush(self):
        # Check to ensure this follows a cell_close_full command?  Perhaps a way to check or read back the last
        # last string sent to ensure closed? Or read back the encoder to ensure it is in the correct position?

    def disconnect(self):
        self.ser.close()
        print('PORT CLOSED')
        time.sleep(2)

# ---------------------------------------------------------------------------------


# class potentiostat: #Want to put in the ECell class? Or at least have it inherent? 
# Will have two levels = developer level and then 'campaign' run level
# So will likely have in ECell as something simply like depo.run_echem()