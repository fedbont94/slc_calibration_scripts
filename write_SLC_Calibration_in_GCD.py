#! /usr/bin/env python3
"""
This script writes the SLC calibration values in the GCD file.
It takes the SLC calibration values from a .pkl file and writes them in the GCD file.

__author__ = Federico Bontempo KIT PhD student <federico.bontempo@kit.edu>
! special thanks to Katherine Rawlins for the help !

How to run:
env-shell.sh python3 write_SLC_Calibration_in_GCD.py \
    --GCD <GCD path> \
    --chargesSumsFile <SLC calibration .pkl path> \
    --outputFile <output path + name + .i3.gz> \
    --startTime <start time> \
    --endTime <end time>

TODO: 
    1. Check if the SLC calibration values for chip = 2 are correct 
    2. Set the correct crossover values
    3. Add the SetCrossOver and GetCrossOver methods to:
        -> src/dataclasses/public/dataclasses/calibration/I3IceTopSLCCalibration.h
        -> src/dataclasses/private/pybindings/I3Calibration/I3VEMCalibration.cxx
"""

import argparse
import json
import sys

from icecube import icetray, dataio, dataclasses

from utils.calculate_p0_p1 import calculate_p0_p1
from utils.utils import tuple_to_str, str_to_tuple


def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("--GCD", type=str, default="", help="GCD path")
    p.add_argument(
        "--chargesSumsFile", type=str, default="", help="SLC calibration .json path"
    )
    p.add_argument(
        "--crossOverPointsFile",
        type=str,
        default="",
        help="Crossover points .json path",
    )
    p.add_argument(
        "--chargesValuesFile", type=str, default="", help="Crossover points .pkl path"
    )
    p.add_argument(
        "--outputFile", type=str, default="", help="Output path + name + .i3.gz"
    )
    p.add_argument("--startTime", type=float, default=0.0, help="Start time")
    p.add_argument("--endTime", type=float, default=0.0, help="End time")

    return p.parse_args()


def __check_args(args):
    if args.GCD == "":
        print("No GCD file given")
        sys.exit(1)
    if args.chargesSumsFile == "":
        print("No SLC calibration file given")
        sys.exit(1)
    if args.crossOverPointsFile == "":
        print("No crossover points file given")
        sys.exit(1)
    if args.outputFile == "":
        print("No output file name given")
        sys.exit(1)
    if args.startTime == 0.0:
        print("No start time given")
        sys.exit(1)
    if args.endTime == 0.0:
        print("No end time given")
        sys.exit(1)
    return


