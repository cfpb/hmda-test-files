import math
import json
import os
import pandas as pd
import random
import string
import time
import yaml
import utils

from lar_generator import lar_gen #Imports lar_gen class. 

from large_test_files import LargeTestFiles

from large_test_files import unique_uli

class EditFailsByRow(object):

	def __init__(self, passes_all_filepath, passes_all_filename, 
		fails_all_filepath, fails_all_filename):
		"""The class instantiates with a filepath and name to a file that 
		passes every edit, and a filepath and name to a file that fails 
		a an edit or multiple edits for every row."""

		#To create a file that has a certain number of clean rows and failed rows,
		# two sets of TS and LAR data are loaded to create a file that
		# has some rows that fail edits, and some rows that do not. 
		# The constructor provides a way for users to input their files that pass cleanly
		# and files that fail an edit or multiple edits for every row.  
		
		#Loading TS and LAR data for the clean file. 
		self.clean_ts, self.clean_lar = utils.read_data_file(path=passes_all_filepath, 
                                                 data_file=passes_all_filename)

		#Loading TS and LAR data for the file that fails a set of edits for every row. 
		self.fail_ts, self.fail_lar = utils.read_data_file(path=fails_all_filepath,
												 data_file=fails_all_filename)

		#Storing the first LAR row of the clean file. 
		self.clean_lar = self.clean_lar.iloc[0:1]
		#print(self.clean_lar)

		#Storing the LEI in a global variable. 
		self.lei = self.clean_ts.iloc[0][14]

		#Storing the bank name as a global variable. 
		self.bank_name = self.clean_ts.iloc[0][1]

		#Setting LEI's for each by self.lei.
		self.clean_lar["lei"] = self.lei

		self.fail_lar["lei"] = self.lei

		#Storing the first LAR row of the file that fails a set of edits for every row. 	
		self.fail_lar = self.fail_lar.iloc[0:1]
		#print(self.fail_lar)

		#Prints a statement indicating that the object has been instantiated. 
		print("Instantiated EditFailsbyRow Class")

	def create_edit_fails_by_row_file(self, rows_failed=50, rows_total=100, 
		output_filepath= "../edits_files/edit_fails_by_row/"):
		"""Creates a file that fails a set of edits by a 
		certain number of rows."""

		#Naming an output filepath. 
		output_filepath = output_filepath + str(self.bank_name) + "/"

		#Creates LAR rows that pass every edit.  
		new_rows_passes = pd.concat([self.clean_lar]*(rows_total-rows_failed))

		#Creates a specified number of LAR rows that fail a set of edits.
		new_rows_fails = pd.concat([self.fail_lar]*(rows_failed))

		#Concatenates the LAR rows above to form the specified number of rows in total. 
		new_lar = pd.concat([new_rows_passes, new_rows_fails])

		#Creates a new set of unique ulis to avoid creating duplicate rows.  
		new_lar = unique_uli(new_lar_df = new_lar, lei=self.lei)

		#Replaces the TS number of rows with the rows in total.
		self.clean_ts['lar_entries'] = str(rows_total)

		#Writes the file to the output filepath specified in the class instantiation. 
		utils.write_file(ts_input=self.clean_ts, lar_input=new_lar,
			path=output_filepath+self.bank_name+"/", name=str(rows_failed)+"_rows_failed_"+str(rows_total)+"_total_rows.txt")

		#Prints a statement indicating that the file has been creating in the specified
		#filepath. 
		statement = (str("{:,}".format(rows_failed)) + 
            " rows failed " + str("{:,}".format(rows_total)) + 
            " rows total stored in " + output_filepath)

		print(statement)
		