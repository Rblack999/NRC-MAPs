import serial
import time

def receiving():
    while stepper_slider_port.inWaiting() >0:
        line = stepper_slider_port.read_until().decode().rstrip()
        print(line)
    print("empty")

    if __name__ == "__receiving__":
        receiving()
    
def startup():
    stepper_slider_port.write("\r\n\r\n".encode())
    time.sleep(2)   # Wait for board to initialize
    receiving() 

    if __name__ == "__startup__":
        startup()

def close_cell():
    
    stepper_slider_port.write(('G0 X-32.5 F200' + "\n").encode())
    time.sleep(0.50)

    if __name__ == "__close_cell__":
        close_cell()

def open_cell(): #add this functionality to the previous function in the future
    
    stepper_slider_port.write(('G0 X32.5 F200' + "\n").encode())
    time.sleep(0.5)

    if __name__ == "__open_cell__":
        open_cell()

def home():

    stepper_slider_port.write(('$H' + "\n").encode())
    time.sleep(0.50)

    if __name__ == "__home__":
        home()