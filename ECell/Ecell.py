import serial
import time

class ECell(self, cell_number): # TODO: define class based on cell number

    self.cell_number = cell_number
    pass

    def pump1(self, on_time):

        dev = serial.Serial("COM10",baudrate = 9600)
        print('connected')
        time.sleep(2)
        dev.write(b'1')
        print(dev.readline().decode('ascii'))
        time.sleep(on_time)
        dev.write(b'0')
        print(dev.readline().decode('ascii'))
        time.sleep(1)
        dev.close()
        print('COM closed')
        
    def pump2(self, on_time):
        pass    #TODO when pump 2 connected

    # if __name__ == "__main__":
    #     pump1(2)