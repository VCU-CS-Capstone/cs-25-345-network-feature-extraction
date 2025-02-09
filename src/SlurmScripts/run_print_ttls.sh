#!/usr/bin/bash
#SBATCH --job-name=printTTLs
#SBATCH --qos=short
#SBATCH --cpus-per-task=104
#SBATCH --mem=1440G
#SBATCH --time=14-0
#SBATCH --output=print_ttls%j.out

cd /home/"$USER"/osirisml/OsirisML/data/csv || exit
python printTTLs.py parsed_bitfields_with_chunks.csv