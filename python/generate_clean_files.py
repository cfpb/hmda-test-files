#This script is used to create test files taht pass all syntax and validity edits that to not require panel data.
#Configuration of the generated data is done in config.yaml.
#This script will write files to the relative path "../edits_files/"
#This script must be run before generate_error_files.py as that script reiles on the presence of a clean file to modify.
#2018 Filing Instruction Guide: https://www.consumerfinance.gov/data-research/hmda/static/for-filers/2018/2018-HMDA-FIG.pdf

from collections import OrderedDict
import json
import os
import pandas as pd
import random
import yaml
import logging
#custom imports
import lar_constraints
import lar_generator
from rules_engine import rules_engine
from test_file_generator import test_data
import utils

#helper functions for data generation
def get_const_list(lar_const):
	"""Creates a list of constraints from the functions in the lar_constraints object."""
	constraints = [] 
	for func in dir(lar_const):
		if func[:1] in ("s", "v") and func[1:4].isdigit()==True:
			constraints.append(func)
	return constraints

def constraints_loop(constraints=[], row=None, row_base=None):
	for const in constraints:
		row = apply_constraint(row, const)
		diff = get_diff(row, row_base)
	return row

def apply_constraint(row, func):
	"""Applies all constraints in the constrains list and returns a LAR row in dictionary format."""
	row_start = row.copy()
	row = getattr(lar_const, func)(row) #apply constraint to row
	diff_1, diff_2 = get_diff(row, row_start)
	if len(diff_1) > 0:
		logging.info(str(func))
		logging.info(diff_1) 
		logging.info(diff_2)
	return row

def get_diff(row, row_base):
	"""Checks the difference between an initial row and the row after constraints are applied"""
	initial_row = set(row_base.items()) #convert initial row to set
	changed_row = set(row.items()) #convert constrained row to set
	diff_1 = (changed_row - initial_row) #subtract row sets to show changes from constraint funcs
	diff_2 = (initial_row - changed_row)
	return diff_1, diff_2

def validation(row, ts_row):
	""""""
	lar_data = pd.DataFrame(row, index=[1])
	ts_data = pd.DataFrame(ts_row, index=[0])
	rules_check = rules_engine(lar_schema=lar_schema_df, ts_schema=ts_schema_df, cbsa_data=cbsas)
		#tracts=tracts, counties=counties) #instantiate edits rules engine
	rules_check.load_lar_data(lar_data)
	rules_check.load_ts_data(ts_data)
	for func in dir(rules_check):
		if func[:1] in ("s", "v") and func[1:4].isdigit()==True:
			#print("applying:", func)
			getattr(rules_check, func)()
	return rules_check.results

#Indicates in the console that the program began and is running. 
print("Running.........")

#Stores the log file name. 
log_file_name = 'clean_files_log.txt'

#Initiating the log file. 
logging.basicConfig(filename=log_file_name,
					format='%(asctime)s %(message)s',
                	datefmt='%m/%d/%Y %I:%M:%S %p',
                	filemode='w',
                	level=logging.INFO)

#load configuration data from YAML file
with open('configurations/config.yaml') as f:
	# use safe_load instead load
	data_map = yaml.safe_load(f)
#load tract and county data from the CBSA file
#tract and county FIPS codes will be used  in geographic data generation
use_cols = ['name', 'metDivName', 'countyFips', 'geoIdMsa', 'metDivFp', 'smallCounty', 'tracts', 'stateCode']
cbsa_cols = ['name', 'metDivName', 'state', 'countyFips', 'county', 'tracts','geoIdMsa', 'metDivFp', 'smallCounty', 
			 'stateCode', 'tractDecimal']
cbsas = pd.read_csv('../dependencies/tract_to_cbsa_2015.txt', usecols=use_cols, delimiter='|', 
					header=None, names=cbsa_cols, dtype=str) #load tract to CBSA data from platform file
cbsas["tractFips"] = cbsas.countyFips + cbsas.tracts
counties = list(cbsas.countyFips)
tracts = list(cbsas.tractFips)
small_counties = list(cbsas.countyFips[cbsas.smallCounty=="1"])

#load schemas for LAR and transmittal sheet
#schemas contain valid enumerations, including NA values, for each field in the dataset
lar_schema_df = pd.DataFrame(json.load(open("../schemas/lar_schema.json", "r")))
ts_schema_df = pd.DataFrame(json.load(open("../schemas/ts_schema.json", "r")))

