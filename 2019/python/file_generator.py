import glob
import json
import logging
import os

import pandas as pd
import numpy as np
import yaml

import lar_constraints
import lar_generator
from rules_engine import rules_engine
from test_file_generator import test_data
import utils

class FileGenerator(object):

	def __init__(self,filename=''):

		#Loads the filepath configuration.
		with open('configurations/test_filepaths.yaml') as f:
			#Uses safe_load instead of load.
			self.filepaths = yaml.safe_load(f)

		#Loads the geographic file configuration.
		with open('configurations/geographic_data.yaml') as f:
			# Uses safe_load instead of load.
			self.geographic = yaml.safe_load(f)

		#Loads the clean file configuration.
		with open(filename) as f:
			# Uses safe_load instead of load.
			self.clean_config = yaml.safe_load(f)

		#Loads the edit report configuration.
		with open('configurations/edit_report_config.yaml') as f:
			# Uses safe_load instead of load.
			self.edit_report_config = yaml.safe_load(f)

		#Stores the column names for the file containing geographic geographic data.
		file_cols = self.geographic['file_columns']

		#Sets the logging parameters.
		#Uses a log file name and file writing mode from the
		#test_filepaths yaml.
		logging.basicConfig(filename=self.filepaths['log_filename'],
					format='%(asctime)s %(message)s',
                	datefmt='%m/%d/%Y %I:%M:%S %p',
                	filemode=self.filepaths['log_mode'],
                	level=logging.INFO)

		#Loads geographic geographic data from filepaths named in the test_filepaths
		#yaml file.
		self.geographic_data = pd.read_csv(self.geographic['geographic_data_file'],
			delimiter='|', header=None, names=file_cols, dtype=str)

		#Creates county, tract, and small county data from the file containing geographic geographic data.
		self.geographic_data['county_fips'] = self.geographic_data['state_code'] + self.geographic_data['county']
		self.geographic_data["tract_fips"] = self.geographic_data.county_fips + self.geographic_data.tracts
		self.counties = list(self.geographic_data.county_fips)
		self.tracts = list(self.geographic_data.tract_fips)
		self.small_counties = list(self.geographic_data.county_fips[self.geographic_data.small_county=="S"])

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
			ts_schema=self.ts_schema_df, geographic_data=self.geographic_data)
					#tracts=tracts, counties=counties, small_counties=small_counties)

		#Stores the number of rows in the test file
		self.file_length = self.clean_config["file_length"]["value"]

		#Stores the LEI for the test file.
		self.lei = self.clean_config["lei"]["value"]


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
			ts_schema=self.ts_schema_df, geographic_data=self.geographic_data)
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

		self.ts_row = self.lar_gen.make_ts_row(self.clean_config)

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
			#the length of the dataframe reaches the file length specified in the
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
					bank_name=self.clean_config["name"]["value"]),
				name=self.filepaths['clean_filename'].format(
					n=self.file_length, bank_name=self.clean_config["name"]["value"]))

		#For error files.
		if kind == 'error_files':

			#Modifies clean data and outputs
			#resulting files that fail specific edits.

			#Instantiates the edit file maker.
			file_maker = test_data(ts_schema=self.ts_schema_df,
								   lar_schema=self.lar_schema_df,
								   geographic_data=self.geographic_data)

			#Pulls in the clean data filepath and name from the
			#test filepaths yaml file.
			ts_data, lar_data = utils.read_data_file(
				path=self.filepaths['clean_filepath'].format(
					bank_name=self.clean_config["name"]["value"]),

				data_file=self.filepaths["clean_filename"].format(
					bank_name=self.clean_config["name"]["value"],
					n=self.clean_config["file_length"]["value"]))


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


	def validate_quality_edit_file(self, quality_filename):
		"""
		The test file generator logic for creating quality edit test files
		may cause rows to fail not only quality edits, but also
		syntax or validity edits in the creation process.

		This function takes a quality edit test file from the quality filepaths
		directory in the test filepaths yaml, drops rows that have
		syntax or validity edits, and duplicates the remaining clean rows to the
		length of the original file.

		The file is then saved in a new directory for quality edit test files
		that also pass syntax and validity edits.

		NOTE: This function works to allow LAR rows to pass syntax and validity edits and
		does not validate the TS sheet.
		"""

		try:
			#Instantiates an edit checker object with rules_engine.
			checker = rules_engine(lar_schema=self.lar_schema_df,
				ts_schema=self.ts_schema_df, geographic_data=self.geographic_data)

			#Reads the files and separates data into TS and LAR frames.
			ts_df, lar_df = utils.read_data_file(
				path=self.filepaths['quality_filepath'].format(bank_name=self.clean_config['name']['value']),
				data_file=quality_filename)

			#Stores the original length of the file.
			original_length = len(lar_df.index)

			#Loads data into the checker object.
			checker.load_data_frames(ts_df, lar_df)

			#Produces a report as to which syntax or validity
			#edits have passed or failed based on logic in the rules_engine.
			for func in dir(checker):
				if func[:1] in ("s", "v") and func[1:4].isdigit()==True:
					getattr(checker, func)()

			#Creates a results dataframe and keeps the results that
			#have failed.
			report_df = pd.DataFrame(checker.results)
			report_df = report_df[(report_df['status']=='failed')]

			# The function ignores TS edits and drops results related
			# to edit fails from the TS.
			report_df = report_df[report_df['row_ids'] != 'TS']

			if len(report_df) == 0:
				#If there are no syntax or validity edits
				#the data is written to a new directory for quality
				#test files that pass syntax and validity edits.

				utils.write_file(path=self.filepaths['quality_pass_s_v_filepath'].format(
					bank_name=self.clean_config['name']['value']),
					ts_input=ts_df,
					lar_input=lar_df,
					name=quality_filename)

			#The case if there are rows that failed syntax or validity edits.

			else:
				#Creates an empty list for storing row numbers
				#where edits have failed.
				uli_list = []

				#Iterates through each row and appends the list of ULI's
				#of rows where syntax or validity edits have failed.
				for index, row in report_df.iterrows():
					uli_list.append(row.row_ids)

				#Drops not-a-numbers from the ULI list.
				if np.nan in uli_list:
					uli_list.remove(np.nan)

				#Creates a new list to store the ULI's without nested brackets.
				new_list = []
				for i in range(len(uli_list)):
					for n in range(len(uli_list[i])):
						new_list.append(uli_list[i][n])

				#Creates a list that removes ULI's that are repeated.
				unique_uli_list = []
				for i in new_list:
					if i not in unique_uli_list:
						unique_uli_list.append(i)

				#Creates a list of row numbers corresponding to the
				#ULI's that have failed syntax or validity edits.
				bad_rows = []
				for index, row in lar_df.iterrows():
					if row['uli'] in unique_uli_list:
						failed_uli = row['uli']
						bad_rows.append(lar_df[lar_df['uli']==failed_uli].index.values.astype(int)[0])

				#Drops all rows that failed syntax or validity edits
				#from the original LAR dataframe.
				lar_df = lar_df.drop(bad_rows)

				#Creates new lar rows to the original length of the file
				#using the utils new lar rows function.
				ts_df, lar_df = utils.new_lar_rows(final_row_count=original_length,
					lar_df=lar_df, ts_df=ts_df)

				#Writes the file to the new path for quality test files
				#that pass syntax and validity edits.
				utils.write_file(path=self.filepaths['quality_pass_s_v_filepath'].format(bank_name=self.clean_config['name']['value']),
					ts_input=ts_df, lar_input=lar_df, name=quality_filename)

				#Prints to the console the name of the file being changed.
				print("Adjusting {file} to pass syntax and validity edits.".format(file=quality_filename))
				print("File saved in {path}".format(path=self.filepaths['quality_pass_s_v_filepath'].format(bank_name=self.clean_config['name']['value'])))

		#The condition where there are no clean rows present in the file.
		except ZeroDivisionError as e:
			#Prints a message to indicate that the file has not been validated.
			print(e)
			print("Sorry no clean file available for {file}.".format(file=quality_filename))

	def edit_report(self):
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
		#LAR schema, a TS schema, and geographic geographic data.
		checker = rules_engine(lar_schema=self.lar_schema_df,
			ts_schema=self.ts_schema_df, geographic_data=self.geographic_data)

		#Seperates data from the filepath and filename into a TS dataframe
		#and a LAR dataframe.
		ts_df, lar_df = utils.read_data_file(path=self.edit_report_config['data_filepath'],
			data_file=self.edit_report_config['data_filename'])

		#Loads the TS and LAR dataframes into the checker object.
		checker.load_data_frames(ts_df, lar_df)

		#Applies each function in the rules engine that checks for edits
		#and creates a results list of edits failed or passed.
		for func in dir(checker):
			if func[:1] in ("s", "v", "q") and func[1:4].isdigit()==True:
				getattr(checker, func)()

		#Creates a dataframe of results from the checker.
		report_df = pd.DataFrame(checker.results)

		#Writes the report to the filepath and name designated in
		#the test_fielpaths yaml
		edit_report_path = self.edit_report_config['edit_report_output_filepath']

		if not os.path.exists(edit_report_path):
			os.makedirs(edit_report_path)

		report_df.to_csv(edit_report_path +self.edit_report_config['edit_report_output_filename'])

		#Logs the result.
		logging.info("Edit Report has been created in {filepath}".format(
			filepath=edit_report_path))

	def create_custom_row(self, dictionary, clean_filepath, clean_filename):

		"""
		Creates a custom clean LAR row by passing in a dictionary of columns
		and new values to modify all the rows of an
		existing clean file, filters the modified file for clean rows,
		and then pulls the first row from the file.
		Pulls rows from the clean file last generated. Suggestion that
		the file pulled should be 1000 original rows or greater, to ensure
		that modified clean rows can be found.
		"""
		#Creates a TS and LAR dataframe from the clean filepath and name
		#specified.
		ts_df, lar_df = utils.read_data_file(
					path=clean_filepath,
					data_file=clean_filename)

		#Changes each column (key in the dictionary) to the new value in
		# the dictionary.
		for key, value in dictionary.items():
			lar_df[key] = value

		checker = rules_engine(lar_schema=self.lar_schema_df,
					ts_schema=self.ts_schema_df,
					geographic_data=self.geographic_data)

		#Produces a report as to which syntax or validity
		#edits have passed or failed based on logic in the rules_engine.
		#Loads the TS and LAR dataframes into the checker object.

		checker.load_data_frames(ts_df, lar_df)

		for func in dir(checker):
			if func[:1] in ("s", "v") and func[1:4].isdigit()==True:
				getattr(checker, func)()


		#Produces a report as to which syntax or validity
		#edits have passed or failed based on logic in the rules_engine.
		for func in dir(checker):
			if func[:1] in ("s", "v") and func[1:4].isdigit()==True:
				getattr(checker, func)()

		#Creates a results dataframe and keeps the results that
		#have failed.
		report_df = pd.DataFrame(checker.results)
		report_df = report_df[(report_df['status']=='failed')].copy()

		# The function ignores TS edits and drops results related
		# to edit fails from the TS.
		report_df = report_df[report_df['row_ids'] != 'TS']

		if len(report_df) == 0:
			#If there are no syntax or validity edits
			#the data is written to a new directory for quality
			#test files that pass syntax and validity edits.

			#Takes the first row of data.
			lar_row = lar_df[0:1]

		#The case if there are rows that failed syntax or validity edits.

		else:
			#Creates a list of ULI's corresponding to rows where
			#syntax or validity edits have failed.

			#The resulting list is a list of lists, a list of ulis failed for each
			#edit failed.
			uli_list = list(report_df.row_ids)

			#Converts the list of lists to a single list.
			single_uli_list = []
			for i in uli_list:
				single_uli_list = single_uli_list + i

			#Creates a list that removes ULI's that are repeated.
			unique_uli_list = set(single_uli_list)

			#Drops rows in the data containing syntax or validity edits.
			lar_df = lar_df[lar_df.uli.isin(unique_uli_list)].copy()

			#Only one row is needed for output.
			#The following, takes the first row of data from the clean dataframe
			lar_row = lar_df[0:1]

		return(lar_row)
