#This script is used to create test files that pass all syntax and validity edits that do not require panel data.
#Configuration of the generated data is done in config.yaml.
#This script will write files to the relative path "../edits_files/"
#This script must be run before generate_error_files.py as that script relies on the presence of a clean file to modify.
#2018 Filing Instruction Guide: https://www.consumerfinance.gov/data-research/hmda/static/for-filers/2018/2018-HMDA-FIG.pdf

from file_generator import FileGenerator
import sys

def runGenerator(filename=''):

    #Instantiating the file generator.
    file = FileGenerator(filename)
    file.create_files(kind='clean_file')

if __name__ == '__main__':

    # check to see if filename is passed in
    if len(sys.argv) == 2: filename = sys.argv[1]
    else: filename = 'configurations/clean_file_config.yaml'
    runGenerator(filename)
