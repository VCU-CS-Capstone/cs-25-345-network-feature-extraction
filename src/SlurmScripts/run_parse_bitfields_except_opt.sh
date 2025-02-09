#!/usr/bin/bash
#SBATCH --job-name=parse_bitfields_except_opt
#SBATCH --qos=short
#SBATCH --cpus-per-task=104
#SBATCH --mem=1440G
#SBATCH --time=14-0
#SBATCH --output=parse_bitfields_except_opt%j.out


start_time=$(date +%s)

cd /home/"$USER"/osirisml/OsirisML/data/csv || exit

python parse_bitfields_except_opt.py combined_train_small.csv parsed_bitfields_except_opt.csv
# then need to split by ttl
# then train on each ttl



end_time=$(date +%s)

runtime=$((end_time - start_time))

runtime_formatted=$(printf '%02dh:%02dm:%02ds\n' $((runtime/3600)) $((runtime%3600/60)) $((runtime%60)))
echo "Script runtime: $runtime_formatted"
