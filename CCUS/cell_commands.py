import serial
import time

#ser = serial.Serial('COM9',115200)  # open serial port before every command 

def receiving():
    while ser.inWaiting() >0:
        line= ser.read_until().decode().rstrip()
        #time.sleep(.05)
        print(line)
    print("empty")
    
    
def startup():
    print("Connecting to board on:",ser.name)    # check which port was really used
    ser.write("\r\n\r\n".encode())
    time.sleep(2)   # Wait for board to initialize
    receiving() 

def close_cell():
    
    startup()

    ser.write(('G91' + "\n").encode()) #ensuring to convert to relative displacement
    ser.write(('G0 X-32.5 F200' + "\n").encode())
    time.sleep(0.5)
    ser.close()

    if __name__ == "__main__":
        close_cell()


def open_cell():
    
    startup()
    
    ser.write(('G91' + "\n").encode())
    ser.write(('G0 X32.5 F100' + "\n").encode())
    time.sleep(0.5)
    ser.close()
    
    if __name__ == "__main__":
        open_cell()


def home():
    
    startup()
    
    ser.write(('$H' + "\n").encode())
    time.sleep(0.5)
    ser.close() #close the port at the end of execution
    
    if __name__ == "__main__":
        home()