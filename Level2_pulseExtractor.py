import glob
import argparse

from I3Tray import I3Tray

from icecube import icetray, dataclasses, dataio, vemcal
from icecube.filterscripts.icetop_slccal import ExtractHLCsAsSLCs

# from icecube.filterscripts.vemcal import IceTopVEMCal

# gcd = '/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_2012.56063_V1_OctSnow.i3.gz'
# infiles = '/hkfs/work/workspace/scratch/rn8463-gamma-detectorResponse/filtered/level2/Level2_IC86.2012_corsika_icetop.14000/data/**/*.i3.bz2'
# outfile = '/hkfs/work/workspace/scratch/rn8463-lv3_Simulations/gamma/2012/slcCalibration/Level2_with_I3SLCCalData_2012_MC_sibyll2.3d_gamma.i3.bz2'


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
