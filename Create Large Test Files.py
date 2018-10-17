#!/usr/bin/env python
# coding: utf-8

# # Creating Large HMDA Submission Test Files
# 
# This notebook demonstrates a function for creating large HMDA submission test files using 1000 row clean files for bank 1 and bank 0. The function concatenates the files together, creates unique Universal Loan Identifiers (ULIs) with a check digit, and generates a submission file with a specified number of LAR rows. 

# In[280]:


#The following code imports the required packages.

import json
import os
import pandas as pd
import random
import string
import time
import yaml
import numpy as np


# In[281]:


#The function below generates a random character string with a given length to create loan identifiers.
def char_string_gen(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

#This function returns a check digit for a given character string. 
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
		'A':10, 'H':17,'O':24,'V':31,'B':11,'I':18,'P':25,'W':32,'C':12,'J':19,'Q':26,'X':33,'D':13,'K':20,'R':27,'Y':34,
		'E':14,'L':21,'S':28,'Z':35,'F':15,'M':22,'T':29,'G':16,'N':23,'U':30}
		
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

#This function checks whether character strings in a column are unique to each other. 
#When column strings are unique, the function returns a "Passed" statement.
#If they are not, it returns a "Failed" statement. 
def uli_check(df=None):
    
    """
    This function passes in a single column dataframe to determine whether values within the column
    are unique. 
    
    The function returns a "Passed" statement if they are, and returns a "Failed" statement if the values
    are not unique. 
    """
    
    df['unique'] = df
    if len(df['unique'].unique()) == len(df.index): #Checks whether column values are unique. 
        statement = "Unique Values: Passed"
    else: 
        statement = "Unique Values: Failed"
    print(statement)
    return df.drop('unique', axis = 1) #Drops the unique values column. 
    print(df)


# ### Creating Clean Test Files
# 
# The following defines a function that creates clean test files. The function uses 1000 row clean test files located in the repository for Bank 0 and Bank 1 to duplicate LAR data to produce data with a desired number of rows, and provide unique ULI's for each row. Test files may be created with rows as multiples of 1000. 

# In[299]:


