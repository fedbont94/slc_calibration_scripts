# Write slc calibrations into the Calibration frame
*The script for writing the slc calibrations into the Calibration frame of a GCD*

__author__ Federico Bontempo KIT PhD student <federico.bontempo@kit.edu>

! special thanks to Katherine Rawlins for the help !

Files description:

    README.md:
        This file
    
    ---------- SLC calibration ----------
    # Step 1.

    Level2_pulseExtractor.py: 
        The script involves extracting HLC charges and saving them as SLC charges for calibration. 
    
    Level2_pulseExtractor.sh
        is the shell script that can be used for running the python script. 
        Modify the variables accordingly
    
    # Step 2.

    readSave_HLC_SLC_charges.py:
        This script provides a data processing pipeline for getting 
        the calibration constants needed for the SLC calibration. 
        It reads input files containing calibration data and 
        performs necessary calculations to obtain 
        calibration parameters (p0, p1) and crossover points. 
        The results can be saved in JSONL and pickle file formats.

    readSave_HLC_SLC_charges.sh:
        is the shell script that can be used for running the python script. 
        Modify the variables accordingly



    ---------- Write the SLC calibration in the file ----------

    writing_SLC_Calibration_in_GCD.py: 
        is the python script used for creating the new GCD file with 
        the a new frame object that can be used for the calibration of SLCs. 

    writing_SLC_Calibration_in_GCD.sh:
        is the shell script that can be used for running the python script. 
        Modify the variables accordingly



    ---------- Create fake SLC calibration for future years ----------

    write_fake_SLC_calibration.py:
        is the python script using for creating a fake slc calibration pkl file. 
        It can be used for future years in which the pkl does not exists.
    
    write_fake_SLC_calibration.sh:
        is the shell script that can be used for running the python script. 
        Modify the variables accordingly

