#This file contains helper functions used by one or more classes 
#in order to generate clean and failing synthetic data files.

#Imports the necessary libraries.
import math
import json
import os
import random
import string
import pandas as pd
import yaml
import utils

state_codes = {'WA':'53', 'WI':'55', 'WV':'54', 'FL':'12', 'WY':'56', 
'NH':'33', 'NJ':'34', 'NM':'33', 'NC':'37', 'ND':'38', 'NE':'31', 'NY':'36', 
'RI':'44', 'NV':'32', 'CO':'08', 'CA':'06', 'GA':'13', 'CT':'09', 'OK':'40', 
'OH':'39', 'KS':'20', 'SC':'45', 'KY':'21', 'OR':'41', 'SD':'46', 'DE':'10', 
'HI':'15', 'PR':'43', 'TX':'48', 'LA':'22', 'TN':'47', 'PA':'42', 'VA':'51', 
'VI':'78', 'AK':'02', 'AL':'01', 'AR':'05', 'VT':'50', 'IL':'17', 'IN':'18',
'IA':'19', 'AZ':'04', 'ID':'16', 'ME':'23', 'MD':'24', 'MA':'25', 'UT':'49', 
'MO':'29', 'MN':'27', 'MI':'26', 'MT':'30', 'MS':'29', 'DC':'11'}

def write_file(path=None, ts_input=None, lar_input=None, name="test_file.txt"):
	"""
	Takes a TS row and LAR data as dataframes. Writes LAR data to file and
	re-reads it to combine with TS data to make a full file.

	ts_input: DataFrame of a TS row
	lar_input: DataFrae of one or more LAR rows
	"""
	
	parts_dir = "../edits_files/file_parts/"
	
	#make directories for files if they do not exist
	if not os.path.exists(path):
		os.makedirs(path)

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


def read_data_file(path, data_file, lar_schema=None, ts_schema=None):
	"""
	Reads a complete file (includes LAR and TS rows) into a pandas 
	dataframe and returns them.
	"""
	if lar_schema is None:
		lar_schema = pd.DataFrame(json.load(open("../schemas/lar_schema.json", "r")))
	if ts_schema is None:
		ts_schema = pd.DataFrame(json.load(open("../schemas/ts_schema.json", "r")))
	

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
			ts_df = pd.DataFrame(data=ts_data, dtype=object, columns=ts_schema.field)
			lar_df  = pd.DataFrame(data=lar_data, dtype=object, columns=lar_schema.field)

			return ts_df, lar_df
	else:
		raise ValueError("A data file must be passed.")

def unique_uli(new_lar_df=None, lei=None):
    """
    Generates a set of unique ULI's for a LAR dataframe.
    """

    #Copy over ULIs with the LEI
    new_lar_df["uli"] = new_lar_df["uli"].apply(lambda x: lei)  
    
    #Generates a loan ID as a random 23-character string for each LEI
    new_lar_df["uli"] = new_lar_df["uli"].apply(lambda x: x + utils.char_string_gen(23)) 
    
    #Adds a check digit to each ULI
    new_lar_df['uli'] = new_lar_df["uli"].apply(lambda x: x + utils.check_digit_gen(ULI=x))

    #If ULIs are duplicated, the unique_uli function is applied again.  
    #FIXME: remove recursion and replace with nexted loops:
    	#for loop for length of new lar file size
    	#while loop to create new ULIs and check against an established list for duplication
    if len(new_lar_df['uli']) > len(set(new_lar_df['uli'])):
        print("Re-Running")
        self.unique_uli(new_lar_df)
    else:
        print("Unique ULIs Assigned")

    return new_lar_df

def new_lar_rows(final_row_count=None, lar_df=None, ts_df=None):
    """
    Returns LAR with a specified number of rows. 
    Returns TS data with updated lar entries.
    final_row_count is the LAR record count of the output file
    new rows are copied from existing rows and given new ULIs with the unique_uli() function
    """

    #Stores the LAR dataframe as a new LAR dataframe. 
    if len(lar_df) <=0:
    	print("LAR data has 0 rows")
    	return

    new_lar_df = lar_df.copy()
    print(final_row_count, "target rows")
    #Stores the number of rows currently in the dataframe to calculate the new number of rows to concatenate. 
    current_row_count = len(new_lar_df.index) 
    print(len(new_lar_df), "lar records in new rows")
    #Calculates a multiplier taking the ceiling function of the desired row count over the current row count.
    multiplier = math.ceil(final_row_count/current_row_count)
    print(multiplier, "mult")
    #Concatenates data to produce the number of rows by the multiplier in a new LAR dataframe. 
    new_lar_df = pd.concat([new_lar_df]*int(multiplier))
    
    #Drops the number of rows to the count specified. 
    #FIXME: reset index and drop anything with index over desired row count
    new_lar_df = new_lar_df[:final_row_count]
    
    #Applies the unique_uli function to the new LAR dataframe 
    #to generate a unique set of ULIs. 
    new_lar_df = utils.unique_uli(new_lar_df=new_lar_df, lei=ts_df.iloc[0][14])

    #Modifies TS data for the new number of LAR entries.
    ts_df["lar_entries"] = len(new_lar_df)

    return (ts_df, new_lar_df)

def row_by_row_modification(lar_df, yaml_filepath='configurations/row_by_row_modification.yaml'):
	"""
	Uses the inputs from the row_by_row modification yaml to modify a dataframe
	"""

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
					
