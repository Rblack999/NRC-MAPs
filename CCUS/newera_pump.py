from new_era.peristaltic_pump import PeristalticPump
import serial
import time                                  
import io
from new_era.peristaltic_pump_network import PeristalticPumpNetwork

#these will go to main - putting them here for now:
pump_port = 'COM5'  # check on your own system
pump_network = PeristalticPumpNetwork(port=pump_port, baudrate=9600)
pump = pump_network.add_pump(address=0, baudrate=9600)  # only one pump is used for this project

def start_pump():
    
    pump.start()

def stop_pump():
    
    pump.stop()

def change_direction(direction):

    directions = ['dispense','withdraw','reverse']   

    if direction in directions:
       pump.set_direction(direction) 

    else: 
        print('pick one of dispense/withdraw/reverse')
        return None

def change_flowrate(rate):
    
    #flowrate must be between 0.004 ml/min and 75.19 ml/min.")   
    rate = float(rate)
   
    if 0.004 <= rate <= 75.19: 
        pump.set_rate(rate, unit='ml/min')
   
    elif rate < 0.004:
        print("Your flowrate is too small. Choose a flowrate between 0.004 ml/min and 75.19 ml/min.")
        return None

    elif rate > 75.19:
        print("Your flowrate is too large. Choose a flowrate between 0.004 ml/min and 75.19 ml/min.")
        return None