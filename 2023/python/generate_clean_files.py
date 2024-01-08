import json
import logging
import os
import sys

import pandas as pd
import yaml

from lar_constraints import lar_data_constraints
import lar_generator
from rules_engine import rules_engine
import utils



config_file = '2023/python/configurations/clean_file_config.yaml'
bank_config = '2023/python/configurations/bank2_config.yaml'

if len(sys.argv) == 2:
	bank_config = sys.argv[1]

geo_config_file='2023/python/configurations/geographic_data.yaml'
filepaths_file = '2023/python/configurations/test_filepaths.yaml'
lar_schema_file="2023/schemas/lar_schema.json"
ts_schema_file="2023/schemas/ts_schema.json"

LOGGING = False
#load config data
print("start initialization of LAR generator")
with open(config_file, 'r') as f:
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
if not os.path.exists(filepaths["log_filepath"]):
	os.makedirs(filepaths["log_filepath"])

#if LOGGING:
logging.basicConfig(filename=filepaths["log_filepath"]+filepaths['log_filename'], format='%(asctime)s %(message)s', 
					datefmt='%m/%d/%Y %I:%M:%S %p', filemode=filepaths['log_mode'], level=logging.INFO)

geographic_data = pd.read_csv(geo_config['geographic_data_file'], delimiter='|', header=0,
	names=geo_config['file_columns'], dtype=object) #instantiate Census file data as dataframe

#create 11 digit Census Tract codes from 5 digit county and 6 digit tract
geographic_data['county_fips'] = geographic_data.apply(lambda x: str(x.state_code) + str(x.county), axis=1)
geographic_data["tract_fips"] = geographic_data.apply(lambda x: str(x.county_fips) + str(x.tracts), axis=1)

with open(geo_config["zip_code_file"], 'r') as f:
	zip_codes = json.load(f)
zip_codes.append("Exempt")

#instantiate lar generator to create random LAR and fixed TS data
lar_gen = lar_generator.lar_gen(lar_schema_file=lar_schema_file, ts_schema_file=ts_schema_file)

#set lar_file_config lei to match bank config data
lar_file_config_data["lei"]["value"] = bank_config_data["lei"]["value"]
#instantiate rules engine to check conformity of synthetic data to FIG schema
rules_engine = rules_engine(config_data=lar_file_config_data, state_codes=geo_config["state_codes"], state_codes_rev=geo_config["state_codes_rev"],
	geographic_data=geographic_data, full_lar_file_check=False)

#instantiate constraints logic to force LAR data to conform to FIG schema
lar_constraints = lar_data_constraints(lar_file_config=lar_file_config_data, geographic_data=geographic_data)

#store original row for diff comparison to see what elements are being changed

ts_row = lar_gen.make_ts_row(bank_file_config=bank_config_data) #create TS row, we only need one
ts_df = pd.DataFrame(ts_row, index=[0])
rules_engine.load_ts_data(ts_df) #loading ts_row to rules_engine converts it to a dataframe for value checking
lar_rows = [] #list to hold all OrderedDict LAR records before writing to file

for i in range(bank_config_data["file_length"]["value"]):
	print("generating row {count}".format(count=i))
	#create initial LAR row
	lar_row = lar_gen.make_row(lar_file_config=lar_file_config_data, geographic_data=geographic_data, 
							   state_codes=geo_config["state_codes_rev"], zip_code_list=zip_codes)
	rules_engine.load_lar_data(lar_row) #loading lar_row to rules engine converts it to a dataframe for value checking

	#generate error report
	edit_report_df = rules_engine.create_edit_report(rules_list=["s", "v", "q"])
	if LOGGING:
		logging.info("generating row {count}".format(count=i))
	if DEBUG:
		print(edit_report_df)

	#apply constraints to force conformity with FIG schema for LAR data
	constraints_iter = 0
	while len(edit_report_df[edit_report_df.fail_count>0]):
		if LOGGING:
			logging.info(edit_report_df[edit_report_df.fail_count>0]) #log the edit fails for the row
			logging.info("constraints iteration {}. checking difference in rows".format(constraints_iter))
		lar_row_start_items = set(lar_row.items()) #capture initial row data before modifications to log difference between initial and changed row
		
		for constraint in lar_constraints.constraints: #loop over all constraint functions to force LAR data to conform to FIG spec
			lar_row = getattr(lar_constraints, constraint)(lar_row) #lar_row is an ordered dict here
		if LOGGING:
			logging.info(set(lar_row.items() - lar_row_start_items))
		constraints_iter += 1
		#prepare new edit fails report for checking lar generation process this is the loop break condition
		rules_engine.reset_results()
		rules_engine.load_lar_data(lar_row)
		edit_report_df = rules_engine.create_edit_report() 
		

		if DEBUG:
			print(len(edit_report_df[edit_report_df.fail_count>0]))
			print(edit_report_df[edit_report_df.fail_count>0])
	lar_rows.append(lar_row)

lar_rows_df = pd.DataFrame(lar_rows)

if DEBUG:
	rules_engine.load_lar_data(lar_rows_df)
	rules_engine.reset_results()
	edit_report_df = rules_engine.create_edit_report()
	if LOGGING:
		logging.info("final edit report for generated LAR file ")
		logging.info(edit_report_df)
	print(edit_report_df)

clean_filename = filepaths["clean_filename"].format(bank_name=bank_config_data["name"]["value"], row_count=bank_config_data["file_length"]["value"])
clean_filepath = filepaths["clean_filepath"].format(bank_name=bank_config_data["name"]["value"])
print("*********")
print("clean_filename:")
print(clean_filename)
print("clean_filepath:")
print(clean_filepath)
#create directory for test files if it does not exist
if not os.path.exists(clean_filepath):
	os.makedirs(clean_filepath)

utils.write_file(path=clean_filepath, name=clean_filename, ts_input=pd.DataFrame(ts_row, index=[0]), lar_input=lar_rows_df)

