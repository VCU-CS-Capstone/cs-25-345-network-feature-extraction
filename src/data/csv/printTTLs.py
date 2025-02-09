import sys
import pandas as pd

usage_message = "Usage: python printTTLs.py <filename.csv>"

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


unique_labels = df["label"].unique()
print("Unique OS labels in the dataset:", unique_labels)

# group by os label and look at the distribution of TTL
for os_name, group_df in df.groupby("label"):
	print(f"\n=== OS: {os_name} ===")
	print("Descriptive stats of TTL values:\n", group_df["ip_ttl"].describe())
	print("Value Counts of TTL:\n", group_df["ip_ttl"].value_counts().head(10))
