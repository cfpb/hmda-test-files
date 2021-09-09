import json
import os
from os.path import join, isfile
from os import listdir, makedirs, path

import pandas as pd
import yaml

#Edit report configurations are located in configurations/edit_report_config.yaml
from rules_engine import rules_engine


#load configurations
lar_config_file = 'configurations/clean_file_config.yaml'
bank_config = 'configurations/bank1_config.yaml'
geo_config_file='configurations/geographic_data.yaml'
filepaths_file = 'configurations/test_filepaths.yaml'
lar_schema_file="../schemas/lar_schema.json"
ts_schema_file="../schemas/ts_schema.json"

#open configuration files and load data
with open(bank_config) as f:
	bank_config_data = yaml.safe_load(f)

with open(lar_config_file, 'r') as f:
	lar_file_config_data = yaml.safe_load(f)

with open(filepaths_file, 'r') as f:
	filepaths = yaml.safe_load(f)

with open(geo_config_file, 'r') as f:
	geo_config = yaml.safe_load(f)

with open(bank_config, 'r') as f:
	bank_config_data = yaml.safe_load(f)

with open(geo_config["zip_code_file"], 'r') as f:
	zip_codes = json.load(f)
zip_codes.append("Exempt")

#set location for edit report CSV writing
edit_report_path = filepaths["edit_report_output_filepath"] 
#get paths to check for clean files (by bank name)
bank_clean_dir = filepaths["clean_filepath"].format(bank_name=bank_config_data["name"]["value"])

geographic_data = pd.read_csv(geo_config['geographic_data_file'], delimiter=',', header=0,
	names=geo_config['file_columns'], dtype=object) #instantiate Census file data as dataframe

#create 11 digit Census Tract codes from 5 digit county and 6 digit tract
geographic_data['county_fips'] = geographic_data.apply(lambda x: str(x.state_code) + str(x.county), axis=1)
geographic_data["tract_fips"] = geographic_data.apply(lambda x: str(x.county_fips) + str(x.tracts), axis=1)

#instantiate rules engine to test clean and error files
rules_engine = rules_engine(config_data=lar_file_config_data, state_codes=geo_config["state_codes"], 
	state_codes_rev=geo_config["state_codes_rev"], geographic_data=geographic_data, full_lar_file_check=True)

#get all files in clean folder(s)
clean_file_names = listdir(bank_clean_dir)
clean_file_names = [f for f in listdir(bank_clean_dir) if isfile(join(bank_clean_dir, f))]
if '.DS_Store' in clean_file_names:
	clean_file_names.remove('.DS_Store')

#get directories to check for files
bank_test_v_dir = filepaths["validity_filepath"].format(bank_name=bank_config_data["name"]["value"])
bank_test_s_dir = filepaths["syntax_filepath"].format(bank_name=bank_config_data["name"]["value"])
bank_test_q_dir = filepaths["quality_filepath"].format(bank_name=bank_config_data["name"]["value"])
bank_test_q_pass_dir = filepaths["quality_pass_s_v_filepath"].format(bank_name=bank_config_data["name"]["value"])

#FIXME add bank_test_q_pass_dir when logic is ready 
edit_filepaths = [bank_test_v_dir, bank_test_s_dir, bank_test_q_dir]

edit_file_names = []
for path in edit_filepaths:
	#concat edit file path to edit file name to make looping easier in edit check
	file_names = [path+f for f in listdir(path) if isfile(join(path, f))]
	edit_file_names = edit_file_names + file_names

try:
	edit_file_names = [f for f in edit_file_names if '.DS_Store' not in f]
except:
	print("no DS Store to remove")

edit_file_names.sort()
print(len(clean_file_names), "clean files to check")
print(len(edit_file_names), "edit files to check")
#set up data structures to hold edit report data
clean_report_df = pd.DataFrame([], columns=['file_name', 'edit_name', 'row_type', 'field', 'fail_count', 'failed_rows'], index=[0])
edit_report_df = pd.DataFrame([], columns=['file_name', 'edit_name', 'row_type', 'field', 'fail_count', 'failed_rows'], index=[0])


#loop over each clean file and compile report of files that failed edits. 
#Produce edit report for each file with fails

print("starting clean file loop")
for file in clean_file_names:
	rules_engine.reset_results() #clear previous edit report results
	#print(file)
	ts_df, lar_df = rules_engine.split_ts_row(bank_clean_dir+file)
	for rule in rules_engine.svq_edit_functions:
		if rule[:1] in ("s", "v", "q") and rule[1:4].isdigit()==True:
					getattr(rules_engine, rule)()
	if len(rules_engine.results)>0:
		new_results_df = pd.DataFrame(rules_engine.results)
		#add filename for edit tracking and reorder columns for concatenation of output
		new_results_df["file_name"] = file
		new_results_df = new_results_df[['file_name', 'edit_name', 'row_type', 'field', 'fail_count', 'failed_rows']] 
		clean_report_df = pd.concat([clean_report_df, new_results_df])

print("starting test file loop")
all_edits = False
for file in edit_file_names:
	#print(file)
	rules_engine.reset_results() #clear previous edit report results
	ts_df, lar_df = rules_engine.split_ts_row(file)
	for rule in rules_engine.svq_edit_functions:
		if all_edits == False: #only test for the edit in the file name
			if rule in file:
				#print("in rule", rule)
				getattr(rules_engine, rule)()
		else:
			getattr(rules_engine, rule)()

	if len(rules_engine.results)>0:
		new_results_df = pd.DataFrame(rules_engine.results)
	#add filename for edit tracking and reorder columns for concatenation of output
		new_results_df["file_name"] = file
		new_results_df = new_results_df[['file_name', 'edit_name', 'row_type', 'field', 'fail_count', 'failed_rows']] 
		edit_report_df = pd.concat([edit_report_df, new_results_df])

print(len(clean_report_df), "clean file edit report rows")
print(len(edit_report_df), "edit file edit report rows")

#save report outputs
if not os.path.exists(edit_report_path):
	os.makedirs(edit_report_path)

#reset index to drop starter row
clean_report_df.reset_index(drop=True, inplace=True)
edit_report_df.reset_index(drop=True, inplace=True)
#remove starter row
clean_report_df.drop(0, inplace=True)
edit_report_df.drop(0, inplace=True)

clean_report_df.to_csv(edit_report_path + filepaths['clean_file_report_output_filename'].format(bank_name=bank_config_data["name"]["value"])
	,sep="|", index=False)
edit_report_df.to_csv(edit_report_path + filepaths['edit_report_output_filename'].format(bank_name=bank_config_data["name"]["value"]),
	 sep="|", index=False)
