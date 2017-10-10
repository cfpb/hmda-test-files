import os
import pandas as pd

import utils

class test_data(object):
	"""This class alters clean synthetic data files in order to cause the altered file to fail the specified edit. Modified files may fail other edits as well."""

	def __init__(self, ts_schema, lar_schema):
		"""Set initial class variables"""
		self.clean_file_path = ""
		self.validity_dir = ""
		self.syntax_dir = ""
		self.lar_field_names = list(lar_schema.field)
		self.ts_field_names = list(ts_schema.field)

	def load_data_frames(self, ts_data, lar_data):
		"""Receives dataframes for TS and LAR and writes them as object attributes"""
		self.ts_df = ts_data
		self.lar_df = lar_data

	def load_lar_data(self, lar_df=None):
		"""Takes a dataframe of LAR data and stores it as a class variable."""
		self.lar_df = lar_df

	def load_ts_data(self, ts_df=None):
		"""Takes a dataframe of TS data and stores it as a class variable. TS data must be a single row."""
		self.ts_df = ts_df
	#edits will be broken out into sub parts as in the rules_engine.py class. This will allow test files to be generated such that they fail conditions inside each edit.
	#When possible each file will only fail the condition listed in the file name. There will be cases when test files fail additional edits, these cases will be documented
	#to the extent possible.
	def s300_1_file(self):
		"""Sets the first character of the first row of the file to 3."""
		s300_1_ts = self.ts_df.copy() #change to local data from class data object
		#modify local data
		s300_1_ts.record_id = "3"
		#write local data to file
		utils.write_file(edit_name="s300_1.txt", path="../edits_files/syntax/", ts_input=s300_1_ts, lar_input=self.lar_df)

	def s300_2_file(self):
		""""Sets the first character of each LAR row to 3."""
		s300_lar = self.lar_df.copy() #set to local data from class data object
		s300_lar.record_id = "3"
		utils.write_file(edit_name="s300_2.txt", path="../edits_files/syntax/", ts_input=self.ts_df, lar_input=s300_lar)