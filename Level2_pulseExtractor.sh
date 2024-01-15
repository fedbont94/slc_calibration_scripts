#! /bin/bash

# gcd = '/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_2012.56063_V1_OctSnow.i3.gz'
# infiles = '/hkfs/work/workspace/scratch/rn8463-gamma-detectorResponse/filtered/level2/Level2_IC86.2012_corsika_icetop.14000/data/**/*.i3.bz2'
# outfile = '/hkfs/work/workspace/scratch/rn8463-lv3_Simulations/gamma/2012/slcCalibration/Level2_with_I3SLCCalData_2012_MC_sibyll2.3d_gamma.i3.bz2'

ENV=$HOME/icetray/build/env-shell.sh
PYTHON=/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/RHEL_7_x86_64/bin/python3
SCRIPT=/home/hk-project-pevradio/rn8463/slc_calibration_scripts/Level2_pulseExtractor.py

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/setup.sh`

echo gamma 2.3d 2012
$ENV $PYTHON $SCRIPT \
    --gcd "/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_2012.56063_V1_OctSnow.i3.gz" \
    --infiles "/hkfs/work/workspace/scratch/rn8463-gamma-detectorResponse/filtered/level2/Level2_IC86.2012_corsika_icetop.14000/data/**/*.i3.bz2" \
    --outfile "/hkfs/work/workspace/scratch/rn8463-lv3_Simulations/gamma/2012/slcCalibration/Level2_with_I3SLCCalData_2012_MC_sibyll2.3d_gamma.i3.bz2" 

echo proton 2.3d 2012
$ENV $PYTHON $SCRIPT \
    --gcd "/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_2012.56063_V1_OctSnow.i3.gz" \
    --infiles "/hkfs/work/workspace/scratch/rn8463-proton_DetectorResponseITonly/2012/filtered/level2/Level2_IC86.2012_corsika_icetop.14001/data/**/*.i3.bz2" \
    --outfile "/hkfs/work/workspace/scratch/rn8463-lv3_Simulations/proton/2012/slcCalibration/Level2_with_I3SLCCalData_2012_MC_sibyll2.3d_proton.i3.bz2"