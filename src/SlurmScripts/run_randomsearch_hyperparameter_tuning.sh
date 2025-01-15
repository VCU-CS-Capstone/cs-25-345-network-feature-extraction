#!/usr/bin/bash
#SBATCH --job-name=randomsearch_hyperparameter_tuning_osiris
#SBATCH --qos=short
#SBATCH --cpus-per-task=104
#SBATCH --mem=1440G
#SBATCH --time=6-0
#SBATCH --output=randomsearch_hyperparameter_tuning%j.out

start_time=$(date +%s)

cd /home/"$USER"/osirisml/OsirisML/model || exit
python hyperparameter_tuning_randomsearch.py combined_train_small.csv

end_time=$(date +%s)

runtime=$((end_time - start_time))

runtime_formatted=$(printf '%02dh:%02dm:%02ds\n' $((runtime/3600)) $((runtime%3600/60)) $((runtime%60)))
echo "Script runtime: $runtime_formatted"
