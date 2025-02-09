#!/usr/bin/bash
#SBATCH --job-name=parse_bitfields_chunks
#SBATCH --qos=short
#SBATCH --cpus-per-task=104
#SBATCH --mem=1440G
#SBATCH --time=2-0
#SBATCH --output=parse_bitfields_chunks%j.out


cd /home/"$USER"/osirisml/OsirisML/data/csv || exit
python parse_bitfields.py combined_train_small.csv parsed_bitfields_with_chunks.csv
