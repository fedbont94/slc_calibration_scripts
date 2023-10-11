import numpy as np
from icecube import icetray, vemcal, dataclasses
from icecube.icetray.i3logging import (
    log_warn,
    log_fatal,
)

from utils.utils import tuple_to_str, str_to_tuple


def get_calibration_values(sums_dict, string, om, chip, atwd, result_dict):
    """
    Calculate the p0 and p1 values for a given OMKey.
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

    result_dict[tuple_to_str((string, om))][tuple_to_str((chip, atwd))] = {}
    result_dict[tuple_to_str((string, om))][tuple_to_str((chip, atwd))]["p0"] = a
    result_dict[tuple_to_str((string, om))][tuple_to_str((chip, atwd))]["p1"] = b
    if sums_dict["n"] <= 2:
        log_warn(
            f"This OM has a n={sums_dict['n']}, which is <=2: ({string},{om},{chip},{atwd})",
            unit="vemcal",
        )
        result_dict[tuple_to_str((string, om))][tuple_to_str((chip, atwd))][
            "p0_error"
        ] = -1
        result_dict[tuple_to_str((string, om))][tuple_to_str((chip, atwd))][
            "p1_error"
        ] = -1
    else:
        result_dict[tuple_to_str((string, om))][tuple_to_str((chip, atwd))][
            "p0_error"
        ] = aerr * np.sqrt(chi2 / (sums_dict["n"] - 2))
        result_dict[tuple_to_str((string, om))][tuple_to_str((chip, atwd))][
            "p1_error"
        ] = berr * np.sqrt(chi2 / (sums_dict["n"] - 2))
    result_dict[tuple_to_str((string, om))][tuple_to_str((chip, atwd))][
        "n"
    ] = sums_dict["n"]
    result_dict[tuple_to_str((string, om))][tuple_to_str((chip, atwd))]["chi2"] = chi2
    # Extend tth result_dict with the sum_dict
    result_dict[tuple_to_str((string, om))][tuple_to_str((chip, atwd))].update(
        sums_dict
    )

    return


def calculate_p0_p1(slcATW_dict, bad_dom_list=[]):
    """
    Calculate the p0 and p1 values for each OMKey in the slcATW_dict.
    The slcATW_dict is a dictionary of OMKeys with a list of slc and hlc charges
    for each ATWD and chips. The p0 and p1 values are calculated using the method of
    least squares. The p0 and p1 values are saved in a dictionary with the
    following structure:
    result_dict = {
        (string, om) = {
            (chip, atwd) = {
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

            ... keep going for each (chip, atwd) ...
        ... keep going for each (string, om) ...
        }
    }
    """
    result_dict = {}
    for omkey, sums_dict in slcATW_dict.items():
        string, om, _ = str_to_tuple(omkey)
        result_dict[tuple_to_str((string, om))] = {}
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
