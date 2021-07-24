from north_c9 import NorthC9
from Locator import *
from ftdi_serial import Serial
import time 

print(Serial.list_device_serials())

c9 = NorthC9('A')

# Initiate Stepper Slider for test--------------------
import serial
import struct
import time

ser = serial.Serial(
    port='COM1',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)
print(ser.isOpen())

# Commands
command_GetVersion_Query = b'\x10\x02\x00\x88\x07\x01\xA2'

command_StepperSlider_Deposit_Set = b'\x10\x02\x00\x88\x08\x0c\x00\xAE'
command_StepperSlider_Character_Set = b'\x10\x02\x00\x88\x08\x0c\x01\xAF'
command_TravelSettings_BothSafe_Set = b'\x10\x02\x00\x88\x1A\x07\x00\x00\x00\x00\x00\x00\x00\x88\xb8\x00\x00\xff\x00\x00\x00\x64\x00\x9c\x40\x3a'
command_TravelSettings_Character_Set = b'\x10\x02\x00\x88\x1A\x07\x00\x00\x00\x00\x00\x00\x00\x9E\x98\x00\x00\xff\x00\x00\x00\x64\x00\xAB\x18\x17'
command_TravelSettings_Deposit_Set = b'\x10\x02\x00\x88\x1A\x07\x00\x00\x00\x00\x00\x00\x00\x99\x20\x00\x00\xff\x00\x00\x00\x64\x00\xA5\xA0\x1c'

command_MoveCommand_JogPlus_Exe = b'\x10\x02\x00\x88\x08\x04\x10\xB6'
command_MoveCommand_JogMinus_Exe = b'\x10\x02\x00\x88\x08\x04\x20\xC6'
command_MoveCommand_Stop_Exe = b'\x10\x02\x00\x88\x08\x04\x02\xa8'
command_MoveCommand_Home_Exe = b'\x10\x02\x00\x88\x08\x04\x04\xaa'
command_MoveCommand_PinSlide_Exe = b'\x10\x02\x00\x88\x08\x04\x08\xae'
command_MoveCommand_FullClose_Exe = b'\x10\x02\x00\x88\x08\x04\x40\xe6'

# Tuple couplings
tuple_GetVersion_Query = (command_GetVersion_Query, 11) # x0B

tuple_StepperSlider_Deposit_Set = (command_StepperSlider_Deposit_Set, 0)
tuple_StepperSlider_Character_Set = (command_StepperSlider_Character_Set, 0)
tuple_TravelSettings_BothSafe_Set = (command_TravelSettings_BothSafe_Set, 26) # x1A
tuple_TravelSettings_Character_Set = (command_TravelSettings_Character_Set, 26) # x1A
tuple_TravelSettings_Deposit_Set = (command_TravelSettings_Deposit_Set, 26) # x1A

tuple_Command_MoveCommand_JogPlus_Exe = (command_MoveCommand_JogPlus_Exe, 0)
tuple_Command_MoveCommand_JogMinus_Exe = (command_MoveCommand_JogMinus_Exe, 0)
tuple_Command_MoveCommand_Stop_Exe = (command_MoveCommand_Stop_Exe, 0)
tuple_Command_MoveCommand_Home_Exe = (command_MoveCommand_Home_Exe, 0)

tuple_Command_MoveCommand_PinSlide_Exe = (command_MoveCommand_PinSlide_Exe, 0)
tuple_Command_MoveCommand_FullClose_Exe = (command_MoveCommand_FullClose_Exe, 0)

###
data = tuple_StepperSlider_Character_Set

ser.write(data[0])
if(data[1] != 0):
    print("Received")
    s = ser.read(data[1])
    print(s)
else:
    print("Sent")

time.sleep(1)  # Critical sleep delay for transmission latency

data = tuple_TravelSettings_Character_Set

ser.write(data[0])
if (data[1] != 0):
    print("Received")
    s = ser.read(data[1])
    print(s)
else:
    print("Sent")
    
time.sleep(1)

# ---------------------------------------------------------------------------------

# Close cell with slide in it

for i in range(0,5):
    print(f'Starting test {i} of 5')
    
    data = tuple_Command_MoveCommand_PinSlide_Exe

    ser.write(data[0])
    if (data[1] != 0):
        print("Received")
        s = ser.read(data[1])
        print(s)
    else:
        print("Sent")
        
    time.sleep(5) #Time to let the cell move into position

    # Fill and remove liquid from cell, holding ten seconds
    hold_time = 10
    c9.pumps[3]['volume']=12.5
    c9.home_pump(3)
    c9.delay(1)
    c9.set_pump_valve(3,1)
    c9.delay(1)
    c9.aspirate_ml(3,12.5)

    c9.delay(1)
    c9.set_pump_valve(3,2)
    c9.delay(1)
    c9.dispense_ml(3,12.5)
    c9.delay(hold_time)

    c9.aspirate_ml(3,12.5)
    c9.delay(1)
    c9.set_pump_valve(3,1)
    time.sleep(1)
    c9.dispense_ml(3,12.5)

    #Open cell back to home

    data = tuple_Command_MoveCommand_Home_Exe

    ser.write(data[0])
    if (data[1] != 0):
        print("Received")
        s = ser.read(data[1])
        print(s)
    else:
        print("Sent")
        
    time.sleep(10)

    #Blower on
    time.sleep(5)
    c9.set_output(3,True)
    time.sleep(2)
    c9.set_output(3,False)

    #Input to run loop again
    while True:
        answer = input('Next Run? Is the slide loaded and ready to go?')
        if answer == 'ok':
            break
        else:
            print('Please print ok to continue')
