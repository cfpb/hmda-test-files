#This file contains helper functions used by one or more classes 
#in order to generate clean and failing synthetic data files.

#Imports the necessary libraries.
import math
import json
import os
import pandas as pd
from large_test_files import unique_uli
import yaml
import utils

#Imports lar_gen class to support the unique_uli function. 
from lar_generator import lar_gen 

#Instantiates lar_gen class as lar_gen. 
lar_gen = lar_gen() 

state_codes = {'WA':'53', 'WI':'55', 'WV':'54', 'FL':'12', 'WY':'56', 
'NH':'33', 'NJ':'34', 'NM':'33', 'NC':'37', 'ND':'38', 'NE':'31', 'NY':'36', 
'RI':'44', 'NV':'32', 'CO':'08', 'CA':'06', 'GA':'13', 'CT':'09', 'OK':'40', 
'OH':'39', 'KS':'20', 'SC':'45', 'KY':'21', 'OR':'41', 'SD':'46', 'DE':'10', 
'HI':'15', 'PR':'43', 'TX':'48', 'LA':'22', 'TN':'47', 'PA':'42', 'VA':'51', 
'VI':'78', 'AK':'02', 'AL':'01', 'AR':'05', 'VT':'50', 'IL':'17', 'IN':'18',
'IA':'19', 'AZ':'04', 'ID':'16', 'ME':'23', 'MD':'24', 'MA':'25', 'UT':'49', 
'MO':'29', 'MN':'27', 'MI':'26', 'MT':'30', 'MS':'29', 'DC':'11'}

def write_file(path=None, ts_input=None, lar_input=None, name="test_file.txt"):
	"""Takes a TS row and LAR data as dataframes. Writes LAR data to file and
	re-reads it to combine with TS data to make a full file."""
	#make directories for files if they do not exist
	if not os.path.exists(path):
		os.makedirs(path)
	#check existence of file parts directory
	parts_dir = "../edits_files/file_parts/"
	if not os.path.exists(parts_dir):
		os.makedirs(parts_dir)

	#write TS dataframe to file
	ts_input.to_csv(parts_dir + "ts_data.txt", sep="|", header=False, 
		index=False, index_label=False)
	#write LAR dataframe to file
	lar_input.to_csv(parts_dir + "lar_data.txt", sep="|", header=False, 
		index=False, index_label=False)
	#load LAR data as file rows
	with open(parts_dir + "lar_data.txt", 'r') as lar_data:
		lar = lar_data.readlines()
	with open(parts_dir + "ts_data.txt", "r") as ts_data:
		ts  = ts_data.readline()
	with open(path + name, 'w') as final_file:
		final_file.write(ts)
		for line in lar:
			final_file.write("{line}".format(line=line))

def read_data_frames(ts_df=None, lar_df=None):
	"""Receives two pandas dataframes (one TS and one LAR) and stores 
	them as class objects."""
	if ts_df is not None:
		self.ts_df = ts_df
	if lar_df is not None:
		self.lar_df = lar_df
	if ts_df is None and lar_df is None:
		raise ValueError("No data passed.\nNo data written to object.")

def read_data_file(path="", data_file=None):
	"""Reads a complete file (includes LAR and TS rows) into a pandas 
	dataframe and returns them."""
	ts_schema = pd.DataFrame(json.load(open("../schemas/ts_schema.json", "r")))
	lar_schema = pd.DataFrame(json.load(open("../schemas/lar_schema.json", "r")))
	if data_file is not None:
		with open(path+data_file, 'r') as infile:
			#split TS row from file
			ts_row = infile.readline().strip("\n")
			ts_data = []
			ts_data.append(ts_row.split("|"))
			#split LAR rows from file
			lar_rows = infile.readlines()
			lar_data = [line.strip("\n").split("|") for line in lar_rows]
			#create dataframes of TS and LAR data
			ts_df = pd.DataFrame(data=ts_data, dtype=object, 
				columns=ts_schema.field)
			lar_df  = pd.DataFrame(data=lar_data, dtype=object, 
				columns=lar_schema.field)
			return (ts_df, lar_df)
	else:
		raise ValueError("A data file mus be passed. No data have been written to the object")

