#!/usr/bin/bash
#SBATCH --job-name=preprocess_osiris
#SBATCH --qos=short
#SBATCH --cpus-per-task=16
#SBATCH --mem=256G
#SBATCH --time=1-0
#SBATCH --output=preprocess_%j.out

cd /home/"$USER"/osirisml/OsirisML/preprocessing || exit
chmod +x process_pcap.sh
./process_pcap.sh Friday-WorkingHours.pcap
