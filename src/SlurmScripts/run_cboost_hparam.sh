#!/usr/bin/bash
#SBATCH --job-name=boost_hparam
#SBATCH --qos=short
#SBATCH --cpus-per-task=104
#SBATCH --mem=1440G
#SBATCH --time=6-0
#SBATCH --output=hyperparameter_cboost_tuning%j.out

start_time=$(date +%s)

cd /home/"$USER"/osirisml/OsirisML/model || exit
python catboost_hparam.py train_d3.csv

end_time=$(date +%s)

runtime=$((end_time - start_time))

runtime_formatted=$(printf '%02dh:%02dm:%02ds\n' $((runtime/3600)) $((runtime%3600/60)) $((runtime%60)))
echo "Script runtime: $runtime_formatted"
