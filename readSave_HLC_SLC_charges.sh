#!/bin/sh

ENV=/data/user/fbontempo/icetray/build/env-shell.sh
PYTHON=/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/RHEL_7_x86_64/bin/python3
SCRIPT=/home/fbontempo/slcCalibrationScripts/readSave_HLC_SLC_charges.py

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`
$ENV $PYTHON $SCRIPT
