from north_c9 import NorthC9
from Locator import *
import time
#from nrc_custom.Ecell_package import ECell

#Initialize everything
c9 = NorthC9('A')
c9.home_robot()

c9.goto_safe(char_cell_in)
