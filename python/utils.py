#This file contains helper functions used by one or more classes in order to generate clean and failing synthetic data files.
import json
import os
import pandas as pd

def write_file(edit_name=None, path=None, ts_input=None, lar_input=None):
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
	with open(path + edit_name, 'w') as final_file:
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