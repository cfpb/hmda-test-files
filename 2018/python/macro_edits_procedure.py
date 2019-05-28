#The following code imports the required packages.
import math
import json
import os
import pandas as pd
import random
import string
import time
import yaml
import shutil as sh
import utils

from large_test_files import LargeTestFiles


class MacroEdits(object):

	"""Using a clean source file, this class creates test files that fail
	Macro Quality Edits while passing edits for syntax and validity."""

	def __init__(self, source_filepath, source_filename):
		
		#Using the read_data_file method to initialize TS and LAR data. 
		self.ts_data, self.lar_data = utils.read_data_file(
			path = source_filepath, 
            data_file = source_filename)
		
		#Storing the path to the file parts directory to store 
		#lar rows that fail a Macro Quality Edit. 
		self.file_parts_path = "../edits_files/fileparts/"

		#Storing the path to the quality edits directory to store the 
		#resulting file. 
		self.quality_edits_path = "../edits_files/quality/"
		
		#Storing the bank name from the Transmittal Sheet to 
		#be used in the file names. 
		self.bank_name = self.ts_data.iloc[0][1]

	def create_macro_files(self, row_count):
		
		"""Creates a set of Macro Quality Edits files that are 
		stored in the quality edits directory."""
		
		self.q634_edit(row_count=row_count)
		self.q635_edit(row_count=row_count)
		self.q636_edit(row_count=row_count)
		self.q637_edit(row_count=row_count)
		self.q638_edit(row_count=row_count)
		self.q639_edit(row_count=row_count)
		self.q640_edit(row_count=row_count)

	def file_writer(self, row_count = 2000, edits_rows = None, edit_name=None):

		"""A helper function that creates a file from a dataframe of LAR rows 
		that incorporates a Macro Quality Edit fail. """

		#Writes a file with the Macro Quality Edit fail to the file parts 
		#directory as a source file for the LargeTestFiles class. 
		utils.write_file(path=self.file_parts_path, ts_input=self.ts_data, 
			lar_input=edits_rows, name=edit_name + "_sample_rows.txt")

		#Instantiates the LargeTestFiles class with the source file.
		
		large_file = LargeTestFiles(
			source_filename=self.file_parts_path + edit_name + "_sample_rows.txt", 
			output_filename=self.quality_edits_path + edit_name + "_macro_edits_file_" 
			+ str(row_count) + "_" + self.bank_name+ ".txt")

		#Creates a larger file using the LargeTestFiles object and saves 
		#a file to the quality edits directory with a specified number of rows.
		large_file.create_file(row_count=row_count)

	def q634_edit(self, row_count=2000):
		
		"""Produces a file with a specified row count that fails 
		Macro Quality Edit, Q634. Requires a minimum file size of 
		5 LAR rows."""

		edit_name = "q634" 
		
		q634_rows = self.lar_data[(self.lar_data['loan_purpose'] == '1') & 
		(self.lar_data['action_taken'] == '1')][0:5]

		self.file_writer(row_count=row_count, edits_rows = q634_rows,
			edit_name=edit_name)
		

	def q635_edit(self, row_count=2000):
		
		"""Produces a file with a specified row count that fails 
		Macro Quality Edit, Q635. Requires a minimum file size of 
		5 LAR rows.""" 

		edit_name = "q635"
		
		q635_rows = self.lar_data[(self.lar_data['action_taken'] == '2')][0:5]

		self.file_writer(row_count=row_count, edits_rows = q635_rows,
			edit_name=edit_name)
		

	def q636_edit(self, row_count=2000):
		
		"""Produces a file with a specified row count that fails 
		Macro Quality Edit, Q636. Requires a minimum file size of 
		5 LAR rows.""" 

		edit_name = "q636"
		
		q636_rows = self.lar_data[(self.lar_data['action_taken'] == '4')][0:5]
		
		self.file_writer(row_count=row_count, edits_rows = q636_rows,
			edit_name=edit_name)
	
	def q637_edit(self, row_count=2000):
		
		"""Produces a file with a specified row count that fails 
		Macro Quality Edit, Q637. Requires a minimum file size of 
		5 LAR rows.""" 

		edit_name = "q637"
		
		q637_rows = self.lar_data[
		(self.lar_data['action_taken'] == '5')][0:5]

		self.file_writer(row_count=row_count, edits_rows = q637_rows,
			edit_name=edit_name)
		
	
	def q638_edit(self, row_count=2000):
		
		"""Produces a file with a specified row count that fails 
		Macro Quality Edit, Q638. Requires a minimum file size of 
		5 LAR rows.""" 

		edit_name = "q638"
		
		q638_rows = self.lar_data[
		(self.lar_data['action_taken'] == '2')].iloc[0:5]

		self.file_writer(row_count=row_count, edits_rows = q638_rows,
			edit_name=edit_name)
		
	
	def q639_edit(self, row_count=2000):
		
		"""Produces a file with a specified row count that fails 
		Macro Quality Edit, Q639. Requires a minimum file size of 
		1 LAR row."""

		edit_name = "q639" 
		
		q639_rows = self.lar_data[
		(self.lar_data["loan_purpose"] == '1') &
		(self.lar_data["action_taken"] == '1') & 
		(self.lar_data["reverse_mortgage"] == '1111')]

		q639_rows = q639_rows[0:1]

		q639_rows["preapproval"] = '1'

		q639_rows["open_end_credit"] = '1111'

		q639_rows["affordable_units"] = "Exempt"

		self.file_writer(row_count=row_count, edits_rows = q639_rows,
			edit_name=edit_name)
		
	
	def q640_edit(self, row_count=2000):
		
		"""Produces a file with a specified row count that fails 
		Macro Quality Edit, Q640. Requires a minimum file size of 
		5 LAR rows.""" 

		edit_name = "q640"

		q640_rows = self.lar_data[(self.lar_data['income'] < '10')][0:5]

		self.file_writer(row_count=row_count, edits_rows = q640_rows,
			edit_name=edit_name)
		

