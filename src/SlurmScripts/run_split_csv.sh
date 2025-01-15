#!/usr/bin/bash
#SBATCH --job-name=split_csv_osiris
#SBATCH --qos=short
#SBATCH --cpus-per-task=104
#SBATCH --mem=1440G
#SBATCH --time=2-0
#SBATCH --output=split_csv%j.out


cd /home/"$USER"/osirisml/OsirisML/data/csv || exit
python split_csv.py
