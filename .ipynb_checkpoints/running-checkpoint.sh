#!/bin/bash
#SBATCH --job-name=heatwave_detection
#SBATCH --output=heatwave_%j.out
#SBATCH --error=heatwave_%j.err
#SBATCH --partition=GPU-AI
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=1200G
#SBATCH --time=5-00:00:00
#SBATCH --gres=gpu:1

source /apps/compilers/anaconda3-2023.3/etc/profile.d/conda.sh
conda activate mt

cd /home/raj.ayush

python -u code/heatwave_detection.py --original_data data/main/40_years.nc --g_ids 100
