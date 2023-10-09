#!/bin/sh

ENV=/data/user/fbontempo/icetray/build/env-shell.sh
PYTHON=/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/RHEL_7_x86_64/bin/python3
SCRIPT=/home/fbontempo/slcCalibrationScripts/write_SLC_Calibration_in_GCD.py

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`

$ENV $PYTHON $SCRIPT \
    --GCD "/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_2020.Run134142.Pass2_V0.i3.gz" \
    --slcCalibration "/data/ana/CosmicRay/IceTop_level3/SLCcal/slc_calib_parameters_ic86_2021_v1.pcl" \
    --chargesValuesFile "/data/user/jsaffer/Data/SLCCal_test.pkl" \
    --output "/home/fbontempo/slcCalibrationScripts/GCD/GeoCalibDetectorStatus_2021.Run135903.T00S1.Pass2_V1b_Snow211115_SLC_calibration.i3.gz" \
    --startTime 59410.0 \
    --endTime 59800.0 