def write_SLC_Calibration_in_Cframe(args, frame, bad_dom_list):
    # This is the calibration frame
    # Load SLC calibration
    with open(args.chargesSumsFile, "r") as f:
        chargesSums_dict = json.load(f)
        """
        slc_calibration_dict is a dictionary with the following structure:
        {
            (OMKey): (
                array([float, float, ... float]), # time
                array([float, float, ... float]), # intercepts
                array([float, float, ... float]), # slopes
            )
            (OMKey): (
                array([float, float, ... float]), # time
                array([float, float, ... float]), # intercepts
                array([float, float, ... float]), # slopes
            )
            ...
        }
        """
        """
        chargesSums_dict is a dictionary with the following structure:
        chargesSums_dict = {
            (OMKey): {
                "chip0atwd0": {
                    "n": int,
                    "x": float,
                    "xx": float,
                    "y": float,
                    "yy": float,
                    "xy": float,
                },
                "chip0atwd1": {
                    "n": int,
                    "x": float,
                    "xx": float,
                    "y": float,
                    "yy": float,
                    "xy": float,
                },
                ... so on for 0, 1 chip and 0, 1, 2 atwd
            }
        """

    # Load crossover points
    with open(args.crossOverPointsFile, "r") as f:
        crossOverPoints = json.load(f)
    """
    crossOverPoints_dict is a dictionary with the following structure:
    {
        (OMKey): (
            float, # crossover point 0-1
            float, # crossover point 1-2
        )
        (OMKey): (
            float, # crossover point 0-1
            float, # crossover point 1-2
        )
        ...
    }
    """

    # Create an instance of the I3IceTopSLCCalibrationCollection
    calibration_collection = dataclasses.I3IceTopSLCCalibrationCollection()

    p0_p1_dict = calculate_p0_p1(chargesSums_dict, bad_dom_list=bad_dom_list)
    for omkey, chipATWdict in p0_p1_dict.items():
        calibration = dataclasses.I3IceTopSLCCalibration()

        string, om = str_to_tuple(omkey)

        # Populate the calibration collection with the loaded SLC calibration values
        for chipATWkey, calibration_values in chipATWdict.items():
            # Eg. chipATWkey = "chip0atwd0"
            # We want to get the chip and atwd values
            chipATWlist = chipATWkey.replace("chip", "").replace("atwd", ",")
            chip, atwd = str_to_tuple(chipATWlist)
            # Get the calibration values
            interceptsCalibration = calibration_values["p0"]
            slopesCalibration = calibration_values["p1"]

            # Set the intercept and slope of the calibration
            calibration.SetIntercept(
                int(chip),
                int(atwd),
                float(interceptsCalibration),
            )
            calibration.SetSlope(
                int(chip),
                int(atwd),
                float(slopesCalibration),
            )

        # make omkey the propper OMKey
        omkey = icetray.OMKey(int(string), int(om))

        # Check if the OMKey is not dead
        if omkey in bad_dom_list:
            # e.g. 2022 dead DOMs "OMKey(74,61,0)" and "OMKey(39,61,0)"
            continue
        elif tuple_to_str(omkey) in crossOverPoints.keys():
            # Get the crossover values
            cop01, cop12 = crossOverPoints[tuple_to_str(omkey)]
            # Set the crossover for unknown chip and unknown atwd
            calibration.SetCrossOver(
                int(1),
                float(10 ** (cop01)),
            )
            calibration.SetCrossOver(
                int(12),
                float(10 ** (cop12)),
            )
        else:
            # Give a run warning
            RuntimeWarning(
                f"OMKey {omkey} has less than 3 ATWDs with charges. Probably something is broken."
            )

        # Set the start and end time of the calibration
        calibration_collection.start_time = dataclasses.I3Time(
            args.startTime
        )  # TODO check time
        calibration_collection.end_time = dataclasses.I3Time(
            args.endTime
        )  # TODO check time
        # make omkey the propper OMKey
        # omkey = icetray.OMKey(int(string), int(om))
        # Add the calibration to the collection
        calibration_collection.it_slc_cal[omkey] = calibration

    # Add the I3IceTopSLCCalibrationCollection to the frame
    frame["I3IceTopSLCCalibrationCollection"] = calibration_collection
    return frame


def get_bad_dom_list(frame):
    """Get the list of bad DOMs from the GCD file"""
    # Get the IceTopBadDOMs from the frame
    bad_dom_list = list(frame["IceTopBadDOMs"])
    return bad_dom_list


def main(args):
    __check_args(args)
    # Load GCD file
    gcd_file = dataio.I3File(args.GCD)
    # Create the new GCD file
    gcd_file_out = dataio.I3File(args.outputFile, "w")
    # Get the Calibration frame
    for frame in gcd_file:
        # Check if the frame is the Detector frame
        if frame.Stop == icetray.I3Frame.DetectorStatus:
            # This is the geometry frame thus we add the the SLC calibration values
            Dframe = frame
            bad_dom_list = get_bad_dom_list(frame)
        # Check if the frame is the calibration frame
        elif frame.Stop == icetray.I3Frame.Calibration:
            # This is the calibration frame thus we add the the SLC calibration values
            Cframe = frame
        else:
            # This is not the calibration frame and is just pushed to the new GCD file
            gcd_file_out.push(frame)

    Cframe = write_SLC_Calibration_in_Cframe(args, Cframe, bad_dom_list)
    gcd_file_out.push(Cframe)
    gcd_file_out.push(Dframe)

    gcd_file_out.close()
    return


if __name__ == "__main__":
    main(args=get_args())
    print("-------------------- Program finished --------------------")
