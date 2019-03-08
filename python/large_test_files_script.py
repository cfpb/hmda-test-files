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

#Loads the large file specifications yaml. 
yaml_file ='configurations/large_file_script_config.yaml'
with open(yaml_file, 'r') as f:
    large_file = yaml.safe_load(f)

#Stores each feature of the large_file category of the yaml file.
source_filepath = large_file['source_filepath']
source_filename = large_file['source_filename']
output_filepath = large_file['output_filepath']
output_filename = large_file['output_filename']
row_count = large_file['row_count']
bank_name = large_file['bank_name']
lei = large_file['lei']
tax_id = large_file['tax_id']

#Loads in TS and LAR data from the source filepath and source filename. 
ts_data, lar_data = utils.read_data_file(path=source_filepath, 
    data_file=source_filename)

#Changes TS and LAR data to the test institution in the configuration file.
ts_data, lar_data = utils.change_bank(ts_data=ts_data, lar_data=lar_data, new_bank_name=bank_name, 
    new_lei=lei, new_tax_id=tax_id)

ts_data, lar_data = utils.new_lar_rows(row_count=row_count, lar_df=lar_data, ts_df=ts_data)

#If a row by row modification yaml file is present in the configuration, the row by row modification function is applied. 
if large_file["row_by_row_modification_yaml_file"] != None:
	lar_data = utils.row_by_row_modification(lar_data, yaml_filepath=large_file["row_by_row_modification_yaml_file"])

#Writes file to the output filepath and name in the large file specifications yaml. 
utils.write_file(path=output_filepath, ts_input=ts_data, lar_input=lar_data, name=output_filename)

#Prints a statement of the file created. 
statement = (str("{:,}".format(len(lar_data.index))) + 
            " Row File Created for " + str(bank_name) + 
            " File Path: " + str(output_filepath+output_filename))
        
print(statement)

 

       
