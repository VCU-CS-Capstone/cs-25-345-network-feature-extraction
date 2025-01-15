#!/usr/bin/bash
#SBATCH --job-name=preprocess_osiris
#SBATCH --qos=short
#SBATCH --cpus-per-task=104
#SBATCH --mem=1440G
#SBATCH --time=1-0
#SBATCH --output=preprocess_%j.out

cd /home/"$USER"/osirisml/OsirisML/preprocessing || exit
chmod +x process_pcap.sh
./process_pcap.sh Monday-WorkingHours.pcap
./process_pcap.sh Tuesday-WorkingHours.pcap
./process_pcap.sh Wednesday-workingHours.pcap
./process_pcap.sh Thursday-WorkingHours.pcap
./process_pcap.sh Friday-WorkingHours.pcap
