#!/usr/bin/bash
#SBATCH --job-name=xgboost_featureselection
#SBATCH --qos=short
#SBATCH --cpus-per-task=104
#SBATCH --mem=1440G
#SBATCH --time=14-0
#SBATCH --output=feature_selection%j.out

start_time=$(date +%s)

# this python file actually needs to be refactored to take combined_test and combined_train
# ... but ill do that later
cd /home/"$USER"/osirisml/OsirisML/model || exit
python xgboostmodel_featureselection.py combined_train.csv chris_model_jan26

end_time=$(date +%s)

runtime=$((end_time - start_time))

runtime_formatted=$(printf '%02dh:%02dm:%02ds\n' $((runtime/3600)) $((runtime%3600/60)) $((runtime%60)))
echo "Script runtime: $runtime_formatted"
