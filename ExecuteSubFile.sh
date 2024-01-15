#!/bin/sh
if [ "$1" = "gpu" ]
then
    sbatch --partition=accelerated --gres=gpu:4 SubFile.sub
else
    sbatch --partition=cpuonly SubFile.sub
fi
