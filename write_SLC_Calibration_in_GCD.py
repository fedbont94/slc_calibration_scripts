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
<<<<<<< HEAD
    2. Set the correct crossover values
    3. Add the SetCrossOver and GetCrossOver methods to:
        -> src/dataclasses/public/dataclasses/calibration/I3IceTopSLCCalibration.h
        -> src/dataclasses/private/pybindings/I3Calibration/I3VEMCalibration.cxx
=======
    2. Do the crossover which I don't even know what it is or how to set it.
>>>>>>> 9a8a5a464515641fed00358c484b8eadab85832d
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


<<<<<<< HEAD
def write_SLC_Calibration_in_GCD(args, frame):
=======
def write_SLC_Calibration_in_GCD(args, frame, gcd_file_out):
>>>>>>> 9a8a5a464515641fed00358c484b8eadab85832d
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
<<<<<<< HEAD
        if not (time >= timeArr[0] and time <= timeArr[-1]):
=======
        if not np.in1d(time, timeArr):
>>>>>>> 9a8a5a464515641fed00358c484b8eadab85832d
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
<<<<<<< HEAD

        # Set the chip = 2 for the unknown chip
        calibration.SetIntercept(
            int(2),
            int(atwd),
            float(interceptsCalibration),  # TODO This is probably not correct
=======
        # TODO Set the chip = 2 
        calibration.SetIntercept(
            int(2),
            int(atwd),
            float(interceptsCalibration), # TODO This is probably not correct
>>>>>>> 9a8a5a464515641fed00358c484b8eadab85832d
        )
        calibration.SetSlope(
            int(2),
            int(atwd),
<<<<<<< HEAD
            float(slopesCalibration),  # TODO This is probably not correct
        )

        # TODO Set the correct crossover
        calibration.SetCrossOver(
            int(1),
            float(0.0),
        )
        calibration.SetCrossOver(
            int(12),
            float(0.0),
        )
=======
            float(slopesCalibration), # TODO This is probably not correct
        )
        # TODO Do the crossover which I don't even know what it is or how to set it.
>>>>>>> 9a8a5a464515641fed00358c484b8eadab85832d

        # Set the start and end time of the calibration
        calibration_collection.start_time = dataclasses.I3Time(startTime)
        calibration_collection.end_time = dataclasses.I3Time(endTime)
        # make omkey the propper OMKey
        omkey = icetray.OMKey(int(string), int(om))
        # Add the calibration to the collection
        calibration_collection.it_slc_cal[omkey] = calibration

<<<<<<< HEAD
    # Add the I3IceTopSLCCalibrationCollection to the frame
    frame["I3IceTopSLCCalibrationCollection"] = calibration_collection
=======
        # Add the I3IceTopSLCCalibrationCollection to the frame
        frame["I3IceTopSLCCalibrationCollection"] = calibration_collection
>>>>>>> 9a8a5a464515641fed00358c484b8eadab85832d
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
<<<<<<< HEAD
        if frame.Stop == icetray.I3Frame.Calibration:
            # This is the calibration frame thus we add the the SLC calibration values
            frame = write_SLC_Calibration_in_GCD(args, frame)
            gcd_file_out.push(frame)
        else:
            # This is not the calibration frame and is just pushed to the new GCD file
            gcd_file_out.push(frame)

=======
        if frame.Stop != icetray.I3Frame.Calibration:
            # This is not the calibration frame and is just pushed to the new GCD file
            gcd_file_out.push(frame)
            continue

        frame = write_SLC_Calibration_in_GCD(args, frame, gcd_file_out)

        gcd_file_out.push(frame)
>>>>>>> 9a8a5a464515641fed00358c484b8eadab85832d
    gcd_file_out.close()
    return


if __name__ == "__main__":
    main(args=get_args())
    print("-------------------- Program finished --------------------")
