import sys
import pandas as pd

def usage():
	print("Usage: python parse_bitfields_with_chunking.py <input.csv> <output.csv>")
	sys.exit(1)

if len(sys.argv) != 3:
	usage()

input_csv = sys.argv[1]
output_csv = sys.argv[2]

#l oad CSV
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
	("ipv4_ver",  4,   "ip_version",     False),
	("ipv4_hl",   4,   "ip_header_len",  False),
	("ipv4_tos",  8,   "ip_tos",         False),
	("ipv4_tl",   16,  "ip_tot_len",     False),
	("ipv4_ttl",  8,   "ip_ttl",         False),
	("ipv4_proto",8,   "ip_proto",       False),
	("ipv4_cksum",16,  "ip_cksum",       False),

	# big 320-bit field => chunk it
	("ipv4_opt", 320,  "ip_options",     True),

	("tcp_doff", 4,    "tcp_data_offset",False),
	("tcp_wsize",16,   "tcp_window",     False),
	("tcp_cksum",16,   "tcp_cksum",      False),
	("tcp_urp",  16,   "tcp_urg_ptr",    False),

	# another 320-bit field => chunk it
	("tcp_opt",  320,  "tcp_options",    True),
]

def parse_bits_to_int(row, prefix, bit_count):
	"""
	convert bits prefix_(0..bit_count-1) to an integer,
	with prefix_0 as the MSB. missing/-1 bits => treat as 0, missing=True.
	also, count how many bits are set for opt fields
	"""
	val = 0
	missing = False
	count_bits_set = 0
	have_any_bit = False

	for i in range(bit_count):
		col_name = f"{prefix}_{i}"
		if col_name not in row.index:
			missing = True
			continue

		bit = row[col_name]
		have_any_bit = True

		if bit == -1:
			missing = True
			bit = 0
		elif bit not in (0,1):
			missing = True
			bit = 0

		if bit == 1:
			shift_amount = (bit_count - 1 - i)
			val += (1 << shift_amount)
			count_bits_set += 1

	if not have_any_bit:
		missing = True

	return val, missing, count_bits_set

def parse_bits_to_chunks(row, prefix, total_bits=320, chunk_size=64):
	"""
	splits prefix_(0..total_bits-1) into multiple integers,
	each chunk_size bits. 320 -> 5 chunks of 64 bits.
	Mark missing if any bits not found or -1.
	also, count total bits set across all chunks.
	"""
	num_chunks = total_bits // chunk_size
	chunk_values = [0]*num_chunks
	missing = False
	bit_count = 0
	have_any_bit = False

	for bit_idx in range(total_bits):
		col_name = f"{prefix}_{bit_idx}"
		if col_name not in row.index:
			missing = True
			continue

		bit_val = row[col_name]
		have_any_bit = True

		if bit_val == -1:
			missing = True
			bit_val = 0
		elif bit_val not in (0,1):
			missing = True
			bit_val = 0

		chunk_idx = bit_idx // chunk_size
		local_offset = bit_idx % chunk_size
		# interpret prefix_0 as MSB => invert offset
		shift_amount = (chunk_size - 1 - local_offset)

		if bit_val == 1:
			chunk_values[chunk_idx] |= (1 << shift_amount)
			bit_count += 1

	if not have_any_bit:
		missing = True

	return chunk_values, missing, bit_count

df_parsed = pd.DataFrame()

for (prefix, bit_count, new_col_name, do_count) in field_map:
	if prefix in ["ipv4_opt", "tcp_opt"]:
		chunk_size = 64
		num_chunks = bit_count // chunk_size  # 320->5

		# prepare columns in df_parsed with dtype=object to store large ints
		chunk_cols = [f"{new_col_name}_chunk{i}" for i in range(num_chunks)]
		for ccol in chunk_cols:
			df_parsed[ccol] = pd.Series([0]*len(df), dtype="object")

		df_parsed[new_col_name + "_missing"] = 0
		if do_count:
			df_parsed[new_col_name + "_count_bits"] = 0

		# fill row by row
		for idx, row_data in df.iterrows():
			chunk_vals, missing, bitcount = parse_bits_to_chunks(
				row_data, prefix, total_bits=bit_count, chunk_size=chunk_size
			)
			for c_i, val_chunk in enumerate(chunk_vals):
				df_parsed.at[idx, chunk_cols[c_i]] = val_chunk

			df_parsed.at[idx, new_col_name + "_missing"] = 1 if missing else 0
			if do_count:
				df_parsed.at[idx, new_col_name + "_count_bits"] = bitcount

	else:
		# smaller fields => parse into single int
		int_values = []
		missing_flags = []
		count_bits_vals = []

		for idx, row_data in df.iterrows():
			val, missing, cbits = parse_bits_to_int(row_data, prefix, bit_count)
			int_values.append(val)
			missing_flags.append(1 if missing else 0)
			count_bits_vals.append(cbits)

		df_parsed[new_col_name] = int_values
		df_parsed[new_col_name + "_missing"] = missing_flags
		if do_count:
			df_parsed[new_col_name + "_count_bits"] = count_bits_vals

label_colname = "label"
if label_colname not in df.columns:
	label_colname = df.columns[-1]

df_parsed[label_colname] = df[label_colname].values

# save
print(f"Final df_parsed shape: {df_parsed.shape}")
df_parsed.to_csv(output_csv, index=False)
print(f"Saved parsed CSV to: {output_csv}")
