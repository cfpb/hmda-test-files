#The following functions help to produce data generation for the script below. 

#Imports the required packages
import json
import pandas as pd
import yaml
import logging
import numpy as np

#Imports custom packages. 
import lar_constraints
import lar_generator
from rules_engine import rules_engine
from test_file_generator import test_data
import glob
import utils

class generate_file(object):

	def __init__(self):

		#Loads the filepath configuration. 
		with open('configurations/test_filepaths.yaml') as f:
			#Uses safe_load instead of load.
			self.filepaths = yaml.safe_load(f)

		#Loads the geographic file configuration.
		with open('configurations/geographic_data.yaml') as f:
			# Uses safe_load instead of load.
			self.geographic = yaml.safe_load(f) 

		#Loads the clean file configuration. 
		with open('configurations/clean_file_config.yaml') as f:
			# Uses safe_load instead of load.
			self.data_map = yaml.safe_load(f)

		#Stores the column names for the CBSA file. 
		cbsa_cols = self.geographic['cbsa_columns']

		#Stores the column names used from the CBSA file. 
		use_cols = self.geographic['cbsa_columns_used']

		#Sets the logging parameters.
		#Uses a log file name and file writing mode from the
		#test_filepaths yaml.  
		logging.basicConfig(filename=self.filepaths['log_filename'],
					format='%(asctime)s %(message)s',
                	datefmt='%m/%d/%Y %I:%M:%S %p',
                	filemode=self.filepaths['log_mode'],
                	level=logging.INFO)

		#Loads tract to CBSA data from filepaths named in the test_filepaths
		#yaml file. 
		self.cbsas = pd.read_csv(self.geographic['tract_to_cbsa_file'], 
			usecols=use_cols, 
			delimiter='|', header=None, names=cbsa_cols, dtype=str)

		#Creates county, tract, and small county data from the CBSA file. 
		self.cbsas["tractFips"] = self.cbsas.countyFips + self.cbsas.tracts
		self.counties = list(self.cbsas.countyFips)
		self.tracts = list(self.cbsas.tractFips)
		self.small_counties = list(self.cbsas.countyFips[self.cbsas.smallCounty=="1"])

		#Loads schemas for LAR and TS.
		#Schemas contain valid enumerations, including NA values, for each 
		#field in the dataset. 
		self.lar_schema_df = pd.DataFrame(json.load(open(
			self.filepaths['lar_schema_json'], "r")))
		self.ts_schema_df = pd.DataFrame(json.load(open(
			self.filepaths['ts_schema_json'], "r")))

		#Instantiates the other classes. 
		
		#lar_gen is responsible for generating data according to the values
		# in the schema.
		self.lar_gen = lar_generator.lar_gen(self.lar_schema_df, 
			self.ts_schema_df, counties=self.counties, tracts=self.tracts)

		#lar_constrains is responsible for modifying generated data so that 
		#the resulting file passes syntax and validity edits.
		self.lar_const = lar_constraints.lar_constraints(counties=self.counties, 
			tracts=self.tracts) 

		#lar_validator checks a dataframe and returns a JSON with 
		#edit pass/fail results. 
		self.lar_validator = rules_engine(lar_schema=self.lar_schema_df, 
			ts_schema=self.ts_schema_df, cbsa_data=self.cbsas)
					#tracts=tracts, counties=counties, small_counties=small_counties) 

		#Stores the number of rows in the test file
		self.file_length = self.data_map["file_length"]["value"] 

		#Stores the LEI for the test file. 
		self.lei = self.data_map["lei"]["value"]

	def get_const_list(self):
		
		"""Creates a list of constraints from the functions in 
		the lar_constraints object that apply syntax and validity edits."""
		
		#Creates an empty list to store constraint function names.
		constraints = [] 

		#Takes each function pertaining to a syntax or validity edit
		#in the lar_constraints class, and adds it to the empty constraints.  
		for func in dir(self.lar_const):
			if func[:1] in ("s", "v") and func[1:4].isdigit()==True:
				constraints.append(func)

		#Returns the list of constraints as strings. 
		return constraints

	def apply_constraint(self, row, func):
		"""Applies a constraint (func) to a generated row
		of LAR data and returns a new row in a dictionary format."""
		
		#Copies the row. 
		row_start = row.copy()
		
		#Uses getattr to apply the constraint in the lar_constraints class. 
		row = getattr(self.lar_const, func)(row)
		
		#Logs the changes in the intial row after the constraints
		#have been applied. 
		diff_1, diff_2 = self.get_diff(row, row_start)
		if len(diff_1) > 0:
			logging.info(str(func))
			logging.info(diff_1)
			logging.info(diff_2)
		return row

	def get_diff(self, row, row_base):
		"""Checks the difference between an initial row and the 
		row after constraints are applied"""
		
		#Convert initial row to set. 
		initial_row = set(row_base.items()) 

		#Convert constrained row to set. 
		changed_row = set(row.items()) 

		#Subtract row sets to show changes from constraint functions. 
		diff_1 = (changed_row - initial_row) 
		diff_2 = (initial_row - changed_row)
		return diff_1, diff_2

	def constraints_loop(self, constraints=[], row=None, row_base=None):
		"""Applies the list of constraints 
		generated to each row"""

		for const in constraints:
			row = self.apply_constraint(row, const)
			diff = self.get_diff(row, row_base)
		return row

	def validation(self, row, ts_row):
		"""
		Applies the syntax and validity rules engine logic 
		to the LAR row to create an edit report.
		"""

		#Creates dataframes of LAR and TS data. 
		lar_data = pd.DataFrame(row, index=[1])
		ts_data = pd.DataFrame(ts_row, index=[0])

		#Instantiates a rules checker to check the row against
		#edits in the rules engine. 
		rules_check = rules_engine(lar_schema=self.lar_schema_df, 
			ts_schema=self.ts_schema_df, cbsa_data=self.cbsas)
			#tracts=tracts, counties=counties) #instantiate edits rules engine

		#Loads LAR and TS data to the rules engine. 
		rules_check.load_lar_data(lar_data)
		rules_check.load_ts_data(ts_data)

		#Runs the edits against the LAR row and produces edit check results. 
		for func in dir(rules_check):
			if func[:1] in ("s", "v") and func[1:4].isdigit()==True:
				#print("applying:", func)
				getattr(rules_check, func)()
		
		#Returns edit check results. 
		return rules_check.results

	def make_ts_row(self):
		"""
		Uses the lar_gen object to create a TS row, 
		dictionary object.
		"""
		
		self.ts_row = self.lar_gen.make_ts_row(self.data_map)

		return self.ts_row

	def make_clean_lar_row(self, ts_row):
		"""Uses the lar_gen object and a TS row to create a LAR row that 
		passes syntax and validity edits according to the FIG."""

		#Stores the stop condition and the initial number of iterations. 
		stop = False
		iters = 1

		#Makes a new row using the lar generator. 
		row = self.lar_gen.make_row(lei=self.lei)
		
		#Begins a loop that creates the LAR row. The loop generates the row 
		#with the lar_generator and then validates the row
		#against the rules engine for syntax or validity edits. 

		#If syntax or validity edits are present, the row is run through 
		#the contraints and validated again. 

		while stop == False:

			#Copies row to enable diff logging.
			row_base = row.copy() 
			
			#Creates an edit report based on the validation.
			res = pd.DataFrame(self.validation(row, ts_row))
			
			#Logs the results of edits that have failed. 
			logging.info(res[res.status=="failed"]) 
			
			#If there are no syntax or validity edits present, the stop
			#condition is invoked and the row is returned. 
			if len(res[res.status=="failed"])<=0:
				stop = True 
			
			#If there are syntax or validity edits present, the constraints
			#are applied and revalidated while stop is False. 
			else:
				message = "\nstarting constraints iteration {iter}".format(
					iter=iters)
				logging.info(message)
				row = self.constraints_loop(self.get_const_list(), row, 
					row_base) 
			
			iters+=1

		return row
		

	def create_files(self, kind):
		"""Creates a clean file or a set of edit files specified by the
		function call"""

		#Creates TS row data. 
		self.ts_row = self.make_ts_row()

		#Creates a TS row dataframe. 
		ts_df = pd.DataFrame(self.ts_row, index=[1])

		#The following produces a clean file. 
		if kind == 'clean_file':

			#Creates a first row of LAR to begin the dataframe.
			#All other rows are concatenated to the dataframe until
			#it the frame reaches the file length specified in the 
			#test filepaths yaml file. 
			for i in range(0, self.file_length):
				print('Creating row {i}'.format(i=i))
				if i==0:
					first_row = self.make_clean_lar_row(ts_row=self.ts_row)
					lar_frame = pd.DataFrame(first_row, index=[1])
				else:
					new_row = self.make_clean_lar_row(ts_row=self.ts_row)
					new_row = pd.DataFrame(new_row, index=[1])
					lar_frame = pd.concat([lar_frame, new_row], axis=0)
			
			#Writes the file to a clean filepath specified in the test_filepaths
			#configuration.  
			utils.write_file(ts_input=ts_df, lar_input=lar_frame, 
				path=self.filepaths['clean_filepath'].format(
					bank_name=self.data_map["name"]["value"]),
				name=self.filepaths['clean_filename'].format(
					n=self.file_length, bank_name=self.data_map["name"]["value"]))

		#For error files. 
		if kind == 'error_files':

			#Modifies clean data and outputs 
			#resulting files that fail specific edits.
			
			#Instantiates the edit file maker.
			file_maker = test_data(ts_schema=self.ts_schema_df, 
				lar_schema=self.lar_schema_df) 

			#Pulls in the clean data filepath and name from the
			#test filepaths yaml file. 
			ts_data, lar_data = utils.read_data_file(
				path=self.filepaths['clean_filepath'].format(
					bank_name=self.data_map["name"]["value"]),
				data_file=self.filepaths["clean_filename"].format(
					bank_name=self.data_map["name"]["value"], 
					n=self.data_map["file_length"]["value"])) 
					

			#Passes clean file data to the file maker object.
			file_maker.load_data_frames(ts_data, lar_data) 

			#Generates a file for each edit function in file maker. 
			edits = []
			
			#Loops over all data modification functions. 
			for func in dir(file_maker): 

				#Checks if function is a numbered syntax or validity edit.
				if func[:1] in ("s", "v", "q") and func[1:4].isdigit()==True: 
					print("applying:", func)
					#Applies data modification functions and produces files.
					getattr(file_maker, func)() 
					

	def edit_report(self, data_filepath, data_filename):
		"""
		This function takes in a filepath and name, producing a report on
		whether any rows of the data failed syntax, validity or quality edits.

		The report contains among its fields the edit name, the status of the 
		edit, the number of rows failed by the edit, if any, and the ULI's or 
		NULIs (loan ID) of the rows that fail the edit. 

		The resulting report is saved as a csv file using configurations
		from the test_filepaths.yaml file. 
		"""

		#Instantiates the rules engine class as a checker object with a
		#LAR schema, a TS schema, and CBSA data. 
		checker = rules_engine(lar_schema=self.lar_schema_df, 
			ts_schema=self.ts_schema_df, cbsa_data=self.cbsas)

		#Seperates data from the filepath and filename into a TS dataframe
		#and a LAR dataframe. 
		ts_df, lar_df = utils.read_data_file(path=data_filepath, 
			data_file=data_filename)

		#Loads the TS and LAR dataframes into the checker object. 
		checker.load_data_frames(ts_df, lar_df)

		#Applies each function in the rules engine that checks for edits
		#and creates a results list of edits failed or passed. 
		for func in dir(checker):
			if func[:1] in ("s", "v", "q") and func[1:4].isdigit()==True:
				getattr(checker, func)()

		#Creates a dataframe of results from the checker. 
		res_df = pd.DataFrame(checker.results)

		#Filters the results for edits that have failed. 
		res_df = res_df[(res_df['status']=='failed')]

		#Writes the report to the filepath and name designated in 
		#the test_fielpaths yaml
		res_df.to_csv(self.filepaths['edit_report_filepath']+self.filepaths['edit_report_filename'])

		#Logs the result.
		logging.info("Edit Report has been created in {filepath}".format(
			filepath=self.filepaths['edit_report_filepath']))
















		