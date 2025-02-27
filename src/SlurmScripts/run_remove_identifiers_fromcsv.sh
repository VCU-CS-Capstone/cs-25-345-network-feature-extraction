#!/usr/bin/bash
#SBATCH --job-name=clean_csvs
#SBATCH --qos=short
#SBATCH --cpus-per-task=104
#SBATCH --mem=1440G
#SBATCH --time=14-0
#SBATCH --output=clean_csv%j.out


cd /home/"$USER"/osirisml/OsirisML/data/csv || exit
python remove_identifiers_fromcsv.py combined_train.csv combined_train_cleaned.csv
python remove_identifiers_fromcsv.py combined_train_small.csv combined_train_small_cleaned.csv
