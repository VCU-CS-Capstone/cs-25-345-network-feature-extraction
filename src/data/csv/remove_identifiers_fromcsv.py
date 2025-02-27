import sys
import pandas as pd


if len(sys.argv) != 3:
	print("Usage: python remove_identifiers.py <raw_input.csv> <cleaned_output.csv>")
	sys.exit(1)

input_csv = sys.argv[1]
output_csv = sys.argv[2]

print(f"Loading raw CSV: {input_csv}")
df = pd.read_csv(input_csv)
print(f"Initial shape: {df.shape}")

# Byte ranges for identifier columns
ipv4_source_start, ipv4_source_end = 97, 129
ipv4_destination_start, ipv4_destination_end = 130, 160
ipv4_identification_start, ipv4_identification_end = 33, 48

tcp_source_port_start, tcp_source_port_end = 480, 496
tcp_destination_port_start, tcp_destination_port_end = 496, 512
tcp_sequence_start, tcp_sequence_end = 512, 544
tcp_ack_start, tcp_ack_end = 544, 576

columns_to_remove = [0] + \
					list(range(ipv4_source_start, ipv4_source_end + 1)) + \
					list(range(ipv4_destination_start, ipv4_destination_end + 1)) + \
					list(range(ipv4_identification_start, ipv4_identification_end + 1)) + \
					list(range(tcp_source_port_start, tcp_source_port_end + 1)) + \
					list(range(tcp_destination_port_start, tcp_destination_port_end + 1)) + \
					list(range(tcp_sequence_start, tcp_sequence_end + 1)) + \
					list(range(tcp_ack_start, tcp_ack_end + 1))

# Drop columns by these index ranges, ignoring any out-of-range
df.drop(df.columns[columns_to_remove], axis=1, inplace=True, errors="ignore")

print(f"After removing identifier columns, shape: {df.shape}")

# Save cleaned CSV
df.to_csv(output_csv, index=False)
print(f"Saved cleaned CSV to: {output_csv}")
