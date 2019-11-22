import json

import pandas as pd
import yaml

from lar_constraints import lar_data_constraints
import lar_generator
from rules_engine import rules_engine
from test_file_generator import test_data
import utils

config_file = 'configurations/clean_file_config.yaml'
geo_config_file='configurations/geographic_data.yaml'
lar_schema_file="../schemas/lar_schema.json"
ts_schema_file="../schemas/ts_schema.json"

#load config data
print("start initialization of LAR generator")
with open(config_file) as f:
	# use safe_load instead load
	lar_file_config_data = yaml.safe_load(f)

#load geographic configuration and census data
print("loading geo data")
with open(geo_config_file, 'r') as f:
	geo_config = yaml.safe_load(f)

geographic_data = pd.read_csv(geo_config['geographic_data_file'], delimiter='|', header=0,
	names=geo_config['file_columns'], dtype=object) #instantiate Census file data as dataframe

#create 11 digit Census Tract codes from 5 digit county and 6 digit tract
geographic_data['county_fips'] = geographic_data.apply(lambda x: str(x.state_code) + str(x.county), axis=1)
geographic_data["tract_fips"] = geographic_data.apply(lambda x: str(x.county_fips) + str(x.tracts), axis=1)
		
with open(geo_config["zip_code_file"], 'r') as f:
	zip_codes = json.load(f)
zip_codes.append("Exempt")

#convert file_generator.py to this script

#instantiate lar generator to create random LAR and fixed TS data
lar_gen = lar_generator.lar_gen(lar_schema_file=lar_schema_file, ts_schema_file=ts_schema_file)

#instantiate rules engine to check conformity of synthetic data to FIG schema
rules_engine = rules_engine(config_data=lar_file_config_data, state_codes=geo_config["state_codes"],
	geographic_data=geographic_data, full_lar_file_check=False)

#instantiate constraints logic to force LAR data to conform to FIG schema
lar_constraints = lar_data_constraints(lar_file_config=lar_file_config_data, geographic_data=geographic_data)

#store original row for diff comparison to see what elements are being changed

ts_row = lar_gen.make_ts_row(lar_file_config=lar_file_config_data) #create TS row, we only need one
rules_engine.load_ts_data(ts_row) #loading ts_row to rules_engine converts it to a dataframe for value checking
lar_rows = [] #list to hold all OrderedDict LAR records before writing to file

for i in range(lar_file_config_data["file_length"]["value"]):
	print("generating row {count}".format(count=i))
	#create initial LAR row
	lar_row = lar_gen.make_row(lar_file_config=lar_file_config_data, geographic_data=geographic_data, state_codes=geo_config["state_codes_rev"], zip_code_list=zip_codes)
	rules_engine.load_lar_data(lar_row) #loading lar_row to rules engine converts it to a dataframe for value checking

	#generate error report
	edit_report_df = rules_engine.create_edit_report()
	print(edit_report_df)

	#apply constraints to force conformity with FIG schema for LAR data
	while len(edit_report_df[edit_report_df.fail_count>0]):
	#if len(edit_report_df[edit_report_df.fail_count>0]) > 0:
		for constraint in lar_constraints.constraints:
			lar_row = getattr(lar_constraints, constraint)(lar_row) #lar_row is an ordered dict here
		rules_engine.reset_results()
		rules_engine.load_lar_data(lar_row)
		edit_report_df = rules_engine.create_edit_report()
		print(len(edit_report_df[edit_report_df.fail_count>0]))
		print(edit_report_df[edit_report_df.fail_count>0])
	lar_rows.append(lar_row)

lar_rows_df = pd.DataFrame(lar_rows)
print(lar_rows_df.head())
lar_rows_df.to_csv("test_lar.txt", sep="|", index=False)

#TODO
#enable logging
#sort out configurations to do stuff more betterrer
