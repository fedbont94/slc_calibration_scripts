#! /usr/bin/env python3
"""
This script writes the SLC calibration values into a fake SLC calibration file.
It takes the SLC calibration values from a .pkl file and writes them in the fake SLC calibration file.
It is used to overcome the problem of not having the SLC calibration file for future years.

__author__ = Federico Bontempo KIT PhD student <federico.bontempo@kit.edu>

How to run:
python3 write_fake_SLC_calibration.py \
    --slcCalibration <SLC calibration .pkl path> \
    --outputFile <output path + name + .pkl> \
    --originalYear <original year> \
    --fakeYear <fake year>
"""

import argparse 
import datetime
import pickle
import sys
import os


def get_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--slcCalibration", type=str, default="", help="SLC calibration .pkl path"
    )
    p.add_argument(
        "--outputFile", type=str, default="", help="Output path + name + .pkl"
    )
    p.add_argument("--originalYear", type=int, default=0, help="The time of the original SLC calibration")
    p.add_argument("--fakeYear", type=int, default=0, help="The time of the fake SLC calibration")

    return p.parse_args()


def __check_args(args):
    if args.slcCalibration == "" or not os.path.exists(args.slcCalibration):
        print("No SLC calibration file given or file does not exist")
        sys.exit(1)
    if args.outputFile == "" or not os.path.exists(os.path.dirname(args.outputFile)):
        print("No output file name given or directory does not exist")
        sys.exit(1)
    if args.originalYear == 0:
        print("No original year given")
        sys.exit(1)
    if args.fakeYear == 0:
        print("No fake year given")
        sys.exit(1)
    return


def write_fake_SLC_calibration(args):
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

    # Create fake SLC calibration
    fake_slc_calibration = slc_calibration.copy()

    # Get the difference in years between the original and fake SLC calibration
    # Calculate the difference in mjd between the original and fake SLC calibration
    timeDifference = datetime.timedelta(days=365) * (args.fakeYear - args.originalYear)
    # Make the time difference in mjd
    timeDifference = timeDifference.total_seconds() / 86400 # seconds in a day

    # Add the difference in mjd to the original SLC cal
    for omkey in fake_slc_calibration.keys():
        # Add the time difference to the time array
        newTime = fake_slc_calibration[omkey][0] + timeDifference
        # Create the new SLC cal
        newSlcCal = (newTime, fake_slc_calibration[omkey][1], fake_slc_calibration[omkey][2])
        # Add the new SLC cal to the fake SLC cal
        fake_slc_calibration[omkey] = newSlcCal
        
    # Write fake SLC calibration
    with open(args.outputFile, "wb") as f:
        pickle.dump(fake_slc_calibration, f)
    return


if __name__ == "__main__":

    args = get_args()
    __check_args(args)

    write_fake_SLC_calibration(args)

    print("-------------------- Program finished --------------------")