def unique_uli(new_lar_df=None, lei=None):
    """
    Generates a set of unique ULI's for a LAR dataframe.
    """

    #Copying over ULIs with the LEI.
    new_lar_df["uli"] = new_lar_df["uli"].apply(lambda x: 
        lei)  
    
    #Generates a loan ID as a random 23-character 
    #string for each LEI.
    new_lar_df["uli"] = new_lar_df["uli"].apply(lambda x: x + 
        lar_gen.char_string_gen(23)) 
    
    #Adds a check digit to each.
    new_lar_df['uli'] = new_lar_df["uli"].apply(lambda x: x + 
        lar_gen.check_digit_gen(ULI=x))

    #If ULIs are duplicated, the unique_uli function 
    #is applied again.  
    if len(new_lar_df['uli']) > len(set(new_lar_df['uli'])):
        print("Re-Running")
        self.unique_uli(new_lar_df)
    else:
        print("Unique ULIs Assigned")

    return new_lar_df

def new_lar_rows(row_count=None, lar_df=None, ts_df=None):
    """
    Returns LAR with a specified number of rows. 
    Returns TS data with updated lar entries.
    """

    #Stores the LAR dataframe as a new LAR dataframe. 
    new_lar_df = lar_df

    #Stores the number of rows currently in the dataframe to calculate the 
    #new number of rows to concatenate. 
    current_row = len(new_lar_df.index) 
    
    #Calculates a multiplier taking the ceiling function of 
    #the desired row count over the current row count.
    multiplier = math.ceil(row_count/current_row)
    
    #Concatenates data to produce the number of rows 
    #by the multiplier in a new LAR dataframe. 
    new_lar_df = pd.concat([new_lar_df]*int(multiplier))
    
    #Drops the number of rows to the count specified. 
    if (row_count % current_row) != 0:
        drop_rows = current_row - (row_count % current_row)
        new_lar_df = new_lar_df[: - (drop_rows)]
    
    #Applies the unique_uli function to the new LAR dataframe 
    #to generate a unique set of ULIs. 
    new_lar_df = utils.unique_uli(new_lar_df=new_lar_df, 
    	lei=ts_df.iloc[0][14])

    #Modifies TS data for the new number of LAR entries.
    ts_df["lar_entries"] = len(new_lar_df)

    return (new_lar_df, ts_df)

def row_by_row_modification(lar_df, yaml_filepath='row_by_row_modification.yaml'):
	"""Uses the inputs from the row_by_row 
	modification yaml to modify a dataframe"""

	#Opens the yaml_file. 
	yaml_file = yaml_filepath
	with open(yaml_file, 'r') as f:
		row_by_row = yaml.safe_load(f)
	
	#Runs through each case in the file. 
	#Modifies values for each column in a row specified in the yaml file. 
	for case in row_by_row:
		for column in row_by_row[case]["columns"]:
			for key in column:
				lar_df.at[row_by_row[case]["row"], str(key)] = column[key]

	return lar_df
					
def change_bank(ts_data=None, lar_data=None, new_bank_name=None, 
	new_lei=None, new_tax_id=None):
	"""Takes in TS and LAR data of one bank and outputs
	the same TS and LAR data with specifications for a different
	bank in the function call."""

	#Stores original bank name.
	orig_bank_name = ts_data.iloc[0][1]
	#print(orig_bank_name) 

	#Changes TS Data to new institution specifications. 
	ts_data["inst_name"] = new_bank_name
	ts_data["tax_id"] = new_tax_id
	ts_data["lei"] = new_lei

	#Changes LAR Data to new institution specifications.
	lar_data["lei"] = new_lei

	#Runs a new set of unique ULI's 
	lar_data = unique_uli(new_lar_df = lar_data, lei = new_lei)

	#Implementing S304 compliance. 

	ts_data["lar_entries"] = len(lar_data.index)

	#Returning a new set of TS and LAR data with a print statement. 

	print("Data for " + str(orig_bank_name) + " has been changed to specifications for  " + str(new_bank_name))
	
	return (ts_data, lar_data)


