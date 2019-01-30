#The following code imports the required packages.
import math
import json
import os
import pandas as pd
import random
import string
import time
import yaml
import shutil as sh
import utils

from large_test_files import unique_uli

"""
This script creates 5 files for testing the Q617 edit with the same
loan amount, property value, and CLTV. Each file has CLTV rounded 
to a different value. Each file has loan amounts and property values 
rounded to either 0, 1, or two decimal places. 

CLTV is calculated by dividing loan amount by the property value for each row
and rounding to the place specified in the filename. 

"""

def passes_cltv(cltv_rounded = 0, row=None):
    """Creates CLTV values from loan amount
    and property value"""
    
    #Divides loan amount by provery value.
    ltv = row['loan_amount']/row['property_value']
    
    #Calculates CLTV by rounding LTV to a place specified in the function.
    cltv = round(ltv, cltv_rounded)
    return cltv


def cltv_passes_all_setup(lar_data=None, ts_data=None, row_count=None):
    """Creates 5 files that should pass Q617"""

    #Stores random floats for loan_amount and property_value. 
    loan_amount = random.uniform(100000, 1000000)
    property_value = random.uniform(100000, 1000000)

    #Creates empty lists for storing the same values rounded to different places. 
    loan_amount_lst = []
    property_value_lst = []

    #Stores loan amount and property value in the list above, rounded to either
    #0, 1, or 2 decimal places. 
    
    for i in [0, 1, 2]:
        loan_amount_lst.append(round(loan_amount, i))
    #print(loan_amount_lst)

    for i in [0, 1, 2]:
        property_value_lst.append(round(property_value, i))
    #print(property_value_lst)


    #Iterates over 0-4 decimal places for CLTV values. 
    for i in [0, 1, 2, 3, 4]:
        #Iterates over each dataframe row to place a property value, 
        #a loan amount and a calculated CLTV. 
        for index, row in lar_data.iterrows():
            row['property_value'] = random.choice(property_value_lst)
            row['loan_amount'] = random.choice(loan_amount_lst)
            row['cltv'] = passes_cltv(cltv_rounded = i, row=row)

        #Stores the LAR dataframe as a new LAR dataframe. 
        new_lar_df = lar_data

        #Stores the number of rows currently in the dataframe.
        current_row = len(new_lar_df.index) 
        
        """Calculates a multiplier taking the ceiling function of 
        the desired row count over the current row count.""" 
        multiplier = math.ceil(row_count/current_row)
        
        """Concatenates data to produce the number of rows 
        by the multiplier in a new LAR dataframe."""  
        new_lar_df = pd.concat([new_lar_df]*int(multiplier))
        
        #Drops the number of rows to the count specified. 
        if (row_count % current_row) != 0:
            drop_rows = current_row - (row_count % current_row)
            new_lar_df = new_lar_df[: - (drop_rows)]
        
        """Applies the unique_uli function from large_test_files 
        to the new LAR dataframe to generate a unique set of ULIs."""  
        new_lar_df = unique_uli(new_lar_df, ts_data['lei'])

        #Modifies TS data for the new number of LAR entries.
        ts_data["lar_entries"] = len(new_lar_df)

        #Writes a Q617 file with CLTV rounded to i places. 
        
        utils.write_file(path="../edits_files/q617_testing/", ts_input=ts_data, 
            lar_input=new_lar_df, name="test_file_cltv_"+str(i)+"_decimals.txt")

        #Prints a statement indicating that a file has been created with a certain
        #number of rows and CLTV rounded to i decimal places. 
        print("Row count is " + str(len(new_lar_df)) + " for cltv rounded to "+str(i)+" decimal places.")

#Stores a filepath for a clean test file, passing syntax and validity. 
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

#Initiates the function for creating Q617 test files. 
new_lar_df = cltv_passes_all_setup(lar_data = lar_df, ts_data=ts_df, row_count=100)

