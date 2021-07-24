import pyserial
import serial
import struct
import time
# North Robotics = c9 class, as normal
# Try to keep consistent with c9. structure

# Initiate with something like depo = ECell(deposition)
# Then call methods on cell, depo.open(), depo.close() etc.

class Ecell:       
	cell_list =  ['deposition',
				  'characterization']
		
	# commands for stepper slider
	command_GetVersion_Query = b'\x10\x02\x00\x88\x07\x01\xA2'

	command_StepperSlider_Deposition_Set = b'\x10\x02\x00\x88\x08\x0c\x00\xAE'
	command_StepperSlider_Characterization_Set = b'\x10\x02\x00\x88\x08\x0c\x01\xAF'
	command_TravelSettings_BothSafe_Set = b'\x10\x02\x00\x88\x1A\x07\x00\x00\x00\x00\x00\x00\x00\x88\xb8\x00\x00\xff\x00\x00\x00\x64\x00\x9c\x40\x3a'
	command_TravelSettings_Characterization_Set = b'\x10\x02\x00\x88\x1A\x07\x00\x00\x00\x00\x00\x00\x00\x9E\x98\x00\x00\xff\x00\x00\x00\x64\x00\xAB\x18\x17'
	command_TravelSettings_Deposit_Set = b'\x10\x02\x00\x88\x1A\x07\x00\x00\x00\x00\x00\x00\x00\x99\x20\x00\x00\xff\x00\x00\x00\x64\x00\xA5\xA0\x1c'

	command_MoveCommand_JogPlus_Exe = b'\x10\x02\x00\x88\x08\x04\x10\xB6'
	command_MoveCommand_JogMinus_Exe = b'\x10\x02\x00\x88\x08\x04\x20\xC6'
	command_MoveCommand_Stop_Exe = b'\x10\x02\x00\x88\x08\x04\x02\xa8'
	command_MoveCommand_Home_Exe = b'\x10\x02\x00\x88\x08\x04\x04\xaa'
	command_MoveCommand_PinSlide_Exe = b'\x10\x02\x00\x88\x08\x04\x08\xae'
	command_MoveCommand_FullClose_Exe = b'\x10\x02\x00\x88\x08\x04\x40\xe6'

	# Tuple couplings of commands above
	tuple_GetVersion_Query = (command_GetVersion_Query, 11) # x0B

	tuple_StepperSlider_Deposition_Set = (command_StepperSlider_Deposit_Set, 0)
	tuple_StepperSlider_Characterization_Set = (command_StepperSlider_Character_Set, 0)
	tuple_TravelSettings_BothSafe_Set = (command_TravelSettings_BothSafe_Set, 26) # x1A
	tuple_TravelSettings_Characterization_Set = (command_TravelSettings_Character_Set, 26) # x1A
	tuple_TravelSettings_Deposition_Set = (command_TravelSettings_Deposit_Set, 26) # x1A

	tuple_Command_MoveCommand_JogPlus_Exe = (command_MoveCommand_JogPlus_Exe, 0)
	tuple_Command_MoveCommand_JogMinus_Exe = (command_MoveCommand_JogMinus_Exe, 0)
	tuple_Command_MoveCommand_Stop_Exe = (command_MoveCommand_Stop_Exe, 0)
	tuple_Command_MoveCommand_Home_Exe = (command_MoveCommand_Home_Exe, 0)

	tuple_Command_MoveCommand_PinSlide_Exe = (command_MoveCommand_PinSlide_Exe, 0)
	tuple_Command_MoveCommand_FullClose_Exe = (command_MoveCommand_FullClose_Exe, 0)

	#Check if proper cell name is added
	def __init__(self, cell_name, com_port):
		
		self.com_port = com_port

		if cell_name in cell_list:
			self.cell_name = cell_name 
		else:
			raise NameError(f'cell name not recognized, please select from {cell_list}')

		# -----Initiate stepper slider-------
		# Connect via comport indicated TODO - how to check if comport is open
		ser = serial.Serial(
			    port=self.com_port,
			    baudrate=115200,
			    parity=serial.PARITY_NONE,
			    stopbits=serial.STOPBITS_ONE,
			    bytesize=serial.EIGHTBITS
			)
		print(ser.isOpen())

		time.sleep(5) # Give time to open communication

		# --- Sending of proper settings to control the cell
		# TODO - print the responses a little more clear of the step this does
	def set_up_deposition():
		
		data = tuple_StepperSlider_Deposition_Set

		ser.write(data[0])
		if(data[1] != 0):
		    print("Received")
		    s = ser.read(data[1])
		    print(s)
		else:
		    print("Sent")

		time.sleep(1)

		data = tuple_TravelSettings_Deposition_Set

		ser.write(data[0])
		if (data[1] != 0):
		    print("Received")
		    s = ser.read(data[1])
		    print(s)
		else:
		    print("Sent")
		    
		time.sleep(1)

	def set_up_characterization():
		
		data = tuple_StepperSlider_Characterization_Set

		ser.write(data[0])
		if(data[1] != 0):
		    print("Received")
		    s = ser.read(data[1])
		    print(s)
		else:
		    print("Sent")

		time.sleep(1)

		data = tuple_TravelSettings_Characterization_Set

		ser.write(data[0])
		if (data[1] != 0):
		    print("Received")
		    s = ser.read(data[1])
		    print(s)
		else:
		    print("Sent")
		    
		time.sleep(1)

	def check_ID(self):
		print(f'Currently connected to cell {self.cell_name}')

	def cell_open(self):  # Open the cell to home position
		
		if self.cell_name == 'deposition':

			set_up_deposition() #Set up deposition travel settings

		if self.cell_name == 'characterization':

			set_up_characterization() #Set up deposition travel settings
			
	    data = tuple_Command_MoveCommand_Home_Exe # Cell will move to home position

	    ser.write(data[0])
	    if (data[1] != 0):
	        print("Received")
	        s = ser.read(data[1])
	        print(s)
	    else:
	        print("Sent")
		        
		time.sleep(7) #Time to let the cell move into position


	def cell_close_slide(self):
		# String command to close the cell to heigh with slide in it
		# Cell will move to correct position based on initial cell ID during Ecell object instantiation

		if self.cell_name == 'deposition':

			set_up_deposition() #Set up deposition travel settings

		if self.cell_name == 'characterization':

			set_up_characterization() #Set up deposition travel settings

	    data = tuple_Command_MoveCommand_PinSlide_Exe

	    ser.write(data[0])
	    if (data[1] != 0):
	        print("Received")
	        s = ser.read(data[1])
	        print(s)
	    else:
	        print("Sent")
	        
	    time.sleep(7) #Time to let the cell move into position


	def cell_close_full(self):
		# String command to fully close the cell
		# Cell will move to correct position based on initial cell ID during Ecell object instantiation
		
		if self.cell_name == 'deposition':

			set_up_deposition() #Set up deposition travel settings

		if self.cell_name == 'characterization':

			set_up_characterization() #Set up deposition travel settings

		data = tuple_Command_MoveCommand_FullClose_Exe

	    ser.write(data[0])
	    if (data[1] != 0):
	        print("Received")
	        s = ser.read(data[1])
	        print(s)
	    else:
	        print("Sent")
	        
	    time.sleep(7) #Time to let the cell move into position

	def cell_flush(self):
		# Check to ensure this follows a cell_close_full command?  Perhaps a way to check or read back the last
		# last string sent to ensure closed? Or read back the encoder to ensure it is in the correct position?

# ---------------------------------------------------------------------------------


class potentiostat: #Want to put in the ECell class? Or at least have it inherent? 
# Will have two levels = developer level and then 'campaign' run level
# So will likely have in ECell as something simply like depo.run_echem()

