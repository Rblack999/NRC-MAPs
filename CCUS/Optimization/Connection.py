import kbio.kbio_types as KBIO
from kbio.kbio_api import KBIO_api
from kbio.c_utils import c_is_64b
import logging


def connect(address, binary_path):
    # this function establishes a connection with the potentiostat, initializes the API to be used and determines the
    # devices family

    try:
        if c_is_64b:  # determine library file according to Python version (32b/64b)
            DLL_file = "EClib64.dll"
        else:
            DLL_file = "EClib.dll"

        DLL_path = binary_path + DLL_file  # set correct path for dll
        api = KBIO_api(DLL_path)  # API initialize
        id_, device_info = api.Connect(address)  # BL_Connect

        # is_VMP3 = device_info.model in KBIO.VMP3_FAMILY  # detect instrument family
        # is_VMP300 = device_info.model in KBIO.VMP300_FAMILY  # detect instrument family

        firmware = binary_path+'kernel4.bin' # Note that this has to be updated depending on device is VMP3 or VMP300 - see manual
        # LoadFirmware(self, id_, channels, firmware, fpga, force=True)
        api.LoadFirmware(id_, [1, 2, 3, 4, 5, 6], firmware, None, force=True)

        logging.info('Device connected at address ' + str(address))  # log device connection

    except Exception as e:
        print('Cannot establish connection with the instrument. Program Ended.')
        logging.error('Cannot establish connection with the instrument. Program Ended. DETAILS: ' + str(e))
        exit()

    return api, id_, device_info


def disconnect(address, api, id_):
    # this function disconnects the potentiostat
    api.Disconnect(id_)  # BL_Disconnect
    logging.info('Device disconnected at address ' + str(address))  # log device disconnection
