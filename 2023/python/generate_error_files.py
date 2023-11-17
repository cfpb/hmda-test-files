import json
import logging
import os
from os import listdir
from os.path import isfile, join
import yaml

import pandas as pd


from lar_constraints import lar_data_constraints
import lar_generator
from rules_engine import rules_engine
from test_file_generator import test_data_creator
import utils
#This script will generate files that fail specific syntax, validity, or quality edit 
#(though others may also fail)
#This script relies on the presence of a clean data file

#load configurations
config_file = '2023/python/configurations/clean_file_config.yaml'
bank_config = '2023/python/configurations/bank1_config.yaml'
geo_config_file='2023/python/configurations/geographic_data.yaml'
filepaths_file = '2023/python/configurations/test_filepaths.yaml'
lar_schema_file="2023/schemas/lar_schema.json"
ts_schema_file="2023/schemas/ts_schema.json"

#load config data
print("start initialization of LAR generator")
with open(config_file, 'r') as f:
	# use safe_load instead load
	lar_file_config_data = yaml.safe_load(f)

with open(filepaths_file, 'r') as f:
	filepaths = yaml.safe_load(f)

#load geographic configuration and census data
print("loading geo data")
with open(geo_config_file, 'r') as f:
	geo_config = yaml.safe_load(f)

with open(bank_config, 'r') as f:
	bank_config_data = yaml.safe_load(f)

with open(geo_config["geographic_data_file"], 'r') as f:
	geographic_data = yaml.safe_load(f)

#set quality filepath to the name of the bank being used
filepaths["quality_filepath"] = filepaths["quality_filepath"].format(bank_name=bank_config_data["name"]["value"]) 

DEBUG = False

#load geographic data
geographic_data = pd.read_csv(geo_config['geographic_data_file'], delimiter='|', header=0,
	names=geo_config['file_columns'], dtype=object) #instantiate Census file data as dataframe

#create 11 digit Census Tract codes from 5 digit county and 6 digit tract
geographic_data['county_fips'] = geographic_data.apply(lambda x: str(x.state_code) + str(x.county), axis=1)
geographic_data["tract_fips"] = geographic_data.apply(lambda x: str(x.county_fips) + str(x.tracts), axis=1)


test_file_gen = test_data_creator(ts_schema_file=ts_schema_file, lar_schema_file=lar_schema_file, 
								  bank_config_data=bank_config_data, state_codes=geo_config["state_codes"], 
								  county_df=geographic_data[["county_fips", "small_county"]])

#config_data, state_codes, state_codes_rev, geographic_data
checker = rules_engine(state_codes=geo_config["state_codes"], state_codes_rev=geo_config["state_codes_rev"],
					   config_data=lar_file_config_data, geographic_data=geographic_data)

clean_data_path = filepaths["clean_filepath"].format(bank_name=bank_config_data["name"]["value"])
clean_file_name = filepaths["clean_filename"].format(bank_name=bank_config_data["name"]["value"], 
													 row_count=bank_config_data["file_length"]["value"])
#load data to test file creator
ts_df, lar_df = utils.read_data_file(path=clean_data_path, data_file=clean_file_name) 

test_file_gen.load_ts_data(ts_df)
test_file_gen.load_lar_data(lar_df)


for edit in test_file_gen.test_file_funcs:
	print("creating file for: ", edit)
	getattr(test_file_gen, edit)()

#check for presence of clean files for specified bank config

#create clean files if none exist

#create error files

#create validated quality files


#Creates quality that pass syntax and validity for each test file 
#in the edits_files directory

#validates quality edits to pass syntax and validity edits. 
#Stores a list of filenames from the quality edits directory. 
quality_files = [f for f in listdir(filepaths["quality_filepath"]) if isfile(join(filepaths["quality_filepath"], f))]
print(len(quality_files), "quality files to fix")
for quality_file in quality_files:
	#try:

	print(quality_file, " is gettin fixed!")

	#split TS and LAR records for use with Pandas DataFrames
	ts_df, lar_df = utils.read_data_file(path=filepaths['quality_filepath'], data_file=quality_file)
	
	#load data to submission engine to check for S/V fails
	checker.load_lar_data(lar_df) 
	checker.load_ts_data(ts_df) 
	checker.reset_results()
	#generate an edits report for the file
	#this will mark the rows that need to be removed to ensure the file passes S/V edits
	for func in dir(checker):
		if func[:1] in ("s", "v") and func[1:4].isdigit()==True:
			getattr(checker, func)()

	#capture edit report results
	report_df = pd.DataFrame(checker.results)
	report_df = report_df[report_df['row_type'] != 'TS'].copy() #remove records relating to TS fails
	#remove report rows that did not have fails
	report_df = report_df[report_df.apply(lambda x: len(x.failed_rows)>0, axis=1)].copy()

	#copy rows that pass S/V edits and remove ones that do not to make a test file free of S/V edits
	#remove lar rows with S/V fails
	bad_uli_list = report_df.failed_rows.to_list()
	#flat_list = [item for sublist in l for item in sublist]
	bad_uli_list = [uli for sublist in bad_uli_list for uli in sublist]
	bad_uli_list = set(bad_uli_list) #convert to set to remove duplicates
	print(len(bad_uli_list), "bad ULIs")
	print(bad_uli_list)
	print(len(lar_df), "before dropping bad ulis")

	clean_lar_df = lar_df[~lar_df.uli.isin(bad_uli_list)].copy() #drop rows failing S/V from lar_df

	if len(clean_lar_df) <=0:
		print("all LAR records removed")
		continue
	else: 
		print(len(clean_lar_df), "after")

		#rebuild lar_df to original size by copying clean rows and regenerating ULIs
		ts_df, clean_lar_df = utils.new_lar_rows(final_row_count=len(lar_df), lar_df=clean_lar_df, ts_df=ts_df)

	utils.write_file(path=filepaths['quality_pass_s_v_filepath'].format(bank_name=bank_config_data['name']['value']),
		ts_input=ts_df, lar_input=clean_lar_df, name=quality_file)

	#Prints to the console the name of the file being changed.
	print("Adjusting {file} to pass syntax and validity edits.".format(file=quality_file))
	print("File saved in {path}".format(path=filepaths['quality_pass_s_v_filepath'].format(bank_name=bank_config_data['name']['value'])))

	#except ZeroDivisionError as e:
	#	print(e)
	#	print("Unable to generate a clean {file}. Try using a longer base file (it helps the mathing).".format(file=quality_file))

#Validates quality edits and stores them in a new directory specified in the test filepaths configuration. 
#FIXME: this creates a quality edit file that passes S/V for every file in the directory
#FIXME: change this to only reference the quality files with the current clean file row count
