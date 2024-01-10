import math
import json
import os
import pandas as pd
import random
import string
import time
import yaml
import utils

#set configuration files
#FIXME these will be moved to a single config location
bank_config = '2022/python/configurations/bank2_config.yaml'
lar_config_file = '2022/python/configurations/clean_file_config.yaml'
filepaths_file = '2022/python/configurations/test_filepaths.yaml'
large_file_config = "2022/python/configurations/large_file_config.yaml"

#Loads the clean lar file configuration. this may no longer be needed here
with open(lar_config_file) as f:
	clean_config = yaml.safe_load(f)

#loads filepath configurations
with open(filepaths_file) as f:
	filepaths = yaml.safe_load(f)

#loads bank data configurations (for TS data)
with open(bank_config) as f:
	bank_config_data = yaml.safe_load(f)

with open(large_file_config) as f:
	large_file_settings = yaml.safe_load(f)

bank_name = bank_config_data['name']['value']
base_clean_file_length = large_file_settings['large_file_base_length']['value']
large_file_length = large_file_settings['large_file_write_length']['value']
lei = bank_config_data['lei']['value']
tax_id = bank_config_data['tax_id']['value']

source_filepath = filepaths['clean_filepath'].format(bank_name=bank_name)
source_filename = filepaths['clean_filename'].format(bank_name=bank_name, row_count=base_clean_file_length)
output_filepath = filepaths['clean_filepath'].format(bank_name=bank_name)
output_filename = filepaths['clean_filename'].format(bank_name=bank_name, row_count=large_file_length)
print("*********")
print("source_filepath:")
print(source_filepath)
print("source_filename:")
print(source_filename)
print("output_filepath:")
print(output_filepath)
print("output_filename:")
print(output_filename)

#Loads in TS and LAR data from the source filepath and source filename. 
ts_data, lar_data = utils.read_data_file(path=source_filepath, 
    data_file=source_filename)

#Changes TS and LAR data to the test institution in the configuration file.
ts_data, lar_data = utils.change_bank(ts_data=ts_data, lar_data=lar_data, new_bank_name=bank_name, 
    new_lei=lei, new_tax_id=tax_id)

ts_data, lar_data = utils.new_lar_rows(final_row_count=large_file_length, lar_df=lar_data, ts_df=ts_data)

#If a row by row modification yaml file is present in the configuration, the row by row modification function is applied. 
if filepaths["row_level_modification_config"] != None:
	lar_data = utils.row_by_row_modification(lar_data, yaml_filepath=filepaths["row_level_modification_config"])

#Writes file to the output filepath and name in the large file specifications yaml. 
utils.write_file(path=output_filepath, ts_input=ts_data, lar_input=lar_data, name=output_filename)

#Prints a statement of the file created. 
statement = (str("{:,}".format(len(lar_data.index))) + 
            " Row File Created for " + str(bank_name) + 
            " File Path: " + str(output_filepath+output_filename))
print("*********")
print()        
print(statement)

 

       
