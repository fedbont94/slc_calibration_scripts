"""
__author__ = Federico Bontempo KIT PhD student <federico.bontempo@kit.edu>

This script defines two functions:  
    get_calibration_values 
    calculate_p0_p1

Here's a summary of what each function does:

get_calibration_values Function:
    This function calculates the p0 and p1 values for a given OMKey based on provided sums and statistics. 
    The calculated values and related information are stored in the result_dict.

    Parameters:
        sums_dict: A dictionary containing sums and statistics necessary for the calculation.
        string: A string identifier.
        om: An identifier for the optical module.
        chip: An identifier for the chip.
        atwd: An identifier for the analog to waveform digitizer.
        result_dict: A dictionary to store the results.

calculate_p0_p1 Function:
    This function calculates the p0 and p1 values for each OMKey in the input slcATW_dict. 
    The calculations are based on the method of least squares. 
    The results, along with related statistics, are stored in the result_dict.

    Parameters:
        slcATW_dict: A dictionary of OMKeys with a list of slc and hlc charges for each ATWD and chips.
        bad_dom_list: A list of bad DOMs (default is an empty list).
        Returns:
        result_dict: A dictionary containing the calculated p0 and p1 values, errors, chi-squared values, and other related statistics for each OMKey.

The calculate_p0_p1 function iterates over OMKeys and uses 
the get_calibration_values function to calculate p0 and p1 values for each combination of OMKey, chip, and ATWD. 
It also sums the charges from two chips and calculates p0 and p1 for the combined values. 
The results are then returned in the result_dict.

The get_calibration_values function calculates p0 and p1 values using a least squares method and stores the results in the result_dict. 
It also handles cases where the calculated values might not be valid.
"""


import numpy as np
from icecube import icetray, vemcal, dataclasses
from icecube.icetray.i3logging import (
    log_warn,
    log_fatal,
)


def get_calibration_values(sums_dict, string, om, chip, atwd, result_dict):
    """
    Calculate the p0 and p1 values for a given OMKey.
    ----------------------------------------------
    Parameters:
        sums_dict: A dictionary containing sums and statistics necessary for the calculation.
        string: A string identifier.
        om: An identifier for the optical module.
        chip: An identifier for the chip.
        atwd: An identifier for the analog to waveform digitizer.
        result_dict: A dictionary to store the results.
    """
    delta = sums_dict["n"] * sums_dict["xx"] - sums_dict["x"] ** 2

    if (delta <= 0) or (sums_dict["n"] == 1):
        log_warn(
            f"This OM has a delta<=0: ({string},{om},{chip},{atwd})", unit="vemcal"
        )
        log_warn(
            f"n = {sums_dict['n']}, xx = {sums_dict['xx']}, x = {sums_dict['x']}",
            unit="vemcal",
        )
        a = 0
        b = 0
        aerr = -1
        berr = -1
    else:
        a = (
            sums_dict["xx"] * sums_dict["y"] - sums_dict["x"] * sums_dict["xy"]
        ) / delta
        b = (sums_dict["n"] * sums_dict["xy"] - sums_dict["x"] * sums_dict["y"]) / delta
        # these are the sqrt(variance) on the parameters
        aerr = np.sqrt(sums_dict["xx"] / delta)
        berr = np.sqrt(sums_dict["n"] / delta)
    chi2 = (
        sums_dict["yy"]
        - 2 * a * sums_dict["y"]
        - 2 * b * sums_dict["xy"]
        + a**2 * sums_dict["n"]
        + 2 * a * b * sums_dict["x"]
        + b**2 * sums_dict["xx"]
    )

    if chi2 < 0:
        log_warn(f"SOCA = {string} {om} {chip} {atwd}", unit="vemcal")
        log_warn(
            f"WARN: chi2 came out less than zero for some reason: {chi2}",
            unit="vemcal",
        )
        log_warn(
            f"N = {sums_dict['n']}, "
            + f"Sx = {sums_dict['x']}, "
            + f"Sy = {sums_dict['y']}, "
            + f"Sxx = {sums_dict['xx']}, "
            + f"Syy = {sums_dict['yy']}, "
            + f"Sxy = {sums_dict['xy']}",
            unit="vemcal",
        )
        if sums_dict["n"] > 2:
            log_fatal("This will cause a fatal NaN error later.")

    result_dict[(string, om, chip, atwd)] = {}
    result_dict[(string, om, chip, atwd)]["p0"] = a
    result_dict[(string, om, chip, atwd)]["p1"] = b
    if sums_dict["n"] <= 2:
        log_warn(
            f"This OM has a n={sums_dict['n']}, which is <=2: ({string},{om},{chip},{atwd})",
            unit="vemcal",
        )
        result_dict[(string, om, chip, atwd)]["p0_error"] = -1
        result_dict[(string, om, chip, atwd)]["p1_error"] = -1
    else:
        result_dict[(string, om, chip, atwd)]["p0_error"] = aerr * np.sqrt(
            chi2 / (sums_dict["n"] - 2)
        )
        result_dict[(string, om, chip, atwd)]["p1_error"] = berr * np.sqrt(
            chi2 / (sums_dict["n"] - 2)
        )
    result_dict[(string, om, chip, atwd)]["n"] = sums_dict["n"]
    result_dict[(string, om, chip, atwd)]["chi2"] = chi2

    # Extend tth result_dict with the sum_dict
    result_dict[(string, om, chip, atwd)].update(sums_dict)

    return


