#The following code imports the required packages.
import math
import json
import os
import pandas as pd
import random
import string
import time
import yaml
import utils

#Loads the clean file configuration. 
with open('configurations/clean_file_config.yaml') as f:
	clean_config = yaml.safe_load(f)

#Loads the filepath configuration. 
with open('configurations/test_filepaths.yaml') as f:
	filepaths = yaml.safe_load(f)


#row_count = clean_config['row_count']['value']
bank_name = clean_config['name']['value']
base_clean_file_length = clean_config['large_file_base_length']['value']
large_file_length = clean_config['large_file_write_length']['value']
lei = clean_config['lei']['value']
tax_id = clean_config['tax_id']['value']

source_filepath = filepaths['clean_filepath'].format(bank_name=bank_name)
source_filename = filepaths['clean_filename'].format(bank_name=bank_name, n=base_clean_file_length)
output_filepath = filepaths['clean_filepath'].format(bank_name=bank_name)
output_filename = filepaths['clean_filename'].format(bank_name=bank_name, n=large_file_length)

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
        
print(statement)

 

       
