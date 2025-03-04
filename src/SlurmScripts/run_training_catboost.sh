#!/usr/bin/bash
#SBATCH --job-name=catboost_train_friday
#SBATCH --qos=short
#SBATCH --cpus-per-task=32
#SBATCH --mem=1024G
#SBATCH --time=1-0
#SBATCH --output=catboost_train_friday_%j.out

# like configure script, this script also assumes you have the same directory structure
#make sure this path is right mine is a little different
if [ -f /home/"$USER"/osirisml/OsirisML/data/csv/combined_train_monday_cleaned.csv ]; then
    echo "CSV file exists and is readable."
else
    echo "CSV file not found."
    exit 1
fi


cd /home/"$USER"/osirisml/OsirisML/model || exit

# run the model script, default test split is 0.2
python3 catboostmodel.py combined_train_monday_cleaned.csv ryanmodel5.json
