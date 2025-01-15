#!/usr/bin/bash
#SBATCH --job-name=combine_csvs_osiris
#SBATCH --qos=short
#SBATCH --cpus-per-task=104
#SBATCH --mem=1440G
#SBATCH --time=2-0
#SBATCH --output=combine_csvs%j.out


cd /home/"$USER"/osirisml/OsirisML/data/csv || exit
python combine_pcaps.py