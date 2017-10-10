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

	def read_data_frames(self):
		"""Receives two pandas dataframes (one TS and one LAR) and stores them as class objects."""
	def write_file(self, edit_name, path):
		"""Writes a dataframe object to a pipe delimited text file in the specified location."""
		#
	#edits will be broken out into sub parts as in the rules_engine.py class. This will allow test files to be generated such that they fail conditions inside each edit.
	#When possible each file will only fail the condition listed in the file name. There will be cases when test files fail additional edits, these cases will be documented
	#to the extent possible.