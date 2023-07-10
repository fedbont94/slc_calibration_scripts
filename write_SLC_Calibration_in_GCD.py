#! /usr/bin/env python3
"""
This script writes the SLC calibration values in the GCD file.
It takes the SLC calibration values from a .pkl file and writes them in the GCD file.

__author__ = Federico Bontempo KIT PhD student <federico.bontempo@kit.edu>
! special thanks to Katherine Rawlins for the help !

How to run:
env-shell.sh python3 write_SLC_Calibration_in_GCD.py \
    --GCD <GCD path> \
    --slcCalibration <SLC calibration .pkl path> \
    --outputFile <output path + name + .i3.gz> \
    --startTime <start time> \
    --endTime <end time>

TODO: 
    1. Check if the SLC calibration values for chip = 2 are correct 
    2. Do the crossover which I don't even know what it is or how to set it.
"""

import argparse
import pickle
import sys

import scipy
import numpy as np

from icecube import icetray, dataio, dataclasses


def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("--GCD", type=str, default="", help="GCD path")
    p.add_argument(
        "--slcCalibration", type=str, default="", help="SLC calibration .pkl path"
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
    if args.slcCalibration == "":
        print("No SLC calibration file given")
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


def write_SLC_Calibration_in_GCD(args, frame, gcd_file_out):
    # This is the calibration frame
    # Load SLC calibration
    with open(args.slcCalibration, "rb") as f:
        slc_calibration = pickle.load(f)
        """
        slc_calibration is a dictionary with the following structure:
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
    # Create an instance of the I3IceTopSLCCalibrationCollection
    calibration_collection = dataclasses.I3IceTopSLCCalibrationCollection()

    # Populate the calibration collection with the loaded SLC calibration values
    for omkey, calibration_values in slc_calibration.items():
        calibration = dataclasses.I3IceTopSLCCalibration()
        string, om, chip, atwd = omkey

        # print(len(calibration_values))
        timeArr, interceptArr, slopeArr = calibration_values  # aka p0 p1 p2

        startTime, endTime = args.startTime, args.endTime
        # Get the time in the middle of the interval
        time = (startTime + endTime) / 2

        # Check if the time is in the timeArr
        if not np.in1d(time, timeArr):
            sys.exit(
                "Time not in start time and end time of the slc calibration file."
                + "\nCheck the start time, end time and the slc calibration file"
                + f"\nStart time: {timeArr[0]}"
                + f"\nEnd time: {timeArr[-1]}"
            )
        # Interpolate the calibration values
        interceptsCalibration = scipy.interp(time, timeArr, interceptArr)
        slopesCalibration = scipy.interp(time, timeArr, slopeArr)
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
        # TODO Set the chip = 2 
        calibration.SetIntercept(
            int(2),
            int(atwd),
            float(interceptsCalibration), # TODO This is probably not correct
        )
        calibration.SetSlope(
            int(2),
            int(atwd),
            float(slopesCalibration), # TODO This is probably not correct
        )
        # TODO Do the crossover which I don't even know what it is or how to set it.

        # Set the start and end time of the calibration
        calibration_collection.start_time = dataclasses.I3Time(startTime)
        calibration_collection.end_time = dataclasses.I3Time(endTime)
        # make omkey the propper OMKey
        omkey = icetray.OMKey(int(string), int(om))
        # Add the calibration to the collection
        calibration_collection.it_slc_cal[omkey] = calibration

        # Add the I3IceTopSLCCalibrationCollection to the frame
        frame["I3IceTopSLCCalibrationCollection"] = calibration_collection
    return frame


def main(args):
    __check_args(args)
    # Load GCD file
    gcd_file = dataio.I3File(args.GCD)
    # Create the new GCD file
    gcd_file_out = dataio.I3File(args.outputFile, "w")
    # Get the Calibration frame
    for frame in gcd_file:
        # Check if the frame is the calibration frame
        if frame.Stop != icetray.I3Frame.Calibration:
            # This is not the calibration frame and is just pushed to the new GCD file
            gcd_file_out.push(frame)
            continue

        frame = write_SLC_Calibration_in_GCD(args, frame, gcd_file_out)

        gcd_file_out.push(frame)
    gcd_file_out.close()
    return


if __name__ == "__main__":
    main(args=get_args())
    print("-------------------- Program finished --------------------")
