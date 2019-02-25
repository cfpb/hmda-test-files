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

#Loads the custom file specifications yaml. 
yaml_file ='custom_file_specifications.yaml'
with open(yaml_file, 'r') as f:
    custom_file = yaml.safe_load(f)

#Stores each feature of the large_file category of the yaml file.
source_filepath = custom_file['large_file']['source_filepath']
source_filename = custom_file['large_file']['source_filename']
output_filepath = custom_file['large_file']['output_filepath']
output_filename = custom_file['large_file']['output_filename']
row_count = custom_file['large_file']['row_count']
bank_name = custom_file['large_file']['bank_name']
lei = custom_file['large_file']['lei']
tax_id = custom_file['large_file']['tax_id']

print(source_filepath)
print(source_filename)

#Loads in TS and LAR data from the source filepath and source filename. 
ts_data, lar_data = utils.read_data_file(path=source_filepath, 
    data_file=source_filename)

#Changes TS and LAR data to the test institution in the configuration file.
ts_data, lar_data = utils.change_bank(ts_data=ts_data, lar_data=lar_data, new_bank_name=bank_name, 
    new_lei=lei, new_tax_id=tax_id)

ts_data, lar_data = utils.new_lar_rows(row_count=row_count, lar_df=lar_data, ts_df=ts_data)

#Writes file to the output filepath and name in the custome file specifications yaml. 
utils.write_file(path=output_filepath, ts_input=ts_data, lar_input=lar_data, name=output_filename)

#Prints a statement of the file created. 
statement = (str("{:,}".format(len(lar_data.index))) + 
            " Row File Created for " + str(bank_name) + 
            " File Path: " + str(output_filepath+output_filename))
        
print(statement)

 

       
