import file_generator
from file_generator import FileGenerator
import utils
import glob
import os

new_file = FileGenerator()

new_file.create_custom_file(
	yaml_filepath='custom_files/ffiec_logic/configurations/sex_categorization.yaml',
	filepath='custom_files/ffiec_logic/output/',
 	filename='sex_categorization_test.txt', 
 	filepath_answers='custom_files/ffiec_logic/answers/', 
 	filename_answers='sex_categorization_answers.txt')