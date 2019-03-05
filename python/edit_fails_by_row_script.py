#This script creates a file that takes rows from a file designed to fail 
#all rows with the same set of edits and combines rows from a file that passes all edits.

import pandas as pd
import string
import yaml
import utils 

#Loads custom_file_specifications yaml. 
with open('configurations/edit_fails_by_row_script_config.yaml') as f:
	# Use safe_load instead of the load function. 
	data_map = yaml.safe_load(f)

#Loads and stores requisite variables. 
bank_name = data_map['bank_name']
lei = data_map['lei']
tax_id = data_map['tax_id']
rows_failed = data_map['rows_failed']
rows_total = data_map['rows_total']
passes_all_filepath = data_map['passes_all_filepath']
passes_all_filename = data_map['passes_all_filename']
fails_all_filepath = data_map['fails_all_filepath']
fails_all_filename = data_map['fails_all_filename']
output_filepath = data_map['output_filepath']
output_filename = data_map['output_filename']

	
#Loading TS and LAR data for the clean file. 
passes_ts, passes_lar = utils.read_data_file(path=passes_all_filepath, 
                                         data_file=passes_all_filename)

#Loading TS and LAR data for the file that fails a set of edits for every row. 
fail_ts, fail_lar = utils.read_data_file(path=fails_all_filepath,
										 data_file=fails_all_filename)

#Storing the first LAR row of the clean file. 
passes_lar_row = passes_lar.iloc[0:1]

#Storing the first LAR row of the file that fails a set of edits for every row. 	
fails_lar_row = fail_lar.iloc[0:1]

#Checks if the number of rows failed is less than the the number of rows in total.
if rows_failed >= rows_total:
	print("Sorry - rows_failed must be a number less than rows_total.")

else: 

	#Creates LAR rows that pass every edit.  
	rows_passed = pd.concat([passes_lar_row]*(rows_total-rows_failed))

	#Creates a specified number of LAR rows that fail a set of edits.
	rows_failed = pd.concat([fails_lar_row]*(rows_failed))

	#Concatenates the LAR rows above to form the specified number of rows in total. 
	new_lar = pd.concat([rows_passed, rows_failed])

	#Creates a new set of unique ULIs to avoid creating duplicate rows.  
	new_lar = utils.unique_uli(new_lar_df = new_lar, lei=lei)

	#Replaces the TS number of rows with the rows in total.
	passes_ts['lar_entries'] = len(new_lar.index)

	#Changes the file to the institution features specified in the configuration file. 
	new_ts, new_lar = utils.change_bank(ts_data=passes_ts, lar_data=new_lar, 
		new_bank_name=bank_name, new_lei=lei, new_tax_id=tax_id)

	#Writes the file to the output filepath specified in the configuration file. 
	utils.write_file(ts_input=new_ts, lar_input=new_lar,
		path=output_filepath, name=output_filename)

	#Prints a statement indicating that the file has been creating in the specified
	#filepath. 

	print("New File Created in {output_filepath}".format(output_filepath=output_filepath))
		