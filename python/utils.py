#This file contains helper functions used by one or more classes in order to generate clean and failing synthetic data files.
import json
import os
import pandas as pd


state_codes = {'WA':'53', 'WI':'55', 'WV':'54', 'FL':'12', 'WY':'56', 'NH':'33', 'NJ':'34', 'NM':'33', 'NC':'37', 'ND':'38', 'NE':'31', 'NY':'36', 'RI':'44', 'NV':'32', 'CO':'08', 'CA':'06', 'GA':'13', 'CT':'09', 'OK':'40', 'OH':'39',
					'KS':'20', 'SC':'45', 'KY':'21', 'OR':'41', 'SD':'46', 'DE':'10', 'HI':'15', 'PR':'43', 'TX':'48', 'LA':'22', 'TN':'47', 'PA':'42', 'VA':'51', 'VI':'78', 'AK':'02', 'AL':'01', 'AR':'05', 'VT':'50', 'IL':'17', 'IN':'18',
					'IA':'19', 'AZ':'04', 'ID':'16', 'ME':'23', 'MD':'24', 'MA':'25', 'UT':'49', 'MO':'29', 'MN':'27', 'MI':'26', 'MT':'30', 'MS':'29', 'DC':'11'}

def write_file(path=None, ts_input=None, lar_input=None, name="test_file.txt"):
	"""Takes a TS row and LAR data as dataframes. Writes LAR data to file and
	re-reads it to combine with TS data to make a full file."""
	#make directories for files if they do not exist
	if not os.path.exists(path):
		os.makedirs(path)
	#check existence of file parts directory
	parts_dir = path+"file_parts/"
	if not os.path.exists(parts_dir):
		os.makedirs(parts_dir)
	#write TS dataframe to file
	ts_input.to_csv(parts_dir + "ts_data.txt", sep="|", header=False, index=False, index_label=False)
	#write LAR dataframe to file
	lar_input.to_csv(parts_dir + "lar_data.txt", sep="|", header=False, index=False, index_label=False)
	#load LAR data as file rows
	with open(parts_dir + "lar_data.txt", 'r') as lar_data:
		lar = lar_data.readlines()
	with open(parts_dir + "ts_data.txt", "r") as ts_data:
		ts  = ts_data.readline()
	with open(path + name, 'w') as final_file:
		final_file.write(ts)
		for line in lar:
			final_file.write("{line}".format(line=line))

def read_data_frames(ts_df=None, lar_df=None):
	"""Receives two pandas dataframes (one TS and one LAR) and stores them as class objects."""
	if ts_df is not None:
		self.ts_df = ts_df
	if lar_df is not None:
		self.lar_df = lar_df
	if ts_df is None and lar_df is None:
		raise ValueError("No data passed.\nNo data written to object.")

def read_data_file(path="", data_file=None):
	"""Reads a complete file (includes LAR and TS rows) into a pandas dataframe and returns them."""
	ts_schema = pd.DataFrame(json.load(open("../schemas/ts_schema.json", "r")))
	lar_schema = pd.DataFrame(json.load(open("../schemas/lar_schema.json", "r")))
	if data_file is not None:
		with open(path+data_file, 'r') as infile:
			#split TS row from file
			ts_row = infile.readline().strip("\n")
			ts_data = []
			ts_data.append(ts_row.split("|"))
			#split LAR rows from file
			lar_rows = infile.readlines()
			lar_data = [line.strip("\n").split("|") for line in lar_rows]
			#create dataframes of TS and LAR data
			ts_df = pd.DataFrame(data=ts_data, dtype=object, columns=ts_schema.field)
			lar_df  = pd.DataFrame(data=lar_data, dtype=object, columns=lar_schema.field)
			return (ts_df, lar_df)
	else:
		raise ValueError("A data file mus be passed. No data have been written to the object")