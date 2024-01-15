#! /usr/bin/env python3
"""
This script provides a data processing pipeline for getting the calibration constants needed for the SLC calibration. 
It reads input files containing calibration data and performs necessary calculations to obtain calibration parameters (p0, p1) and crossover points. 
The results can be saved in JSONL and pickle file formats.

__author__ = Federico Bontempo KIT PhD student <federico.bontempo@kit.edu>
! special thanks to Katherine Rawlins for the help !

Usage:
Ensure you have the necessary dependencies installed, including the IceCube software framework.

Run the script using Python in the icetray environment:
    python3 readSave_HLC_SLC_charges.py [options]
    
Options
    --runDir: Path to the directory containing the calibration data for a specific run.
    --runNumb: Run number for which the calibration is being performed.
    --year: Year of the calibration.
    --outputDir: Path to the directory where the results will be saved.
    --frameType: Frame type, either "Q" and/or "P".
    --frameKey: Frame object name for the SLC calibration data.
    --saveJsonl: Save the results in a JSONL file.
    --savePickle: Save the results in a pickle file.

Functions:
    get_args(): Parses the command-line arguments and returns the arguments as a namespace.
    __check_args(args): Checks if the required arguments are provided and exits the program if any are missing.
    save_jsonl(): Saves the calibration results, including p0, p1, and crossover points, in a JSONL file.
    save_pickle(): Saves the calibration results, including p0, p1, and crossover points, in pickle files.
    read_calibrationFromRuns(): Reads calibration data from input files and extracts calibration information for further processing.
    main(): Main function to coordinate the calibration process and save the results.

Dependencies:
    argparse: For parsing command-line arguments.
    glob: For finding files matching a specified pattern.
    json: For handling JSON data.
    pickle: For serializing and deserializing Python objects.
    sys: For system-specific parameters and functions.
    numpy: For numerical operations and array handling.
    icecube: The IceCube software framework for data handling and calculations.
    utils.crossover_points: Custom utility function to calculate crossover points.
    utils.calculate_p0_p1: Custom utility function to calculate p0 and p1 calibration parameters.
"""

import argparse
import glob
import json
import pickle
import sys
import numpy as np

from icecube import icetray, dataio, vemcal

from utils.crossover_points import calculate_crossOverPoints
from utils.calculate_p0_p1 import calculate_p0_p1


def get_args():
    """
    Parse the command-line arguments and return the arguments as a namespace.
    """
    p = argparse.ArgumentParser()
    p.add_argument("--runDir", type=str, default="", help="Run directory")
    p.add_argument("--runNumb", type=int, default=0, help="Run number")
    p.add_argument("--year", type=int, default=0, help="Year")
    p.add_argument("--outputDir", type=str, default="", help="Output directory")
    p.add_argument(
        "--frameType", type=str, default="", help="Frame type either Q and/or P"
    )
    p.add_argument(
        "--frameKey",
        type=str,
        default="I3ITSLCCalData",
        help="Frame object name of the SLC calibration data",
    )
    p.add_argument(
        "--saveJsonl", action="store_true", help="Save the results in a jsonl file"
    )
    p.add_argument(
        "--savePickle", action="store_true", help="Save the results in a pickle file"
    )
    return p.parse_args()


def __check_args(args):
    """
    Check if the required arguments are provided and exit the program if any are missing.
    ----------------------------------
    Parameters:
        args: Command-line arguments.
    """
    if args.runDir == "":
        print("No run directory given")
        sys.exit(1)
    if args.runNumb == 0:
        print("No run number given")
        sys.exit(1)
    if args.year == 0:
        print("No year given")
        sys.exit(1)
    if args.outputDir == "":
        print("No output directory given")
        sys.exit(1)
    if args.frameType == "":
        print("No frame type given")
        sys.exit(1)
    if not args.saveJsonl and not args.savePickle:
        Warning("No save option selected")
    return


