#!/usr/bin/bash
#SBATCH --job-name=compressed_bitfields_mining_test
#SBATCH --qos=short
#SBATCH --cpus-per-task=104
#SBATCH --mem=1440G
#SBATCH --time=14-0
#SBATCH --output=compressed_bitfields_mining_test%j.out

start_time=$(date +%s)

cd /home/"$USER"/osirisml/OsirisML/model || exit

# remove this once i test
# python hyperparameter_tuning_randomsearch_no_removal.py parsed_bitfields_except_opt.csv

python hyperparameter_tuning_randomsearch_no_removal.py combined_train_small_parsed_bitfields_except_opt_ttl128.csv
python hyperparameter_tuning_randomsearch_no_removal.py combined_train_small_parsed_bitfields_except_opt_ttl64.csv
python hyperparameter_tuning_randomsearch_no_removal.py combined_train_small_parsed_bitfields_except_opt_otherTTLs.csv


end_time=$(date +%s)

runtime=$((end_time - start_time))

runtime_formatted=$(printf '%02dh:%02dm:%02ds\n' $((runtime/3600)) $((runtime%3600/60)) $((runtime%60)))
echo "Script runtime: $runtime_formatted"
