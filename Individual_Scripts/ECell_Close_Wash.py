from north_c9 import NorthC9
from Locator import *
import time
from nrc_custom.Ecell_package import ECell

c9 = NorthC9('A')

a = ECell('characterization','COM4')
a.cell_close_full()
time.sleep(10)

c9.set_output(3,True)
time.sleep(30)
c9.set_output(3,False)
time.sleep(5)

a.cell_open()