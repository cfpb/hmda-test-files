#This script creates a test file, using the row_by_row_modification
#function in utils. The row_by_row_modification_yaml file is used 
#with the function to make modifications to an existing file specifying rows, 
#columns, and values to be changed.

#The source filepaths, output filepaths, and number of rows for this script
#are stored in the custom_file_specifications yaml file under 
#"row_by_row_file."

#The following code imports the utils package and yaml library.
import utils
import yaml

#Import custom_file_specifications yaml file. 
yaml_file ='custom_file_specifications.yaml'
with open(yaml_file, 'r') as f:
	custom = yaml.safe_load(f)

#Loads TS and LAR data from the source file and path from 
#custom_file_specifications yaml file. 
ts_df, lar_df = utils.read_data_file(path=custom["row_by_row_file"]["source_filepath"], 
	data_file=custom["row_by_row_file"]["source_filename"])

#Creates a file with a number of LAR rows specified in the 
#custom_file_specifications yaml file.
lar_df, ts_df = utils.new_lar_rows(row_count=custom["row_by_row_file"]["row_count"], 
	lar_df=lar_df, ts_df=ts_df)

#Modifies the LAR rows based on the row_by_row_modification yaml file.
lar_df = utils.row_by_row_modification(lar_df)

#Writes a file to the filename and path in the custom_file_specifications yaml
#file. 
utils.write_file(path=custom["row_by_row_file"]["output_filepath"], 
	ts_input=ts_df, lar_input=lar_df, name=custom["row_by_row_file"]["output_filename"])

#Outputs print statements indicating the number of LAR, the filename, 
#and the filepath the new file is stored. 
print("Row count is " + str(len(lar_df)) + " for " + str(custom["row_by_row_file"]["output_filename"]))
print(str(custom["row_by_row_file"]["output_filepath"]) + " is stored in " + str(custom["row_by_row_file"]["output_filename"]))
