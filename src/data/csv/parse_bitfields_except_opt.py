import sys
import pandas as pd

def usage():
	print("Usage: python parse_bitfields_except_opt.py <input.csv> <output.csv>")
	sys.exit(1)

if len(sys.argv) != 3:
	usage()

input_csv = sys.argv[1]
output_csv = sys.argv[2]

# load csv
print(f"Loading CSV: {input_csv}")
df = pd.read_csv(input_csv)
print(f"Loaded shape: {df.shape}")

# remove identifiers
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

df.drop(df.columns[columns_to_remove], axis=1, inplace=True, errors="ignore")
print(f"After dropping direct ID columns shape: {df.shape}")

# define the fields we are going to squish
field_map = [
	# (prefix, bit_count, new_col_name, do_count_bits?)
	("ipv4_ver",   4,   "ip_version",     False),
	("ipv4_hl",    4,   "ip_header_len",  False),
	("ipv4_tos",   8,   "ip_tos",         False),
	("ipv4_tl",    16,  "ip_tot_len",     False),
	("ipv4_ttl",   8,   "ip_ttl",         False),
	("ipv4_proto", 8,   "ip_proto",       False),
	("ipv4_cksum", 16,  "ip_cksum",       False),

	# not including ("ipv4_opt", 320,...) => so these bits remain raw
	("tcp_doff",   4,   "tcp_data_offset",False),
	("tcp_wsize",  16,  "tcp_window",     False),
	("tcp_cksum",  16,  "tcp_cksum",      False),
	("tcp_urp",    16,  "tcp_urg_ptr",    False),
	# not including ("tcp_opt", 320,...) => remain raw
]

# parse_bits_to_int for smaller fields
def parse_bits_to_int(row, prefix, bit_count):
	"""
	convert bits prefix_(0..bit_count-1) to an integer,
	with prefix_0 as the MSB. missing/-1 bits => treat as 0, missing=True.
	"""
	val = 0
	missing = False
	count_bits_set = 0
	found_any = False

	for i in range(bit_count):
		col_name = f"{prefix}_{i}"
		if col_name not in row.index:
			missing = True
			continue

		bit_val = row[col_name]
		found_any = True

		if bit_val == -1:
			missing = True
			bit_val = 0
		elif bit_val not in (0,1):
			missing = True
			bit_val = 0

		if bit_val == 1:
			shift_amount = (bit_count - 1 - i)
			val += (1 << shift_amount)
			count_bits_set += 1

	if not found_any:
		missing = True

	return val, missing, count_bits_set

# build a small DataFrame (df_small) with compressed columns
df_small = pd.DataFrame()

for (prefix, bit_count, new_col_name, do_count) in field_map:
	int_vals = []
	missing_flags = []
	count_bits_list = []

	for idx, row_data in df.iterrows():
		val, miss, cbits = parse_bits_to_int(row_data, prefix, bit_count)
		int_vals.append(val)
		missing_flags.append(1 if miss else 0)
		count_bits_list.append(cbits)

	df_small[new_col_name] = int_vals
	df_small[new_col_name + "_missing"] = missing_flags
	if do_count:
		df_small[new_col_name + "_count_bits"] = count_bits_list

# identify the label and store it separately
label_colname = "label"
if label_colname not in df.columns:
	label_colname = df.columns[-1]

label_series = df[label_colname].copy()

# identify ip/tcp option columns => prefix "ipv4_opt_" or "tcp_opt_"
# we keep them as raw bits in the final CSV
option_cols = [c for c in df.columns
			   if c.startswith("ipv4_opt_") or c.startswith("tcp_opt_")]

# also keep any columns that were NOT parsed or removed,
# excluding the label. e.g., if there's any leftover raw columns for other fields
excluded_set = set(field_map[i][0] for i in range(len(field_map)))
# above is just the prefix, though, not the columns themselves
parsed_prefixes = [f[0] for f in field_map]
parsed_prefix_cols = []
for (pref, bcount, _, _) in field_map:
	for i in range(bcount):
		col_name = f"{pref}_{i}"
		parsed_prefix_cols.append(col_name)

# all columns used in parse_bits_to_int
parsed_cols_set = set(parsed_prefix_cols) | {label_colname}

# leftover columns that we haven't dropped or parsed (excluding the label)
unparsed_cols = [c for c in df.columns
				 if (c not in parsed_cols_set and c != label_colname)]

# but we specifically want option_cols from them
raw_option_cols = [c for c in unparsed_cols
				   if c.startswith("ipv4_opt_") or c.startswith("tcp_opt_")]

# combine df_small + raw_option_cols, then reattach label at end
df_small_no_label = df_small.copy()  # it has compressed columns

# also gather the raw option columns from the original df
df_raw_opts = df[raw_option_cols].copy()

# concatenate compressed columns + raw option bits horizontally
df_merged = pd.concat([df_small_no_label, df_raw_opts], axis=1)

# finally, add label as the last column
df_merged[label_colname] = label_series.values

# save final
print(f"Final df_merged shape: {df_merged.shape}")
df_merged.to_csv(output_csv, index=False)
print(f"Saved CSV to: {output_csv}")