def calculate_p0_p1(slcATW_dict, bad_dom_list=[]):
    """
    Calculate the p0 and p1 values for each OMKey in the slcATW_dict.
    The slcATW_dict is a dictionary of OMKeys with a list of slc and hlc charges
    for each ATWD and chips. The p0 and p1 values are calculated using the method of
    least squares. The p0 and p1 values are saved in a dictionary with the
    following structure:
    result_dict[(string, om, chip, atwd)]= {
            "n": n, # number of charges which were summed to calculate the p0 and p1 values
            "p0": p0,
            "p1": p1,
            "p0_error": p0_error,
            "p1_error": p1_error,
            "chi2": chi2,
            "x": x, # sum of the charges
            "xx": xx, # sum of the squared charges
            "y": y, # sum of the log10(slc/hlc) charges
            "yy": yy, # sum of the squared log10(slc/hlc) charges
            "xy": xy, # sum of the product of the charges and log10(slc/hlc) charges

        ... keep going for each (string, om, chip, atwd) ...

        }
    ----------------------------------------------
    Parameters:
        slcATW_dict: A dictionary of OMKeys with a list of slc and hlc charges for each ATWD and chips.
        bad_dom_list: A list of bad DOMs (default is an empty list).
        Returns:
        result_dict: A dictionary containing the calculated p0 and p1 values, errors, chi-squared values, and other related statistics for each OMKey.
    """

    result_dict = {}
    for omkey, sums_dict in slcATW_dict.items():
        string, om = omkey.string, omkey.om
        for atwd in range(3):
            for chip in range(2):
                get_calibration_values(
                    sums_dict=sums_dict[f"chip{chip}atwd{atwd}"],
                    string=string,
                    om=om,
                    chip=chip,
                    atwd=atwd,
                    result_dict=result_dict,
                )

            # sum the two chips
            sumsChips_dictc = {}
            sums_dict0 = sums_dict[f"chip0atwd{atwd}"]
            sums_dict1 = sums_dict[f"chip1atwd{atwd}"]
            for key in sums_dict0.keys():
                sumsChips_dictc[key] = sums_dict0[key] + sums_dict1[key]

            get_calibration_values(
                sums_dict=sumsChips_dictc,
                string=string,
                om=om,
                chip=2,
                atwd=atwd,
                result_dict=result_dict,
            )

    return result_dict
