"""
# Script Documentation

## Overview

The provided script is designed for processing IceCube data using the IceTray framework. 
The script involves extracting HLC charges and saving them as SLC charges for future calibration. 
Additionally, it performs cleanup by removing unnecessary frame objects.

## Usage

The script can be run from the command line and accepts several optional arguments:

- `--gcd`: Path to the Geometry, Calibration, and Detector (GCD) file.
- `--infiles`: Path or pattern to the input IceCube data files.
- `--outfile`: Path to the output IceCube data file.

### Example Usage

```bash
python script_name.py --gcd /path/to/gcd.i3 --infiles "/path/to/data/*.i3" --outfile /path/to/output.i3
```

__author__ = "Saffer, Julian", "Bontempo, Federico"
"""


import glob
import argparse

from I3Tray import I3Tray

from icecube import icetray, dataclasses, dataio, vemcal
from icecube.filterscripts.icetop_slccal import ExtractHLCsAsSLCs


def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("--gcd", type=str, default="", help="GCD file")
    p.add_argument("--infiles", type=str, default="", help="input i3 file(s)")
    p.add_argument("--outfile", type=str, default="", help="output i3 file")
    return p.parse_args()


def main_traySegment(args):
    gcd = glob.glob(args.gcd)
    fileList = glob.glob(args.infiles, recursive=True)

    tray = I3Tray()
    tray.Add("I3Reader", "reader", FileNameList=gcd + fileList)

    # Extract HLC-as-SLC charges and save for future SLC calibration.
    # Input = "CleanIceTopRawData",
    # Output = small "I3SLCCalibData" frame object

    tray.AddSegment(ExtractHLCsAsSLCs, "IceTop_SLCprep")

    # Cleanup of frame objects no longer needed
    my_garbage = [
        "I3MCPESeriesMap",
        "I3MCPulseSeriesMap",
        "I3MCPulseSeriesMapParticleIDMap",
        "I3MCTree",
        "IceTopRawData",
        "InIceRawData",
        "MMCTrackList",
        "I3SuperDST",
        "CleanIceTopRawData",
    ]

    tray.Add("Delete", "SLCCal_cleanup", keys=my_garbage)

    tray.AddModule(
        "I3Writer",
        "i3-writer",
        Filename=args.outfile,
        streams=[
            icetray.I3Frame.TrayInfo,
            icetray.I3Frame.Simulation,
            icetray.I3Frame.DAQ,
        ],
    )

    tray.Execute()


if __name__ == "__main__":
    main_traySegment(args=get_args())
    print("-------------------- Program Finished --------------------")
