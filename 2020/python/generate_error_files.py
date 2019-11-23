import json
import logging
import os
import yaml

import pandas as pd


from lar_constraints import lar_data_constraints
import lar_generator
from test_file_generator import test_data_creator
import utils
#This script will generate files that fail specific syntax, validity, or quality edit 
#(though others may also fail)
#This script relies on the presence of a clean data file

#load configurations
config_file = 'configurations/clean_file_config.yaml'
bank_config = 'configurations/bank1_config.yaml'
geo_config_file='configurations/geographic_data.yaml'
filepaths_file = 'configurations/test_filepaths.yaml'
lar_schema_file="../schemas/lar_schema.json"
ts_schema_file="../schemas/ts_schema.json"

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

DEBUG = False

#load geographic data
geographic_data = pd.read_csv(geo_config['geographic_data_file'], delimiter='|', header=0,
	names=geo_config['file_columns'], dtype=object) #instantiate Census file data as dataframe

#create 11 digit Census Tract codes from 5 digit county and 6 digit tract
geographic_data['county_fips'] = geographic_data.apply(lambda x: str(x.state_code) + str(x.county), axis=1)
geographic_data["tract_fips"] = geographic_data.apply(lambda x: str(x.county_fips) + str(x.tracts), axis=1)


test_file_gen = test_data_creator(ts_schema_file=ts_schema_file, lar_schema_file=lar_schema_file, bank_config_data=bank_config_data,
								state_codes=geo_config["state_codes"], county_df=geographic_data[["county_fips", "small_county"]])


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
#quality_files = os.listdir(file.filepaths['quality_filepath'].format(bank_name=file.clean_config['name']['value']))

#Validates quality edits and stores them in a new directory specified in the test filepaths configuration. 
#FIXME: this creates a quality edit file that passes S/V for every file in the directory
#FIXME: change this to only reference the quality files with the current clean file row count
#for quality_file in quality_files:
#	file.validate_quality_edit_file(quality_filename=quality_file)
#




