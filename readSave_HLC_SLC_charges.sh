#!/bin/sh

ENV=/data/user/fbontempo/icetray/build/env-shell.sh
PYTHON=/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/RHEL_7_x86_64/bin/python3
SCRIPT=/home/fbontempo/slcCalibrationScripts/readSave_HLC_SLC_charges.py

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`

$ENV $PYTHON $SCRIPT \
    --runDir "/data/exp/IceCube/2023/filtered/PFFilt/090[67]/PFFilt_PhysicsFiltering_Run00138329_Subrun00000000_00000000*.tar.bz2" \
    --runNumb 138329 \
    --year 2023 \
    --outputDir "/data/user/fbontempo/test/" \
    --frameType "P" \
    --frameKey "I3ITSLCCalData" \
    --saveJsonl \
    --savePickle

# $ENV $PYTHON $SCRIPT \
#     --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2012_burnsample_run120160.i3" \
#     --runNumb 120160 \
#     --year 2012 \
#     --outputDir "/data/user/fbontempo/test/" \
#     --frameType "Q" \
#     --frameKey "I3ITSLCCalData" \
#     --saveJsonl \
#     --savePickle
