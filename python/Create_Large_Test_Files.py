#!/usr/bin/env python
# coding: utf-8

# # Creating Custom Row HMDA Submission Test Files
# 
# This notebook demonstrates a class for creating custom row HMDA submission test files.

# In[82]:


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

from lar_generator import lar_gen #Imports lar_gen class. 
lg = lar_gen() #Instantiates lar_gen class as lg. 


# ### Custom_Test_Files Class
# 
# The following demonstrates a function from the Custom_Test_Files class that creates test files with a custom number of rows. The class is instantiated with an existing file to create a new file with a specified row count. This set of functions is from the Custom_Test_Files class defined below.

# In[85]:


#The class is instantiated with an existing clean file
cf = Custom_Test_Files(filename = "../edits_files/file_parts/clean_file_1000_rows_Bank1.txt")
cf.create_file(row_count=4000, save_file = "../edits_files/new_files/clean_file_4000_rows_Bank1.txt" )


# In[84]:


class Custom_Test_Files(object):
    
    """Returns a Custom_Tesst_Files object with a set of functions and parameters to create submission files
    with a specified number of rows."""
    
    def __init__(self, filename):
        self.filename = filename #Instantiates a file to build 
        print("Custom_Test_Files Object Instantiated.")
            
    def create_file(self, row_count=None, save_file=None):
        """
        Creates a new custom file, passing in a row count and filepath to save the created file. 
    
        """
        ts_file = cf.separate_ts() #Stores the file path for TS data as ts_file. 
        lar_file = cf.separate_lar() #Stores the file path for LAR data as lar_file. 
        #Uses the get_rows function to create a dataframe of LAR and to add on the specified number of rows. 
        df = cf.get_rows(row_count=row_count, lar_file=lar_file) 
        #Uses the assign rows function to create unique ULI's. 
        df = cf.assign_uli(df=df, ts_file=ts_file)
        #Places the dataframe of LAR in a file with a TS row. 
        cf.lar_to_hmda_file(ts_file=ts_file, df=df, save_file=save_file)
    
    def separate_ts(self):  
        """
         Separates the Transmittal Sheet (TS) row from the submission file.
         Saves the TS data as text files in the /edits_files/file_parts/ directory. 
        
        """
        with open(self.filename, 'r+' ) as f: #Opening the submission file. 
            ts_row = f.readline() #Reading in the first row as the TS submission. 
            lar_rows = f.readlines() #Reading in the other rows as the LAR submission.  
        with open("../edits_files/file_parts/ts_data.txt", 'w') as out_ts: #Writes a file of TS data. 
            out_ts.writelines(ts_row)
            
        statement = """ TS file saved as: "../edits_files/file_parts/lar_data.txt" """
        ts_filepath = "../edits_files/file_parts/ts_data.txt"
        return ts_filepath #returns a string of the TS filepath.
    
    def separate_lar(self):
        with open(self.filename, 'r+' ) as f: #Opening the submission file. 
            ts_row = f.readline() #Reading in the first row as the TS submission. 
            lar_rows = f.readlines() #Reading in the other rows as the LAR submission.  
        with open("../edits_files/file_parts/lar_data.txt", 'w') as out_lar: #Writes a file of LAR data. 
            out_lar.writelines(lar_rows)
        
        #Prints the location of each data file. 
        statement = """LAR file saved as: "../edits_files/file_parts/lar_data.txt" """
        
        lar_filepath = "../edits_files/file_parts/lar_data.txt"
        return lar_filepath #returns a string of the LAR filepath.
    
    def get_rows(self, lar_file=None, row_count=None):
        """
        Returns a data frame of LAR data with a specified number of rows.
        
        """
        with open('../schemas/lar_schema.json') as d: #Loads in the schema for the LAR file as a dataframe. 
            headers = json.load(d)
            headers = pd.DataFrame(headers)
        #Reads in the data from lar_file. 
        df = pd.read_csv(lar_file, delimiter="|", header=None, dtype='object',
                         keep_default_na=False) 
        
        df.columns = headers['field'] #Takes the field names from the LAR schema as column names.
        
        current_row = len(df.index) #Number of rows currently in the dataframe. 

        #Calculates a multiplier taking the ceiling function of desired row count over current row count. 
        multiplier = math.ceil(row_count/current_row)
        
        #Concatenates data to produce the number of rows by the multiplier in a new LAR dataframe. 
        df = pd.concat([df]*int(multiplier))
        
        #Drops the number of rows to the row count specified. 
        
        if (row_count%current_row) == 0:
            return df
        else:
            drop_rows = current_row - (row_count%current_row)
            df = df[:-(drop_rows)]
            return df
         
    def assign_uli(self, df=None, ts_file=None):
        """
        Assigns new ULI's to a dataframe of lar rows, based on the bank number in the TS file. 
        
        """
        #Reads in ts_file.
        ts_df = pd.read_csv(ts_file, delimiter="|", header=None, dtype='object',
                         keep_default_na=False)
        
        #Stores the second column of the TS file as 'bank'. 
        bank = ts_df.iloc[0][1]
        
        #Assigns the number of rows in the dataframe to row_count. 
        df.reset_index()
        row_count = len(df.index)
        #Creates a new list of LEI's for the ULI column by bank.
        if bank == 'Bank0': 
            unique_lei_for_uli = {'uli':list(['B90YWS6AFX2LGWOXJ1LD']*int((row_count)))}
        
        if bank == 'Bank1':
            unique_lei_for_uli = {'uli':list(['BANK1LEIFORTEST12345']*int((row_count)))}
        
        uli_col = pd.DataFrame(unique_lei_for_uli) #Creates a dataframe of new ULI's.
        #Amends the ULI's by adding up to 23 additional characters. 
        uli_col['uli'] = uli_col.apply(lambda x: x.uli + lg.char_string_gen(length = 23), axis=1)
        #Adds a checkdigit to the end of the ULI. 
        uli_col['uli'] = uli_col.apply(lambda x: x.uli + lg.check_digit_gen(ULI=x.uli), axis=1)
        #Checks whether ULI's are unique using the uli_check function. 
        
        if self.uli_check(col = uli_col) is True:
            df['uli'] = uli_col['uli'] #If unique, ULI's in the dataframe are replaced. 
            print("Unique ULIs Assigned for " + str(bank))
            return df
        else: 
            #If not unique, the assign_uli function is re-run.
            print("Re-Running")
            assign_uli(self, ts_file=ts_file, df=df)  
    
    def uli_check(self, col=None):
        """
        Passes in a single column dataframe to determine whether values within the column
        are unique. 
        
        Returns a True statement if they are, and returns a False statement if not. 
        """
        col['unique'] = col
        if len(col['unique'].unique()) == len(col.index): #Checks whether column values are unique. 
            return True
        else: 
            return False
        
    def lar_to_hmda_file(self, df=None, ts_file=None, save_file=None):
        
        """
        Creates a HMDA submission file, passing in a dataframe of LAR rows, the TS file, and a filepath to store
        the file. 
        
        """
        
        #Store the number of rows in the lar_rows dataframe. 
        row_count = len(df.index)
        
        #Replaces the lar_data text file with the lar_rows dataframe.
        df.to_csv("../edits_files/file_parts/lar_data.txt", sep="|", index=False, header=None)


        #Reads in TS file.
        ts_df = pd.read_csv(ts_file, delimiter="|", header=None, dtype='object',
                         keep_default_na=False)
        
        #Stores the second column of the TS file as 'bank'. 
        bank = ts_df.iloc[0][1]
        
        #Creates a new file path to place the new HMDA submission file. 
        os.makedirs(os.path.dirname(save_file), exist_ok=True)
        
        #Copies the TS text file into the save filepath specified in the function and renames it. 
        sh.copyfile(ts_file, save_file)
        
        #Reads in lar_data text file and appends it to the Transmittal Sheet row in the new file. 
        with open("../edits_files/file_parts/lar_data.txt", 'r' ) as f:
            new_lars = f.readlines()

        with open(save_file, 'a') as append_lar:
            append_lar.writelines(new_lars)

        
        #Prints out a statement with the number of rows created, and the location of the new file. 
        statement1 = (str("{:,}".format(row_count)) + " Row File Created for " + str(bank) + 
                      " File Path: " + str(save_file))
    
        return print(statement1)

        

