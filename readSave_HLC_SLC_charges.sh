#!/bin/sh

ENV=/data/user/fbontempo/icetray/build/env-shell.sh
PYTHON=/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/RHEL_7_x86_64/bin/python3
SCRIPT=/home/fbontempo/slcCalibrationScripts/readSave_HLC_SLC_charges.py

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`

# Level2_with_I3SLCCalData_2012_burnsample_run120160.i3
# Level2_with_I3SLCCalData_2012_burnsample_run120170.i3
# Level2_with_I3SLCCalData_2012_burnsample_run120180.i3
# Level2_with_I3SLCCalData_2022_burnsample_run136650.i3
# Level2_with_I3SLCCalData_2022_burnsample_run136660.i3
# Level2_with_I3SLCCalData_2022_burnsample_run136670.i3

ehco 2012

$ENV $PYTHON $SCRIPT \
    --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2012_burnsample_run120160.i3" \
    --runNumb 120160 \
    --year 2012 \
    --outputDir "/data/user/fbontempo/slcCalibration/" \
    --frameType "Q" \
    --frameKey "I3ITSLCCalData" \
    --saveJsonl \
    --savePickle

$ENV $PYTHON $SCRIPT \
    --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2012_burnsample_run120170.i3" \
    --runNumb 120170 \
    --year 2012 \
    --outputDir "/data/user/fbontempo/slcCalibration/" \
    --frameType "Q" \
    --frameKey "I3ITSLCCalData" \
    --saveJsonl \
    --savePickle

$ENV $PYTHON $SCRIPT \
    --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2012_burnsample_run120180.i3" \
    --runNumb 120180 \
    --year 2012 \
    --outputDir "/data/user/fbontempo/slcCalibration/" \
    --frameType "Q" \
    --frameKey "I3ITSLCCalData" \
    --saveJsonl \
    --savePickle

echo 2022

$ENV $PYTHON $SCRIPT \
    --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2022_burnsample_run136650.i3" \
    --runNumb 136650 \
    --year 2022 \
    --outputDir "/data/user/fbontempo/slcCalibration/" \
    --frameType "Q" \
    --frameKey "I3ITSLCCalData" \
    --saveJsonl \
    --savePickle

$ENV $PYTHON $SCRIPT \
    --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2022_burnsample_run136660.i3" \
    --runNumb 136660 \
    --year 2022 \
    --outputDir "/data/user/fbontempo/slcCalibration/" \
    --frameType "Q" \
    --frameKey "I3ITSLCCalData" \
    --saveJsonl \
    --savePickle

$ENV $PYTHON $SCRIPT \
    --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2022_burnsample_run136670.i3" \
    --runNumb 136670 \
    --year 2022 \
    --outputDir "/data/user/fbontempo/slcCalibration/" \
    --frameType "Q" \
    --frameKey "I3ITSLCCalData" \
    --saveJsonl \
    --savePickle
