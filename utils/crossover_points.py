#!/usr/bin/env python
"""
This script contains the functions to calculate the crossover points of the SLC calibration values.
It takes the SLC calibration values from a .pkl file and calculates the crossover points.
It can also plot the histograms with the crossover points.

__author__ = 
Julian Saffer KIT PhD student <julian.saffer@kit.edu>
Federico Bontempo KIT PhD student <federico.bontempo@kit.edu>
! special thanks to Katherine Rawlins for the help !

When running the main script, simply import calculate_crossOverPoints and give the path to the .pkl file as argument.
"""

import glob
import pickle
import numpy as np

from scipy.stats import gaussian_kde
from scipy.optimize import brentq

from icecube import icetray, dataio, vemcal


def load_chargesFromFile(file):
    # Open the pickle file
    with open(file, "rb") as f:
        slcATW_dict = pickle.load(f)
    return slcATW_dict


def findIntersection(fun1, fun2, weight1, weight2, lower, upper):
    return brentq(lambda x: weight1 * fun1(x) - weight2 * fun2(x), lower, upper)


def calculate_crossOverPoints(file, pathSave="", doPlotting=False):
    slcATW_dict = load_chargesFromFile(file)
    crossOverPoints_dict = {}

    # Loop over all OMKeys
    for key in slcATW_dict.keys():
        atwd0 = np.log10(slcATW_dict[key]["atwd0"][0])[
            ~np.isinf(np.log10(slcATW_dict[key]["atwd0"][0]))
        ]  # remove zero charges
        atwd1 = np.log10(slcATW_dict[key]["atwd1"][0])[
            ~np.isinf(np.log10(slcATW_dict[key]["atwd1"][0]))
        ]
        atwd2 = np.log10(slcATW_dict[key]["atwd2"][0])[
            ~np.isinf(np.log10(slcATW_dict[key]["atwd2"][0]))
        ]

        # Check if the ATW2 has charges to the very left
        # that mess up the crossover point
        if len(atwd2) != 0 and len(atwd1) != 0:
            if max(atwd2) < min(atwd1):
                atwd2 = np.array([])

        len0 = len(atwd0)
        len1 = len(atwd1)
        len2 = len(atwd2)

        charge_binning = np.linspace(-1, 6, 71)
        charge_bin_width = charge_binning[1] - charge_binning[0]

        if len0:
            med0 = np.median(atwd0)
            kde0 = gaussian_kde(atwd0)
            weight0 = len(slcATW_dict[key]["atwd0"][0]) * charge_bin_width
        if len1:
            med1 = np.median(atwd1)
            kde1 = gaussian_kde(atwd1)
            weight1 = len(slcATW_dict[key]["atwd1"][0]) * charge_bin_width
        if len2:
            med2 = np.median(atwd2)
            kde2 = gaussian_kde(atwd2)
            weight2 = len(slcATW_dict[key]["atwd2"][0]) * charge_bin_width

        if len0 and len1:
            cop01_kde = findIntersection(kde0, kde1, weight0, weight1, med0, med1)
        if len1 and len2:
            cop12_kde = findIntersection(kde1, kde2, weight1, weight2, med1, med2)

        # Check if the OMKey has charges in all ATWDs
        # and save the crossover points in the dictionary
        if len0 and len1 and len2:
            crossOverPoints_dict[key] = (cop01_kde, cop12_kde)
        elif (key[0], key[1], key[2]) in [(74, 61, 0), (39, 61, 0)]:
            # Dead DOMs "OMKey(74,61,0)" and "OMKey(39,61,0)"
            continue
        else:
            # Give a run warning
            RuntimeWarning(
                f"OMKey {key} has less than 3 ATWDs with charges. Probably something is broken."
            )

    if doPlotting:
        plot_histWithCrossOverPoints(
            slcATW_dict, pathSave, charge_array_kde=np.linspace(-1, 6, 701)
        )

    return crossOverPoints_dict


def plot_histWithCrossOverPoints(slcATW_dict, pathSave, charge_array_kde):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(81, 4, figsize=(25, 162 * 1.5))

    for key in slcATW_dict.keys():
        # check if key is a string
        if isinstance(key, str):
            station = int(key.replace("OMKey", "")[1:-1].split(",")[0]) - 1
            om = int(key.replace("OMKey", "")[1:-1].split(",")[1]) - 61
        else:
            station = key.string - 1
            om = key.om - 61

        axes[station, om].text(
            0.05,
            0.8,
            key,
            fontsize=10,
            color="k",
            weight="bold",
            transform=axes[station, om].transAxes,
        )

        atwd0 = np.log10(slcATW_dict[key]["atwd0"][0])[
            ~np.isinf(np.log10(slcATW_dict[key]["atwd0"][0]))
        ]  # remove zero charges
        atwd1 = np.log10(slcATW_dict[key]["atwd1"][0])[
            ~np.isinf(np.log10(slcATW_dict[key]["atwd1"][0]))
        ]
        atwd2 = np.log10(slcATW_dict[key]["atwd2"][0])[
            ~np.isinf(np.log10(slcATW_dict[key]["atwd2"][0]))
        ]

        if len(atwd2) != 0 and len(atwd1) != 0:
            if max(atwd2) < min(atwd1):
                atwd2 = np.array([])

        len0 = len(atwd0)
        len1 = len(atwd1)
        len2 = len(atwd2)

        charge_binning = np.linspace(-1, 6, 71)
        charge_bin_width = charge_binning[1] - charge_binning[0]

        if len0:
            axes[station, om].hist(
                atwd0, alpha=0.5, color="blue", bins=charge_binning, label="ATWD0"
            )
            med0 = np.median(atwd0)
            kde0 = gaussian_kde(atwd0)
            weight0 = len(slcATW_dict[key]["atwd0"][0]) * charge_bin_width
        if len1:
            axes[station, om].hist(
                atwd1, alpha=0.5, color="green", bins=charge_binning, label="ATWD1"
            )
            med1 = np.median(atwd1)
            kde1 = gaussian_kde(atwd1)
            weight1 = len(slcATW_dict[key]["atwd1"][0]) * charge_bin_width
        if len2:
            axes[station, om].hist(
                atwd2, alpha=0.5, color="red", bins=charge_binning, label="ATWD2"
            )
            med2 = np.median(atwd2)
            kde2 = gaussian_kde(atwd2)
            weight2 = len(slcATW_dict[key]["atwd2"][0]) * charge_bin_width

        if len0 and len1:
            cop01_kde = findIntersection(kde0, kde1, weight0, weight1, med0, med1)
            axes[station, om].axvline(x=cop01_kde, c="k", ls="solid")
        if len1 and len2:
            cop12_kde = findIntersection(kde1, kde2, weight1, weight2, med1, med2)
            axes[station, om].axvline(x=cop12_kde, c="k", ls="dashed")

        axes[station, om].set_xlabel(r"$\log_\mathrm{10}$" + "(SLC charge (PE))")
        axes[station, om].set_ylabel("count")
        axes[station, om].set_xlim(-1, 6)
        axes[station, om].set_yscale("log")
        if (key != "OMKey(74,61,0)") and (key != "OMKey(39,61,0)"):
            axes[station, om].legend(loc="upper right")
        else:
            axes[station, om].text(
                0.5,
                0.5,
                "dead DOM",
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=10,
                color="k",
                weight="bold",
                transform=axes[station, om].transAxes,
            )

    plt.savefig(f"{pathSave}/SLCCal_first_results_linear.png", bbox_inches="tight")
    plt.close()
