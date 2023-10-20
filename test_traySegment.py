#!/usr/bin/env python

########################################################################
# Run analysis-level processing on I3 Files, store as HDF Files
########################################################################

import argparse
import os
import sys
import glob
import pathlib
import numpy as np

from I3Tray import I3Tray
from icecube import icetray, dataio, dataclasses, phys_services, toprec
from icecube import tableio, coinc_twc, static_twc  # , SeededRTCleaning
from icecube.tableio import I3TableWriter
from icecube.hdfwriter import I3HDFTableService
from icecube.recclasses import I3LaputopParams, LaputopParameter
from icecube.icetop_Level3_scripts.functions import count_stations
from icecube.frame_object_diff.segments import uncompress
from icecube.hdfwriter import I3HDFWriter

# from icecube.rock_bottom import I3RbParameterMap
from icecube.gulliver import I3LogLikelihoodFitParams

# Messages set to warning
# icetray.set_log_level(icetray.I3LogLevel.LOG_WARN)

# Messages set to error
icetray.set_log_level(icetray.I3LogLevel.LOG_ERROR)

from utils.Agnostic_I3IceTopSLCCalibrator import Calibrate_Orphaned_SLCVEMPulses


def main():
    gcd = [
        "/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_2012.56063_V1_OctSnow.i3.gz"
    ]
    in_files = glob.glob(
        "/data/sim/IceTop/2012/filtered/CORSIKA-ice-top/12360/level2_Elinks/5.0/Level2_IC86_corsika_icetop.010410.000091.i3.bz2"
    )
    tray = I3Tray()

    tray.AddModule("I3Reader", "Reader", FilenameList=gcd + in_files)

    tray.Add(
        Calibrate_Orphaned_SLCVEMPulses,
        "SLCCalibrator",
        SLCcalibfile="/data/user/fbontempo/slcCalibration/test/Run120160_2012ITSLCChargeCalResults.jsonl",  # <- give it the right year!
        SLCVEMPulses="OfflineIceTopSLCVEMPulses",
        SLCTankPulses="OfflineIceTopSLCTankPulses",
    )

    # ---------------------------------------------------------------------
    #           Writing
    # ---------------------------------------------------------------------

    # Write events to an i3 file
    tray.AddModule(
        "I3Writer",
        "i3writer",
        Filename="/home/fbontempo/temp/test_SLC_Calibration.i3.bz2",
        # Filename=args.output_directory + "/" + "temp_" + basename + ".i3.bz2",
        Streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics],
    )

    # Write events to an HDF file
    # tray.Add(
    #     I3HDFWriter,
    #     keys=keys,
    #     Output=f"{args.output_directory}/temp_{basename}.hdf5",
    #     SubEventStreams=["IceTopSplit", "SubEventStreams", "ice_top"],
    #     BookEverything=False,
    # )

    tray.AddModule("TrashCan", "Done")
    tray.Execute()
    tray.Finish()


if __name__ == "__main__":
    main()