#instantiate class objects
lar_gen = lar_generator.lar_gen(lar_schema_df, ts_schema_df, counties=counties, tracts=tracts) #lar gen is responsible for generating data according to the schema
lar_const = lar_constraints.lar_constraints(counties=counties, tracts=tracts) #lar constrains is responsible for modifying generated data so that the resulting file passes edits
lar_validator = rules_engine(lar_schema=lar_schema_df, ts_schema=ts_schema_df, cbsa_data=cbsas)
			#tracts=tracts, counties=counties, small_counties=small_counties) #lar validator checks a dataframe and returns a JSON with generate_error_files

#Set parameters for data creation
file_length = data_map["file_length"]["value"] #set number of rows in test file
lei = data_map["lei"]["value"]#None #Flag for presence of an LEI. Only a single LEI should be used for a file, so if one is present, it will be used.
first = True #flag for first row of data. The first row is used to create the dataframe, subsequent rows are appended

#Data generation loop
#lar_gen will produce n rows of data where n=file_length.
#Constraints are applied to ensure that the row produced is valid.
#The rules engine is then used to check if the row passes all edits
#The row is then converted to a Pandas dataframe
for i in range(0, file_length): #loop over file length
	
	stop = False #Flag variable for controlling sub-loop. Stop is set to True if the row passes all edits in the rules engine.
	message = "making new row {row_num}\n\n".format(row_num=i)
	logging.info(message)
	logging.info("*"*50)

	if lei:
		row = lar_gen.make_row(lei=lei) #generate a row using the same  LEI. The same LEI must be used for each row
	else:
		row = lar_gen.make_row() #create new row

	lei = row["lei"] #copy LEI from previous row
	iters = 1 #start iteration count for checking diff time. This is used for troubleshooting.
	ts_row = lar_gen.make_ts_row(data_map) #create dictionary of TS row fields
	#flag for starting the LAR dataframe
	while stop == False:
		row_base = row.copy() #copy row to enable diff
		res = pd.DataFrame(validation(row, ts_row))
		logging.info(res[res.status=="failed"]) #print the results dataframe of edits that failed
		if len(res[res.status=="failed"])<=0:
			stop = True #stop applying constraints to the data row the row passes all edits
		else:
			message = "\nstarting constraints iteration {iter}".format(iter=iters)
			logging.info(message)
			row = constraints_loop(get_const_list(lar_const), row, row_base) #edit the data row by applying constraints
		iters+=1

	if first: #create first row of dataframe
		lar_frame = pd.DataFrame(row, index=[1])
		first = False
		message = "finished row\ncreating dataframe"
		logging.info(message)
	else: #add additional rows to dataframe
		message = "finished row\nappending to dataframe"
		logging.info(message)
		new_lar = pd.DataFrame(row, index=[1])
		lar_frame = pd.concat([lar_frame, new_lar], axis=0)

message = "LAR dataframe complete"
logging.info(message)

print("LAR dataframe complete") #file generation is complete
print("File available in clean files directory")
print("Log Output in {filename}".format(filename=log_file_name))

#check validity and syntax of data using rules_engine
#instantiate edits rules engine to check validity of file.
validator = rules_engine(lar_schema=lar_schema_df, ts_schema=ts_schema_df, cbsa_data=cbsas)#tracts=tracts, counties=counties)

validator.load_lar_data(lar_frame) #load data to validator engine
validator.load_ts_data(pd.DataFrame(ts_row, index=[0], columns=validator.ts_field_names)) #pass a TS dataframe to the rules engine

#check dataframe to see if it passes edits
for func in dir(validator):
	if func[:1] in ("s", "v") and func[1:4].isdigit()==True:
		message = "applying" + str(func)
		logging.info(message) #print which function is being applied
		getattr(validator, func)() #apply validation check

#get validation results
results_df = pd.DataFrame(validator.results) #convert results json object to dataframe
logging.info(results_df[results_df.status=="failed"]) #display dataframe of failed edits. If no rows are present the file is clean of edit rule violations.


#write clean data file to disk
utils.write_file(ts_input=pd.DataFrame(ts_row, index=[0], columns=validator.ts_field_names), lar_input=lar_frame, 
	path="../edits_files/clean_files/{bank_name}/".format(bank_name=data_map["name"]["value"]),
	name="clean_file_{n}_rows_{bank_name}.txt".format(n=file_length, bank_name=data_map["name"]["value"]))