def change_bank(ts_data=None, lar_data=None, new_bank_name=None, new_lei=None, new_tax_id=None):
	"""
	Takes in TS and LAR data of one bank and outputs the same TS and LAR data with specifications 
	for a different bank in the function call. 
	The elements changed are Bank Name in the TS row, LEI in the TS row and the  
	LAR rows, and Tax ID in the TS row. 
	ULI's are generated with the new LEI.
	"""

	#Stores original Bank Name.
	orig_bank_name = ts_data.iloc[0][1] 

	#Changes TS Data to new institution specifications. 
	ts_data["inst_name"] = new_bank_name
	ts_data["tax_id"] = new_tax_id
	ts_data["lei"] = new_lei

	#Changes LAR Data to new institution specifications.
	lar_data["lei"] = new_lei

	#Runs a new set of unique ULI's 
	lar_data = utils.unique_uli(new_lar_df = lar_data, lei = new_lei)

	#Implementing S304 compliance. 
	ts_data["lar_entries"] = len(lar_data.index)

	#Returning a new set of TS and LAR data with a print statement. 
	print("Data for " + str(orig_bank_name) + " has been changed to specifications for  " + str(new_bank_name))
	
	return (ts_data, lar_data)

def char_string_gen(length):
	"""Generates a string of chosen length using ascii uppercase and numerical characters"""
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def check_digit_gen(valid=True, ULI=None):
	"""Generates a check digit for a ULI in accordance with
	https://www.consumerfinance.gov/eregulations/diff/1003-C/2015-26607_20170101/2015-26607_20180101?from_version=2015-26607_20170101#1003-C-1"""
	if ULI is None:
		raise ValueError("a ULI must be supplied")
	#GENERATING A CHECK DIGIT
	#Step 1: Starting with the leftmost character in the string that consists of the combination of the
	#Legal Entity Identifier (LEI) pursuant to § 1003.4(a)(1)(i)(A) and the additional characters identifying the
	#covered loan or application pursuant to § 1003.4(a)(1)(i)(B), replace each alphabetic character with numbers
	#in accordance with Table I below to obtain all numeric values in the string.
	
	
	#1: convert letters to digits
	#2: append '00' to right of string
	#3:Apply the mathematical function mod=(n, 97) where n= the number obtained in step 2 above and 97 is the divisor.
	#3a: Alternatively, to calculate without using the modulus operator, divide the numbers in step 2 above by 97.
	#   Truncate the remainder to three digits and multiply it by .97. Round the result to the nearest whole number.
	#4: Subtract the result in step 3 from 98. If the result is one digit, add a leading 0 to make it two digits.
	#5: The two digits in the result from step 4 is the check digit. Append the resulting check digit to the
	#   rightmost position in the combined string of characters described in step 1 above to generate the ULI.
	
	#digit_vals contains the conversion of numbers to letters
	digit_vals = {
	'A':10, 'H':17,'O':24,'V':31,'B':11,
	'I':18,'P':25,'W':32,'C':12,'J':19,
	'Q':26,'X':33,'D':13,'K':20,'R':27,
	'Y':34, 'E':14,'L':21,'S':28,'Z':35,
	'F':15,'M':22,'T':29,'G':16,'N':23,'U':30}
	
	uli_chars = list(ULI)
	mod_uli_chars = []
	for char in uli_chars:
		if char.upper() in digit_vals.keys():
			mod_uli_chars.append(str(digit_vals[char.upper()]))
		else:
			mod_uli_chars.append(char)
	mod_uli_chars.append('00') 
	digit_base = int("".join(mod_uli_chars))
	digit_modulo = digit_base % 97
	check_digit = 98 - digit_modulo

	if valid:
		return str(check_digit).zfill(2) #left pad check digit with 0 if length is less than 2
	else:
		return str(check_digit+6).zfill(2)[:2] #return a bad check digit (used in edit testing)

def validate_state_codes(path, lar_file):
	"""Parses through an existing test file and replaces the state code 
	abbreviation with one that maps to the FIPS state code indicated 
	in the census tract field."""

	#Seperates LAR and TS Data.
	ts_data, lar_data = utils.read_data_file(path=path, data_file=test_file)

	print(len(lar_data.columns))

	if len(lar_data.columns) !=110:
		print("Not the right number of columns")
		print("Number of columns is " + str(len(lar_data.columns)))

	#Loads the geographic file configuration.
	with open('configurations/geographic_data.yaml') as f:
		# Uses safe_load instead of load.
		geographic = yaml.safe_load(f) 

	#Iterrates through each row in the LAR data. 
	for index, row in lar_data.iterrows():
		print(row.state)
		if row.state != 'NA':
			#Assigns the state code abbreviation key from the FIPS state code value to the row's
			#state code field. 
			print("The census tract is " + row['tract'])
			print("Original value is " + row['state'])
			print("New state is " + geographic['state_FIPS_to_abbreviation'][row['tract'][0:2]])
			row['state'] = geographic['state_FIPS_to_abbreviation'][row['tract'][0:2]]
			print("Changed value is " + row['state'])

	#Prints a statement when the process is complete. 
	print("Validating State Code Abbreviations")

	#Writes file back to the original path. 
	utils.write_file(path=path, ts_input=ts_data, lar_input=lar_data, name=test_file)

	#Prints a statement when the file is re-written. 
	print("File rewritten to " + path)