def large_clean_test_files(bank=None, file=file, count=None):
    
    """
    Creates clean HMDA submission test files in multiples of 1000, specified by the count variable. 
    The function requires a count, and a specification for the test bank, either '0' or '1.'
    
    The function replicates LAR data from two clean test files in the repository.
    """
   #Checks whether the count is a multiple of 1000.  
    if (count % 1000) != 0:
        statement = "Please specify a count in a multiple of 1000"
        return print(statement)
    #Establishes the case for bank = 0. 
    if bank == 0:
        file = "clean_file_1000_rows_Bank0.txt" 
        with open(file, 'r+' ) as f: #Opens the 1000 row file for Bank 0. 
            ts_row = f.readline() #Reading in the first row as the Transmittal Sheet submission. 
            lar_rows = f.readlines() #Reading in the other rows as the LAR submission.  
        with open("edits_files/lar_rows.txt", 'w') as out_lar: #Writes a file of LAR data. 
            out_lar.writelines(lar_rows)
        with open("edits_files/ts_row.txt", 'w') as out_ts: #Writes a file of TS data. 
            out_ts.writelines(ts_row)
        with open('schemas/lar_schema.json') as d: #Loads in the schema for the LAR file as a dataframe. 
            data = json.load(d)
            data = pd.DataFrame(data)

        #Reads in the LAR data as a dataframe, as object values without converting NA values to 
        #Not a Number Values. 
        df = pd.read_csv('edits_files/lar_rows.txt', delimiter = "|", header = None, dtype = 'object',
                         keep_default_na=False)
        df.columns = data['field'] #Takes the field names from the LAR schema as column names. 
        
        #Concatenates data to produce the desired number of rows in a new LAR dataframe. 
        df = pd.concat([df]*int((count/1000)), ignore_index = True) 
        
        #Creates a list of unique ULI's for Bank 0, and checks to determine that ULI's are unique.
        uli_1 = {'uli':list(['B90YWS6AFX2LGWOXJ1LD']*int((count)))}
        df1 = pd.DataFrame(uli_1)
        df1["uli"] = df1.apply(lambda x: x.uli + char_string_gen(23), axis = 1)
        df1['uli'] = df1.apply(lambda x: x.uli + check_digit_gen(ULI = x.uli), axis = 1)
        uli_check(df1)

        #Replaces ULI's in the new LAR dataframe with the unique ULI's.  
        df['uli'] = df1['uli']
        
        #Creates a new LAR csv file with the new LAR data with unique ULI's. 
        df.to_csv("lar_" + str(count) + ".txt", sep = "|", index = False, header= None)
        
        #The following appends the new LAR data into the TS file created earlier. 
        #The new file is renamed "clean_file_(count)_row_Bank0.txt."
        #New clean files are placed in the "edits_files/clean_files/bank0/" directory.
        filepath = "edits_files/clean_files/bank0/"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open("lar_" + str(count) + ".txt", 'r' ) as f:
            lar_count = f.readlines()

        with open("edits_files/ts_row.txt", 'a') as append_lar:
            append_lar.writelines(lar_count)

        os.remove("lar_" + str(count) + ".txt")
        os.rename("edits_files/ts_row.txt", "edits_files/clean_files/bank0/clean_file_" + 
                         str(count) + "_rows_Bank0.txt")
        return print(str("{:,}".format(count)) + " Row File Created for Bank " + str(bank))

    #Establishes the case for bank = 1.
    elif bank == 1:
        file = "clean_file_1000_rows_Bank1.txt" #Opens the 1000 row file for Bank 1. 
        with open(file, 'r' ) as f:
            ts_row = f.readline() #Reading in the first row as the Transmittal Sheet submission. 
            lar_rows = f.readlines() #Reading in the other rows as the LAR submission.
        with open("edits_files/lar_rows.txt", 'w') as out_lar: #Writes a file of LAR data.
            out_lar.writelines(lar_rows) 
        with open("edits_files/ts_row.txt", 'w') as out_ts: #Writes a file of TS data. 
            out_ts.writelines(ts_row)
        with open('schemas/lar_schema.json') as d: #Loads in the schema for the LAR file as a dataframe.
            data = json.load(d)
            data = pd.DataFrame(data)

        #Reads in the LAR data as a dataframe, as object values without converting NA values to 
        #Not a Number Values. 
        df = pd.read_csv('edits_files/lar_rows.txt', delimiter = "|", header = None, dtype = 'object',
                         keep_default_na=False)
        df.columns = data['field']
        
        #Concatenates data to produce the desired number of rows in a new LAR dataframe. 
        df = pd.concat([df]*int((count/1000)), ignore_index = True)  

        #Creates a list of unique ULI's for Bank 1, and checks to determine that ULI's are unique.
        uli_1 = {'uli':list(['BANK1LEIFORTEST12345']*int((count)))}
        df1 = pd.DataFrame(uli_1)
        df1["uli"] = df1.apply(lambda x: x.uli + char_string_gen(23), axis = 1)
        df1['uli'] = df1.apply(lambda x: x.uli + check_digit_gen(ULI = x.uli), axis = 1)
        uli_check(df1)
        
        #Replaces ULI's in the new LAR dataframe with the unique ULI's.  
        df['uli'] = df1['uli']
        
        #Creates a new LAR csv file with the new LAR data with unique ULI's. 
        df.to_csv("lar_" + str(count) + ".txt", sep = "|", index = False, header= None)

        #The following appends the new LAR data into the TS file created earlier. 
        #The new file is renamed "clean_file_(count)_row_Bank1.txt."
        #New clean files are placed in the "edits_files/clean_files/bank1/" directory.
        
        filepath = "edits_files/clean_files/bank1/"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open("lar_" + str(count) + ".txt", 'r' ) as f:
            lar_count = f.readlines()

        with open("edits_files/ts_row.txt", 'a') as append_lar:
            append_lar.writelines(lar_count)

        os.remove("lar_" + str(count) + ".txt")
        os.rename("edits_files/ts_row.txt", "edits_files/clean_files/bank1/clean_file_" + 
                         str(count) + "_rows_Bank1.txt")
        return print(str("{:,}".format(count)) + " Row File Created for Bank " + str(bank))

    else:
        statement = "Please list bank as '0' or '1'"
        return print(statement)
        
    


# In[300]:


large_clean_test_files(bank = 1, count = 3000)


# ### Creating Clean Test Files With Specified Counts in a List
# A loop may be used to create clean large test files with the counts in a list. 

# In[303]:


counts = [1000, 5000, 10000, 50000, 100000]

for count in counts:
    large_clean_test_files(bank = 0, count = count)


# In[304]:


counts = [1000, 5000, 10000, 50000, 100000]

for count in counts:
    large_clean_test_files(bank = 1, count = count)

