#!/usr/bin/bash
#SBATCH --job-name=split_csv_by_TTL
#SBATCH --qos=short
#SBATCH --cpus-per-task=104
#SBATCH --mem=1440G
#SBATCH --time=14-0
#SBATCH --output=split_csv_by_ttl%j.out

cd /home/"$USER"/osirisml/OsirisML/data/csv || exit
python split_csv_by_TTL.py parsed_bitfields_except_opt.csv
