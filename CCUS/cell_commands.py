import serial
import time

stepper_slider_port = serial.Serial('COM9',115200) 

def receiving():
    while stepper_slider_port.inWaiting() >0:
        line = stepper_slider_port.read_until().decode().rstrip()
        print(line)
    print("empty")

    
def startup():
    stepper_slider_port.write("\r\n\r\n".encode())
    time.sleep(2)   # Wait for board to initialize
    receiving() 


def close_cell():
    
    stepper_slider_port.write(('G0 X-32.5 F200' + "\n").encode())
    time.sleep(0.50)


def open_cell(): #add this functionality to the previous function in the future
    
    stepper_slider_port.write(('G0 X32.5 F200' + "\n").encode())
    time.sleep(0.5)


def home():

    stepper_slider_port.write(('$H' + "\n").encode())
    time.sleep(0.50)
