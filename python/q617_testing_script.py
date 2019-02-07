#This script creates a test file for Q617, using the row_by_row_modification
#function in utils. The row_by_row_modification_yaml file is used with the function
#to make modifications to a file specifying rows, columns, and values.

#The resulting file is placed in the edits_files directory under
# "../edits_files/Q617_testing/".

#The following code imports the utils package.
import utils

#Stores a filepath for a clean test file. 
filepath = "../../hmda-platform/data/clean_test_files/bank_0/"

#Stores a filename for the clean test file. 
filename = "clean_file_100_rows_Bank0_syntax_validity.txt"

#Loads TS and LAR data from the clean file. 
ts_df, lar_df = utils.read_data_file(path=filepath, data_file=filename)

#Drops LAR rows with loan amount, property value, or CLTV as "Exempt" or "NA"
lar_df = lar_df[(lar_df['loan_amount'] != 'Exempt') &
                (lar_df['loan_amount'] != 'NA') &
                (lar_df['property_value'] != 'Exempt') &
                (lar_df['property_value'] != 'NA') & 
                (lar_df['cltv'] != 'Exempt') &
                (lar_df['cltv'] != 'NA')]

#Creates a five line file for each line in the row by row modification yaml.
lar_df, ts_df = utils.new_lar_rows(row_count=5, lar_df=lar_df, ts_df=ts_df)

#Modifies the file based on the row by row modification yaml.
lar_df = utils.row_by_row_modification(lar_df)

#Stores the file path for the resulting file. 
output_filepath = "../edits_files/Q617_testing/"

#Stores the file name for the resulting file. 
output_filename = "Q617_testing.txt"

#Writes a file to the filename and path. 
utils.write_file(path=output_filepath, ts_input=ts_df, 
    lar_input=lar_df, name=output_filename)

#Outputs print statements indicating the number of LAR, the filename, 
#and the filepath.
print("Row count is " + str(len(lar_df)) + " for " + str(output_filename))
print(str(output_filename) + " is stored in " + str(output_filepath))
