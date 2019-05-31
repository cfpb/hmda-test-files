#This script will write an edit report for a submission file to a path and filename of the user's choosing. 

#Edit report configurations are located in configurations/edit_report_config.yaml

from file_generator import FileGenerator 

#Instantiating the file generator. 
file = FileGenerator()

#Writing edit report.
file.edit_report()