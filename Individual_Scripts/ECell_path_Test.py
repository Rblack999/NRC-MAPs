from north_c9 import NorthC9
from Locator import *
import time
from nrc_custom.Ecell_package import ECell

# c9 = NorthC9('A')
# c9.home_robot()

a = ECell('characterization','COM4')
a.cell_close_slide()
a.cell_open()