def save_jsonl(p0_p1_dict, crossOvers_dict, startTime, endTime, args):
    """
    Save the p0 and p1 and corssover points values in a jsonl file
    ----------------------------------
    Parameters:
        p0_p1_dict: A dictionary containing the calculated p0 and p1 values, errors, chi-squared values, and other related statistics for each OMKey.
        crossOvers_dict: A dictionary containing the crossover points for each OMKey.
        startTime: Start time of the calibration.
        endTime: End time of the calibration.
        args: Command-line arguments.
    """
    fileName = (
        f"{args.outputDir}/Run{args.runNumb}_{args.year}ITSLCChargeCalResults.jsonl"
    )
    with open(fileName, "w") as f:
        for SOCAkey, valuesDict in p0_p1_dict.items():
            string, om, chip, atwd = SOCAkey
            omkey = icetray.OMKey(string, om)
            # check if the key is there aka if the dom is not dead
            if crossOvers_dict.get(omkey) is None:
                cop = -1
            elif atwd == 0:
                cop = crossOvers_dict[omkey][0]
            elif atwd == 1:
                cop = crossOvers_dict[omkey][1]
            else:
                cop = -1

            # save each line in a dictionary in a jsonl file
            jsonDict = {
                "_id": "64f9cd9e19368f",
                "service": "PFMoniWriter",
                "varname": "ITSLCChargeCalResults",
                "value": {
                    "string": string,
                    "om": om,
                    "chip": chip,
                    "channel": atwd,
                    "runNumber": args.runNumb,
                    "subrunNumber": 0,
                    "version": 0,
                    "recordingStartTime": f"{startTime}",
                    "recordingStopTime": f"{endTime}",
                    "result": {
                        "chi2": valuesDict["chi2"],
                        "n": valuesDict["n"],
                        "p0": valuesDict["p0"],
                        "p0_error": valuesDict["p0_error"],
                        "p1": valuesDict["p1"],
                        "p1_error": valuesDict["p1_error"],
                        "sum_x": valuesDict["x"],
                        "sum_xx": valuesDict["xx"],
                        "sum_xy": valuesDict["xy"],
                        "sum_y": valuesDict["y"],
                        "sum_yy": valuesDict["yy"],
                        "crossover": cop,
                    },
                },
                "prio": 3,
                "time": "2023-09-07 13:18:21.986000",
                "insert_time": "2023-09-08 06:02:47.940807",
            }
            json.dump(jsonDict, f)
            f.write("\n")
    print(f"Saved {fileName}")
    return


def save_pickle(p0_p1_dict, crossOvers_dict, args):
    """
    Save the p0 and p1 and corssover points values in 2 pickle files
    """
    # Save the p0 and p1 values in a pickle file
    fileName = f"{args.outputDir}/Run{args.runNumb}_{args.year}_chargeSums_dict.pkl"
    with open(fileName, "wb") as f:
        pickle.dump(p0_p1_dict, f)
    print(f"Saved {fileName}")

    # Save the crossover points values in a pickle file
    fileName = f"{args.outputDir}/Run{args.runNumb}_{args.year}_crossOvers_dict.pkl"
    with open(fileName, "wb") as f:
        pickle.dump(crossOvers_dict, f)
    print(f"Saved {fileName}")

    return


