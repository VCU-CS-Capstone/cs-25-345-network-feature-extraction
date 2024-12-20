#!/usr/bin/bash
#SBATCH --job-name=xgboost_train_friday
#SBATCH --qos=short
#SBATCH --cpus-per-task=32
#SBATCH --mem=512G
#SBATCH --time=1-0
#SBATCH --output=xgboost_train_friday_%j.out

# like configure script, this script also assumes you have the same directory structure

if [ -f /home/"$USER"/osirisml/OsirisML/data/csv/Friday-WorkingHours.csv ]; then
    echo "CSV file exists and is readable."
else
    echo "CSV file not found."
    exit 1
fi


cd /home/"$USER"/osirisml/OsirisML/model || exit

# run the model script, default test split is 0.2
python3 xgboostmodel.py Friday-WorkingHours.csv chrismodel.json
