""" Bio-Logic OEM package python API.

This module contains support functions when building technique parameters,
and decoding experiment records.

"""

from dataclasses import dataclass

import kbio.kbio_types as KBIO
from kbio.tech_types import TECH_ID

import numpy as np


@dataclass
class ECC_parm:
    """ECC param template"""
    label: str
    type_: type


# functions to build the technique ECC parameters (structure+contents)

def make_ecc_parm(api, ecc_parm, value=0, index=0):
    """Given an ECC_parm template, create and return an EccParam, with its value and optional index."""
    parm = KBIO.EccParam()
    # BL_Define<xxx>Parameter
    # .. value is converted to its proper type, which DefineParameter will use
    api.DefineParameter(ecc_parm.label, ecc_parm.type_(value), index, parm)
    return parm


def make_ecc_parms(api, *ecc_parm_list):
    """Create an EccParam array from an EccParam list, and return an EccParams refering to it."""
    nb_parms = len(ecc_parm_list)
    parms_array = KBIO.ECC_PARM_ARRAY(nb_parms)

    for i, parm in enumerate(ecc_parm_list):
        parms_array[i] = parm

    parms = KBIO.EccParams(nb_parms, parms_array)

    return parms


# function to handle records from a running experiment

def unpack_experiment_data(api, data, is_VMP3):
    """Unpack the experiment data, decode it according to the technique
       then return the experiment status and decoded data"""

    current_values, data_info, data_record = data

    status = current_values.State
    status = KBIO.PROG_STATE(status).name

    tech_name = TECH_ID(data_info.TechniqueID).name

    # synthetic info for current record
    info = {
        'tb': current_values.TimeBase,
        'ix': data_info.TechniqueIndex,
        'tech': tech_name,
        'proc': data_info.ProcessIndex,
        'loop': data_info.loop,
        'skip': data_info.IRQskipped,
    }

    # print("> data info :")
    # print(info)

    ix = 0

    if tech_name == 'GEIS' or tech_name == 'PEIS':  # special implementation required for GEIS and PEIS
        t_ret = np.array([])
        freq_ret = np.array([])
        Ewe_bar_ret = np.array([])
        I_bar_ret = np.array([])
        Phase_zwe_ret = np.array([])
        Ewe_ret = np.array([])
        I_ret = np.array([])
        Ece_bar_ret = np.array([])
        Ice_bar_ret = np.array([])
        Phase_zce_ret = np.array([])
        Ece_ret = np.array([])
        I_range_ret = np.array([])

        if data_info.ProcessIndex == 0:
            for _ in range(data_info.NbRows):  # points saved in buffer
                inx = ix + data_info.NbCols
                t_high, t_low, *row = data_record[ix:inx]

                nb_words = len(row)
                if nb_words != 2:
                    raise RuntimeError(f"{tech_name} : unexpected record length ({nb_words})")

                Ewe = api.ConvertNumericIntoSingle(row[0])  # Ewe is a float
                I = api.ConvertNumericIntoSingle(row[1])  # current is a float

                # compute timestamp in seconds
                t_rel = (t_high << 32) + t_low
                t = current_values.TimeBase * t_rel

                ix = inx

        elif data_info.ProcessIndex == 1:
            for _ in range(data_info.NbRows):  # points saved in buffer
                inx = ix + data_info.NbCols
                row = data_record[ix:inx]

                nb_words = len(row)
                if nb_words == 15:
                    vmp3 = True
                elif nb_words == 14:
                    vmp3 = False
                else:
                    raise RuntimeError(f"{tech_name} : unexpected record length ({nb_words})")

                freq = api.ConvertNumericIntoSingle(row[0])  # freq
                Ewe_bar = api.ConvertNumericIntoSingle(row[1])  # ewe_bar
                I_bar = api.ConvertNumericIntoSingle(row[2])  # I_bar
                Phase_zwe = api.ConvertNumericIntoSingle(row[3])  # phase_zwe
                Ewe = api.ConvertNumericIntoSingle(row[4])  # Ewe
                I = api.ConvertNumericIntoSingle(row[5])  # I
                Ece_bar = api.ConvertNumericIntoSingle(row[7])  # ece_bar
                Ice_bar = api.ConvertNumericIntoSingle(row[8])  # ice_bar
                Phase_zce = api.ConvertNumericIntoSingle(row[9])  # phase zce
                Ece = api.ConvertNumericIntoSingle(row[10])  # ece
                t = api.ConvertNumericIntoSingle(row[13])  # t

                t_ret = np.append(t_ret, t)
                freq_ret = np.append(freq_ret, freq)
                Ewe_bar_ret = np.append(Ewe_bar_ret, Ewe_bar)
                I_bar_ret = np.append(I_bar_ret, I_bar)
                Phase_zwe_ret = np.append(Phase_zwe_ret, Phase_zwe)
                Ewe_ret = np.append(Ewe_ret, Ewe)
                I_ret = np.append(I_ret, I)
                Ece_bar_ret = np.append(Ece_bar_ret, Ece_bar)
                Ice_bar_ret = np.append(Ice_bar_ret, Ice_bar)
                Phase_zce_ret = np.append(Phase_zce_ret, Phase_zce)
                Ece_ret = np.append(Ece_ret, Ece)

                if vmp3:
                    I_range = api.ConvertNumericIntoSingle(row[14])  # I range
                    I_range_ret = np.append(I_range_ret, I_range)

                ix = inx

        else:
            raise RuntimeError(f"{tech_name} : unexpected process index ({data_info.ProcessIndex})")

        if is_VMP3:
            return status, np.array([t_ret, freq_ret, Ewe_bar_ret, I_bar_ret, Phase_zwe_ret, Ewe_ret, I_ret, Ece_bar_ret, \
               Ice_bar_ret, Phase_zce_ret, Ece_ret, I_range_ret])
        else:
            return status, np.array(
                [t_ret, freq_ret, Ewe_bar_ret, I_bar_ret, Phase_zwe_ret, Ewe_ret, I_ret, Ece_bar_ret, \
                 Ice_bar_ret, Phase_zce_ret, Ece_ret])

    elif tech_name == 'OCV':
        # create storage for data values
        t_ret = np.array([])
        Ewe_ret = np.array([])
        Ece_ret = np.array([])

        for _ in range(data_info.NbRows):  # loop through the number of points saved in the buffer
            # progress through record
            inx = ix + data_info.NbCols

            # extract timestamp and one row
            t_high, t_low, *row = data_record[ix:inx]

            nb_words = len(row)
            if nb_words == 1:
                vmp3 = False
            elif nb_words == 2:
                vmp3 = True
            else:
                raise RuntimeError(f"{tech_name} : unexpected record length ({nb_words})")

            # compute timestamp in seconds
            t_rel = (t_high << 32) + t_low
            t = current_values.TimeBase * t_rel

            Ewe = api.ConvertNumericIntoSingle(row[0])  # Ewe is a float

            t_ret = np.append(t_ret, t)
            Ewe_ret = np.append(Ewe_ret, Ewe)

            if vmp3:
                Ece = api.ConvertNumericIntoSingle(row[1])  # Ece is a float
                Ece_ret = np.append(Ece_ret, Ece)

            ix = inx

        if is_VMP3:
            return status, np.array([t_ret, Ewe_ret, Ece_ret])
        else:  # SP300 series
            return status, np.array([t_ret, Ewe_ret])

    elif tech_name == 'CP' or tech_name == 'CA':
        # create storage for data values
        t_ret = np.array([])
        Ewe_ret = np.array([])
        I_ret = np.array([])
        cycle_ret = np.array([])

        for _ in range(data_info.NbRows):  # loop through the number of points saved in the buffer
            # progress through record
            inx = ix + data_info.NbCols
            t_high, t_low, *row = data_record[ix:inx]

            nb_words = len(row)
            if nb_words != 3:
                raise RuntimeError(f"{tech_name} : unexpected record length ({nb_words})")

            Ewe = api.ConvertNumericIntoSingle(row[0])  # Ewe is a float
            I = api.ConvertNumericIntoSingle(row[1])  # current is a float
            cycle = row[2]  # technique cycle is an integer

            # compute timestamp in seconds
            t_rel = (t_high << 32) + t_low
            t = current_values.TimeBase * t_rel

            t_ret = np.append(t_ret, t)
            Ewe_ret = np.append(Ewe_ret, Ewe)
            I_ret = np.append(I_ret, I)
            cycle_ret = np.append(cycle_ret, cycle)

            ix = inx

        return status, np.array([t_ret, Ewe_ret, I_ret, cycle_ret])

    elif tech_name == 'CV':
        # create storage for data values
        t_ret = np.array([])
        Ewe_ret = np.array([])
        Ec_ret = np.array([])
        Cycle_ret = np.array([])
        I_ret = np.array([])

        for _ in range(data_info.NbRows):  # loop through the number of points saved in the buffer
            # progress through record
            inx = ix + data_info.NbCols
            t_high, t_low, *row = data_record[ix:inx]

            nb_words = len(row)
            if nb_words == 4:
                vmp3 = True
            elif nb_words == 3:
                vmp3 = False
            else:
                raise RuntimeError(f"{tech_name} : unexpected record length ({nb_words})")

            # compute timestamp in seconds
            t_rel = (t_high << 32) + t_low
            t = current_values.TimeBase * t_rel
            t_ret = np.append(t_ret, t)

            if vmp3:
                # implemented for VMP3 device family
                Ec = api.ConvertNumericIntoSingle(row[0])  # EC is a float
                I = api.ConvertNumericIntoSingle(row[1])  # I is an float
                Ewe = api.ConvertNumericIntoSingle(row[2])  # Ewe is a float
                Cycle = row[3]  # Cycle is an integer

                Ewe_ret = np.append(Ewe_ret, Ewe)
                Ec_ret = np.append(Ec_ret, Ec)
                Cycle_ret = np.append(Cycle_ret, Cycle)
                I_ret = np.append(I_ret, I)
            else:
                I = api.ConvertNumericIntoSingle(row[0])  # I is an float
                Ewe = api.ConvertNumericIntoSingle(row[1])  # Ewe is a float
                Cycle = row[2]  # Cycle is an integer
                Ewe_ret = np.append(Ewe_ret, Ewe)
                Cycle_ret = np.append(Cycle_ret, Cycle)
                I_ret = np.append(I_ret, I)

            ix = inx

        if is_VMP3:
            return status, np.array([t_ret, Ec_ret, I_ret, Ewe_ret, Cycle_ret])
        else:
            return status, np.array([t_ret, I_ret, Ewe_ret, Cycle_ret])

    else:  # techniques implemented: OCV, CP, CV, CA
        for _ in range(data_info.NbRows):
            print('**** WARNING: Technique not implemented ****')
            # show a raw dump of the record
            inx = ix + data_info.NbCols
            row = data_record[ix:inx]
            parsed_row = [f"0x{word:08X}" for word in row]
            # print("> data record :")
            # print(parsed_row)
            ix = inx
        return

    raise RuntimeError(f"Technique not implemented, there has been an error.")
