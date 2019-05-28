#This script is used to create test files taht pass all syntax and validity edits that do not require panel data.
#Configuration of the generated data is done in config.yaml.
#This script will write files to the relative path "../edits_files/"
#This script must be run before generate_error_files.py as that script reiles on the presence of a clean file to modify.
#2018 Filing Instruction Guide: https://www.consumerfinance.gov/data-research/hmda/static/for-filers/2018/2018-HMDA-FIG.pdf

from file_generator import FileGenerator 

#Instantiating the file generator. 
file = FileGenerator()

file.create_files(kind='clean_file')




