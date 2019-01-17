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

class percentQualityFails(object):

	def __init__(self, passes_all_filepath, passes_all_filename, 
		fails_all_filepath, fails_all_filename):
		"""The class instantiates with a filepath and name to a file that 
		passes every edit, and a filepath and name to a file that fails 
		a quality edit or multiple quality edits for every row."""
		
		#Loading TS and LAR data for the clean file. 
		self.ts_data, self.passes_all_lar = utils.read_data_file(path=passes_all_filepath, 
                                                 data_file=passes_all_filename)

		#Loading TS and LAR data for the file that fails quality edits for every row. 
		self.ts_data, self.fails_all_lar = utils.read_data_file(path=fails_all_filepath,
												 data_file=fails_all_filename)

		#Storing the first LAR row of the clean file. 
		self.passes_all_lar = self.passes_all_lar.iloc[0:1]
		print(self.passes_all_lar)

		self.lei = self.ts_data.iloc[0][14]


		#Storing the first LAR row of the file that fails quality edits for every row. 	
		self.fails_all_lar = self.fails_all_lar.iloc[0:1]
		print(self.fails_all_lar)

		#Prints a statement indicating that the object has been instantiated. 
		print("Instantiated")

	def create_quality_fails_by_row(self, rows_failed=50, rows_total=100, 
		output_filepath="../edits_files/percent_quality_fails/"):

		"""Creates a file that fails quality edits at a 
		certain number of rows."""

		#Creates 
		new_passes = pd.concat([self.passes_all_lar]*(rows_total-rows_failed))

		new_fails = pd.concat([self.fails_all_lar]*(rows_failed))

		new_lar = pd.concat([new_passes, new_fails])

		new_lar = unique_uli(new_lar_df = new_lar, lei=self.lei)

		utils.write_file(ts_input=self.ts_data, lar_input=new_lar,
			path=output_filepath, name=str(rows_failed)+"_rows_failed_"+str(rows_total)+"_total_rows.txt")

		statement = (str("{:,}".format(rows_failed)) + 
            " rows failed " + str("{:,}".format(rows_total)) + 
            " rows total stored in " + output_filepath)

		print(statement)
		