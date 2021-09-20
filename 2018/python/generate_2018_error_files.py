import os
import yaml
#This script will generate a file that will fail a specific syntax, validity, or quality edit 
#(though others may also fail)
#This script relies on the presence of a clean data file

from file_generator import FileGenerator

#Instantiating the file generator. 
file = FileGenerator('configurations/clean_file_config.yaml')

#Creates quality that pass syntax and validity for each test file 
#in the edits_files directory
file.create_files(kind='error_files')

#The following code validates quality edits to pass syntax and validity edits. 
#Stores a list of filenames from the quality edits directory. 
quality_files = os.listdir(file.filepaths['quality_filepath'].format(bank_name=file.data_map['name']['value']))

#Validates quality edits and stores them in a new directory specified in the test filepaths configuration. 
for quality_file in quality_files:
	file.validate_quality_edit_file(quality_filename=quality_file)

