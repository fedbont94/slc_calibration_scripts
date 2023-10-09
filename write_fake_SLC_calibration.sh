#!/bin/sh

PYTHON=/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/RHEL_7_x86_64/bin/python3
SCRIPT=/home/fbontempo/slcCalibrationScripts/write_fake_SLC_calibration.py

$PYTHON $SCRIPT \
    --slcCalibration "/data/ana/CosmicRay/IceTop_level3/SLCcal/slc_calib_parameters_ic86_2021_v1.pcl" \
    --outputFile "/data/user/fbontempo/slcCalibration/slc_calib_parameters_ic86_fake2025_original2021_v1.pcl" \
<<<<<<< HEAD
    --originalYear 2022 \
=======
    --originalYear 2021 \
>>>>>>> 9a8a5a464515641fed00358c484b8eadab85832d
    --fakeYear 2025 
