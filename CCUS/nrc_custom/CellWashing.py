import serial
import time       
import io
from nesp_lib import Port, Pump, PumpingDirection

class CellWashing:
    
    # Start on class instantiate
    def __init__(self, valve_com_port, syringe_com_port):
        
        self.valve_com_port = valve_com_port
        self.syringe_com_port = syringe_com_port
        
        # Connect valve via the specified com_port
        self.ser = serial.Serial(port = self.valve_com_port,  #Check your device manager and change the COM port here as needed.
                    baudrate = 9600, 
                    bytesize = serial.EIGHTBITS,  
                    parity = serial.PARITY_NONE,   #Establishes a serial connection between valve controller and computer.
                    stopbits = serial.STOPBITS_ONE
                   )
        
        print('Valve Connected')
        
        # Connect syringe via the specified com_port
        self.port = Port(self.syringe_com_port)
        self.pump = Pump(self.port, address = 1)
        time.sleep(1)
        
        # Sets the syringe diameter of the pump in units of millimeters.
        self.pump.syringe_diameter = 26.64
        
        # Sets the pumping rate of the pump in units of milliliters per minute.
        self.pump.pumping_rate = 25
        
        print('Syringe Pump Connected')
    
    # This is for the serial communications with the valve
    def _readline(self): #Used to ensure readline() end at \r since readline() function no longer exists in Python 3.x
        
        eol = b'\r'
        leneol = len(eol)
        line = bytearray()
        while True:
            c = self.ser.read(1)
            if c:
                line += c
                if line[-leneol:] == eol:
                    break
            else:
                break
        print(bytes(line))
        return bytes(line)

    # Def move the valve to any direction that is wished
    def move_valve(self, valve_num):
        
        # Input check
        if valve_num not in [1,2,3,4,5,6]:
            raise NameError(f'Invalid valve change position - must be [1,2,3,4,5,6]')
                
        print(f'Valve request to moved to position {valve_num}')
        position = f'GO0{valve_num}\r'     
        self.ser.write(position.encode()) #Serial command communicates and "instructs" the valve controller to change positions.
        time.sleep(1)

        self.ser.write(b'CP\r')     #This serial command prints the current position of the valve.
        time.sleep(0.2)
        self._readline()
    
    # Definitions of the pump
    # Port 1 - DI Water Source
    # Port 2 - Deposition Cell
    # Port 3 - Characterization Cell
    # Port 4 - Waste
    
    # The following code is purely for the cell washing steps
    def wash_deposition_cell(self, volume, num_wash_steps): 
        
        # Sets the pumping volume of the pump in units of milliliters.
        self.pump.pumping_volume = volume
        
        # Initial withdraw of liquid from cell
        self.move_valve(2)
        self.pump.pumping_direction = PumpingDirection.WITHDRAW
        self.pump.run()
        self.move_valve(4)
        self.pump.pumping_direction = PumpingDirection.INFUSE
        self.pump.run()
        
        # Washing loop 
        for i in range(num_wash_steps):
                self.move_valve(1)
                self.pump.pumping_direction = PumpingDirection.WITHDRAW
                self.pump.run()
                self.move_valve(2)
                self.pump.pumping_direction = PumpingDirection.INFUSE
                self.pump.run()
                self.pump.pumping_direction = PumpingDirection.WITHDRAW
                self.pump.run()
                self.move_valve(4)
                self.pump.pumping_direction = PumpingDirection.INFUSE
                self.pump.run()
                
    def wash_characterization_cell(self, volume, num_wash_steps): 
        
        # Sets the pumping volume of the pump in units of milliliters.
        self.pump.pumping_volume = volume
        
        # Initial withdraw of liquid from cell
        self.move_valve(3)
        self.pump.pumping_direction = PumpingDirection.WITHDRAW
        self.pump.run()
        self.move_valve(4)
        self.pump.pumping_direction = PumpingDirection.INFUSE
        self.pump.run()
        
        # Washing loop 
        for i in range(num_wash_steps):
                self.move_valve(1)
                self.pump.pumping_direction = PumpingDirection.WITHDRAW
                self.pump.run()
                self.move_valve(3)
                self.pump.pumping_direction = PumpingDirection.INFUSE
                self.pump.run()
                self.pump.pumping_direction = PumpingDirection.WITHDRAW
                self.pump.run()
                self.move_valve(4)
                self.pump.pumping_direction = PumpingDirection.INFUSE
                self.pump.run()
        