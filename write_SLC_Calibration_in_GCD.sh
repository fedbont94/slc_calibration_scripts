#!/bin/sh

ENV=/data/user/fbontempo/icetray/build/env-shell.sh
PYTHON=/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/RHEL_7_x86_64/bin/python3
SCRIPT=/home/fbontempo/slcCalibrationScripts/write_SLC_Calibration_in_GCD.py

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`

$ENV $PYTHON $SCRIPT \
    --GCD "/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115.i3.gz" \
    --chargesSumsFile "/data/user/fbontempo/test/chargeSums_dict.json" \
    --crossOverPointsFile "/data/user/fbontempo/test/crossOvers_dict.json" \
    --output "/home/fbontempo/slcCalibrationScripts/GCD/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115_SLC_calibration.i3.gz" \
    --startTime 59410.0 \
    --endTime 59800.0 