def read_calibrationFromRuns(
    slc_hlc_q_dict,
    slc_hlc_sum_q_dict,
    files_list,
    runNumb,
    frameType,
    startTime=None,
    slcdata_name="I3ITSLCCalData",
):
    """
    Read calibration data from input files and extract calibration information for further processing.
    ----------------------------------
    Parameters:
        slc_hlc_q_dict: A dictionary of OMKeys with empty arrays for each ATWD array shape: (2, 0).
        slc_hlc_sum_q_dict: A dictionary of OMKeys with empty dictionaries for each chip and ATWD.
        files_list: A list of files containing the runs data.
        runNumb: Run number for which the calibration is being performed.
        startTime: Start time of the calibration.
        slcdata_name: Frame object name for the SLC calibration data.
    """
    for f in sorted(files_list):
        print(f"Reading file {f}")
        for frame in dataio.I3File(f):
            # Is this one of the streams you wanted (Q or P)?
            framesList = []
            if "Q" in frameType:
                framesList.append(icetray.I3Frame.DAQ)
            if "P" in frameType:
                framesList.append(icetray.I3Frame.Physics)

            if frame.Stop not in framesList:
                continue
            # IF there is no slc calibration information, skip
            if slcdata_name not in frame:
                continue

            slcdata = frame[slcdata_name]

            # At Lv2, all frames have an I3EventHeader, but this is not true for PFFilt
            if frame.Has("I3EventHeader"):
                header = frame["I3EventHeader"]

                if startTime is None:
                    startTime = header.start_time
                    endTime = header.end_time
                if endTime < header.end_time:
                    endTime = header.end_time

                ## Run number sanity checks
                # if not header.run_id == runNumb:
                #     SystemExit(
                #         "I3EventHeader and I3ITSLCCalItem run numbers do not match!"
                #     )

            itemlist = slcdata.HLC_vs_SLC_Hits

            for calkey in itemlist:
                # It's just a vector of Items; Each "calkey" is a ITSCLCalItem
                ## Each "calkey" is a custom lightweight object... extract the info!
                omkey = icetray.OMKey(calkey.string, calkey.om)
                chip = calkey.chip
                atwd = calkey.atwd

                ## What is stored is "deci-photoelectrons"
                hlcc = calkey.hlc_charge_dpe / 10.0
                slcc = calkey.slc_charge_dpe / 10.0

                # Add the calibration to the collection
                slc_hlc_q_dict[omkey][f"atwd{atwd}"] = np.append(
                    slc_hlc_q_dict[omkey][f"atwd{atwd}"], [[slcc], [hlcc]], axis=1
                )

                # Add the calibration to the sum collection for the p0 p1 fit
                slc_hlc_sum_q_dict[omkey][f"chip{chip}atwd{atwd}"]["n"] += 1
                slc_hlc_sum_q_dict[omkey][f"chip{chip}atwd{atwd}"]["x"] += slcc
                slc_hlc_sum_q_dict[omkey][f"chip{chip}atwd{atwd}"]["xx"] += slcc**2
                slc_hlc_sum_q_dict[omkey][f"chip{chip}atwd{atwd}"]["y"] += hlcc
                slc_hlc_sum_q_dict[omkey][f"chip{chip}atwd{atwd}"]["yy"] += hlcc**2
                slc_hlc_sum_q_dict[omkey][f"chip{chip}atwd{atwd}"]["xy"] += slcc * hlcc

        print(f"Completed file {f}")
    return startTime, endTime


def main(args):
    """
    Main function to coordinate the calibration process and save the results.
    ----------------------------------
    Parameters:
        args: Command-line arguments.
    """
    __check_args(args=args)

    files_list = sorted(glob.glob(f"{args.runDir}"))

    # Create a dictionary of OMKeys with
    # empty arrays for each ATWD array shape: (2, 0)
    # 1. array slc calibration
    # 2. array hlc calibration
    slc_hlc_q_dict = {}
    slc_hlc_sum_q_dict = {}

    for string in range(1, 82):
        for om in range(61, 65):
            omkey = icetray.OMKey(string, om)
            slc_hlc_q_dict[omkey] = {
                "atwd0": np.array([[], []]),
                "atwd1": np.array([[], []]),
                "atwd2": np.array([[], []]),
            }
            chipATWDkeys = [
                "chip0atwd0",
                "chip0atwd1",
                "chip0atwd2",
                "chip1atwd0",
                "chip1atwd1",
                "chip1atwd2",
            ]
            slc_hlc_sum_q_dict[omkey] = {
                cakey: {
                    "n": 0,
                    "x": 0.0,
                    "xx": 0.0,
                    "y": 0.0,
                    "yy": 0.0,
                    "xy": 0.0,
                }
                for cakey in chipATWDkeys
            }

    startTime, endTime = read_calibrationFromRuns(
        slc_hlc_q_dict=slc_hlc_q_dict,
        slc_hlc_sum_q_dict=slc_hlc_sum_q_dict,
        files_list=files_list,
        runNumb=args.runNumb,
        frameType=args.frameType,
        slcdata_name=args.frameKey,
    )

    crossOvers_dict = calculate_crossOverPoints(slc_hlc_q_dict, bad_doms_list=[])
    """
    crossOvers_dict = {
        OMKey: crossover_atwd01, crossover_atwd12
        ...
        }
    """
    p0_p1_dict = calculate_p0_p1(slc_hlc_sum_q_dict, bad_dom_list=[])

    """
    p0_p1_dict[(string, om, chip, atwd)]= {
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
    """

    print("Saving results")
    # Save the p0 and p1 and crossover points values in a jsonl file
    if args.saveJsonl:
        save_jsonl(p0_p1_dict, crossOvers_dict, startTime, endTime, args)
    # Save the p0 and p1 and crossover points values in 2 pickle files
    if args.savePickle:
        save_pickle(p0_p1_dict, crossOvers_dict, args)


if __name__ == "__main__":
    main(args=get_args())
    print("-------------------- Program finished --------------------")
