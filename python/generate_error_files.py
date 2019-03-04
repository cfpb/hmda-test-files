#This script will generate a file that will fail a specific edit (though others may also fail)
#This script relies on the presence of a clean data file

#fixme: add file_length, data_file name to config.yaml
import json
import os
import pandas as pd
import yaml

from test_file_generator import test_data
import utils

#load config data from yaml file
with open('config.yaml') as f:
	# use safe_load instead load
	data_map = yaml.safe_load(f)

ts_schema = pd.DataFrame(json.load(open("../schemas/ts_schema.json"))) #load TS schema
lar_schema = pd.DataFrame(json.load(open("../schemas/lar_schema.json"))) #load LAR schema
#instantiate test_file_generator.py to modify clean data so that the resulting files fail specific edits
file_maker = test_data(ts_schema=ts_schema, lar_schema=lar_schema) #instantiate edit file maker

ts_data, lar_data = utils.read_data_file(path="../edits_files/clean_files/{bank_name}/".format(bank_name=data_map["name"]["value"]), 
data_file=data_map["clean_file"]["value"]) #load clean data file
file_maker.load_data_frames(ts_data, lar_data) #pass clean file data to file maker object
#generate a file for each edit function in file maker
edits = []
for func in dir(file_maker): #loop over all data modification functions
	if func[:1] in ("s", "v", "q") and func[1:4].isdigit()==True: #check if function is a numbered syntax or validity edit
		print("applying:", func)
		getattr(file_maker, func)() #apply data modification functions and produce files
