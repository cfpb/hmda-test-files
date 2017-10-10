import os
import pandas as pd


class test_data(object):
	"""This class alters clean synthetic data files in order to cause the altered file to fail the specified edit. Modified files may fail other edits as well."""

	def __init__(self, ts_schema, lar_schema):
		"""Set initial class variables"""
		self.clean_file_path = ""
		self.validity_dir = ""
		self.syntax_dir = ""
		self.lar_field_names = list(lar_schema.field)
		self.ts_field_names = list(ts_schema.field)

	def read_data_file(self, path, data_file):
		"""Reads a complete file (includes LAR and TS rows) into a pandas dataframe and stores it as a class object."""
		with open(path+data_file, 'r') as infile:
			#split TS row from file
			ts_row = infile.readline().strip("\n")
			ts_data = []
			ts_data.append(ts_row.split("|"))
			#split LAR rows from file
			lar_rows = infile.readlines()
			lar_data = [line.strip("\n").split("|") for line in lar_rows]
			#create dataframes of TS and LAR data
			self.ts_df = pd.DataFrame(data=ts_data, dtype=object, columns=self.ts_field_names)
			self.lar_df  = pd.DataFrame(data=lar_data, dtype=object, columns=self.lar_field_names)

	def read_data_frames(self, ts_df, lar_df):
		"""Receives two pandas dataframes (one TS and one LAR) and stores them as class objects."""
		self.ts_df = ts_df
		self.lar_df = lar_df

	def write_file(self, edit_name, path, ts_input, lar_input):
		"""Takes a TS row as a dictionary and LAR data as a dataframe. Writes LAR data to file and
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
			final_file.write(tste)
			for line in lar:
				final_file.write("{line}".format(line=line))

	#edits will be broken out into sub parts as in the rules_engine.py class. This will allow test files to be generated such that they fail conditions inside each edit.
	#When possible each file will only fail the condition listed in the file name. There will be cases when test files fail additional edits, these cases will be documented
	#to the extent possible.
	def s300_1_file(self):
		"""The first row of the file must begin with a "1"."""
		#change to local data
		s300_1_lar = self.lar_df.copy()
		s300_1_ts = self.ts_df.copy()
		#modify local data
		s300_1_ts.record_id = "3"
		#write local data to file
		self.write_file(edit_name="s300_1.txt", path="../edits_files/syntax/", ts_input=s300_1_ts, lar_input=s300_1_lar)