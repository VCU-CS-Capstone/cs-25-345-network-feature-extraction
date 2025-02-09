import sys

import pandas as pd

usage_message = "Usage: python split_csv_by_TTL.py <filename.csv>"

if len(sys.argv) != 2:
	print(usage_message)
	sys.exit(1)

csv_file = sys.argv[1]
print(f"Loading CSV File: {csv_file}")

try:
	df = pd.read_csv(f"{csv_file}")
	print(f"CSV file loaded")
except FileNotFoundError:
	print(usage_message)
	print(f"ERROR: File '{csv_file}' not found")
	sys.exit(1)
except Exception as e:
	print(usage_message)
	print(f"ERROR: {e}")
	sys.exit(1)

df_64 = df[df["ip_ttl"] == 64].copy()
df_64.to_csv("combined_train_small_parsed_bitfields_except_opt_ttl64.csv", index=False)

df_128 = df[df["ip_ttl"] == 128].copy()
df_128.to_csv("combined_train_small_parsed_bitfields_except_opt_ttl128.csv", index=False)

# leftovers
df_other = df[~df["ip_ttl"].isin([64, 128])].copy()
df_other.to_csv("combined_train_small_parsed_bitfields_except_opt_otherTTLs.csv", index=False)

print("Rows with TTL=64:", len(df_64))
print("Rows with TTL=128:", len(df_128))
print("Rows with other TTL:", len(df_other))
