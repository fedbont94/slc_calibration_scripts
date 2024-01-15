#!/bin/sh

ENV=$HOME/icetray/build/env-shell.sh
PYTHON=/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/RHEL_7_x86_64/bin/python3
SCRIPT=$HOME/slc_calibration_scripts/readSave_HLC_SLC_charges.py

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/setup.sh`

# Level2_with_I3SLCCalData_2012_burnsample_run120160.i3
# Level2_with_I3SLCCalData_2012_burnsample_run120170.i3
# Level2_with_I3SLCCalData_2012_burnsample_run120180.i3
# Level2_with_I3SLCCalData_2022_burnsample_run136650.i3
# Level2_with_I3SLCCalData_2022_burnsample_run136660.i3
# Level2_with_I3SLCCalData_2022_burnsample_run136670.i3

# echo gamma 2.3d 2012

# $ENV $PYTHON $SCRIPT \
#     --runDir "/hkfs/work/workspace/scratch/rn8463-lv3_Simulations/gamma/2012/slcCalibration/Level2_with_I3SLCCalData_2012_MC_sibyll2.3d_gamma.i3.bz2" \
#     --runNumb 14000 \
#     --year 2012 \
#     --outputDir "/hkfs/work/workspace/scratch/rn8463-lv3_Simulations/gamma/2012/slcCalibration/" \
#     --frameType "Q" \
#     --frameKey "I3ITSLCCalData" \
#     --saveJsonl \
#     --savePickle

echo proton 2.3d 2012
$ENV $PYTHON $SCRIPT \
    --runDir "/hkfs/work/workspace/scratch/rn8463-lv3_Simulations/proton/2012/slcCalibration/Level2_with_I3SLCCalData_2012_MC_sibyll2.3d_proton.i3.bz2" \
    --runNumb 14001 \
    --year 2012 \
    --outputDir "/hkfs/work/workspace/scratch/rn8463-lv3_Simulations/proton/2012/slcCalibration/" \
    --frameType "Q" \
    --frameKey "I3ITSLCCalData" \
    --saveJsonl \
    --savePickle


# ehco 2012

# $ENV $PYTHON $SCRIPT \
#     --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2012_burnsample_run120160.i3" \
#     --runNumb 120160 \
#     --year 2012 \
#     --outputDir "/data/user/fbontempo/slcCalibration/" \
#     --frameType "Q" \
#     --frameKey "I3ITSLCCalData" \
#     --saveJsonl \
#     --savePickle

# $ENV $PYTHON $SCRIPT \
#     --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2012_burnsample_run120170.i3" \
#     --runNumb 120170 \
#     --year 2012 \
#     --outputDir "/data/user/fbontempo/slcCalibration/" \
#     --frameType "Q" \
#     --frameKey "I3ITSLCCalData" \
#     --saveJsonl \
#     --savePickle

# $ENV $PYTHON $SCRIPT \
#     --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2012_burnsample_run120180.i3" \
#     --runNumb 120180 \
#     --year 2012 \
#     --outputDir "/data/user/fbontempo/slcCalibration/" \
#     --frameType "Q" \
#     --frameKey "I3ITSLCCalData" \
#     --saveJsonl \
#     --savePickle

# echo 2022

# $ENV $PYTHON $SCRIPT \
#     --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2022_burnsample_run136650.i3" \
#     --runNumb 136650 \
#     --year 2022 \
#     --outputDir "/data/user/fbontempo/slcCalibration/" \
#     --frameType "Q" \
#     --frameKey "I3ITSLCCalData" \
#     --saveJsonl \
#     --savePickle

# $ENV $PYTHON $SCRIPT \
#     --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2022_burnsample_run136660.i3" \
#     --runNumb 136660 \
#     --year 2022 \
#     --outputDir "/data/user/fbontempo/slcCalibration/" \
#     --frameType "Q" \
#     --frameKey "I3ITSLCCalData" \
#     --saveJsonl \
#     --savePickle

# $ENV $PYTHON $SCRIPT \
#     --runDir "/data/user/jsaffer/Data/SLC_calibration/Level2_with_I3SLCCalData_2022_burnsample_run136670.i3" \
#     --runNumb 136670 \
#     --year 2022 \
#     --outputDir "/data/user/fbontempo/slcCalibration/" \
#     --frameType "Q" \
#     --frameKey "I3ITSLCCalData" \
#     --saveJsonl \
#     --savePickle
