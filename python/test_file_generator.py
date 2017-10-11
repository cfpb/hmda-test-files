import os
import pandas as pd
import random
import string

import utils

class test_data(object):
	"""This class alters clean synthetic data files in order to cause the altered file to fail the specified edit. Modified files may fail other edits as well."""

	def __init__(self, ts_schema, lar_schema):
		"""Set initial class variables"""
		self.clean_file_path = "../edits_files/"
		self.validity_path = "../edits_files/validity/"
		self.syntax_path = "../edits_files/syntax/"
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
		name = "s300_1.txt"
		path = self.syntax_path
		ts = self.ts_df.copy() #change to local data from class data object
		lar = self.lar_df.copy()
		ts.record_id = "3" #modify local data to fail edit test
		#write local data to file
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def s300_2_file(self):
		""""Sets the first character of each LAR row to 3."""
		name = "s300_2_file"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy() #set to local data from class data object
		lar.record_id = "3" #modify data to fail edit test
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def s301_file(self):
		"""Changes the LEI of a LAR file such that it does not match the TS."""
		name = "s301.txt"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		while lar.lei[0] == self.ts_df.lei[0]:
			lar.lei = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
		print("writing {name}".format(name=name))
		utils.write_file(name="s301.txt", path="../edits_files/syntax/", ts_input=ts, lar_input=lar)

	def s302_file(self):
		"""Sets the year of submission to 2016"""
		name = "s302.txt"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.calendar_year = "2016"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v600_file(self):
		"""Modifies the LEI of TS and LAR so that they do not meed schema requirements"""
		name = "v600.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.lei = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		lar.lei = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)