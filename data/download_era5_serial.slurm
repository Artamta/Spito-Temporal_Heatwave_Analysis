#!/bin/bash
#SBATCH --job-name=era5_serial
#SBATCH --output=era5_serial.log
#SBATCH --error=era5_serial.err
#SBATCH --time=48:00:00
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1

source ~/.bashrc
conda init
conda activate mt

python /home/raj.ayush/data/api.py
