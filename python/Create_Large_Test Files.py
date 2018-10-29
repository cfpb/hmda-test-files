#!/usr/bin/env python
# coding: utf-8

# # Creating Large HMDA Submission Test Files
# 
# This notebook demonstrates a class for creating large HMDA submission test files.

# In[148]:


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


# ### Creating Clean Test Files
# 
# The following defines a function that creates clean test files. It uses an existing clean file to create a new clean file of any row count. This set of functions is from the Clean_Files class defined below. An existing clean test file can be separated into its Transmittal Sheet and LAR components, using the Clean_Files class function separate_lar_ts. 

# In[143]:


cf = Clean_Files()
cf.separate_lar_ts(file = "../edits_files/file_parts/clean_file_1000_rows_Bank1.txt")


# ### Creating Clean Test Files With Specified Counts in a List
# A loop may be used to create clean large test files with the counts in a list. 

# In[147]:


rows = [297]

for row in rows:
    ts_file = "../edits_files/file_parts/ts_data.txt" #Stores the file path for TS data as ts_file. 
    lar_file = "../edits_files/file_parts/lar_data.txt" #Stores the file path for LAR data as lar_file.
    df = cf.get_rows(lar_file = lar_file, row_count = row)
    df = cf.assign_uli(df=df, ts_file = ts_file)
    cf.lar_to_hmda_file(ts_file=ts_file, lar_rows_df=df)


# In[136]:


class Clean_Files(object):
    def separate_lar_ts(self, file=None):  
        """
         Separates a clean file into Transmittal Sheet (TS) and Loan Application Register (LAR) data.
         Saves the LAR data and TS data as text files in the /edits_files/file_parts/ directory. 
        
        """
        with open(file, 'r+' ) as f: #Opening the submission file. 
            ts_row = f.readline() #Reading in the first row as the TS submission. 
            lar_rows = f.readlines() #Reading in the other rows as the LAR submission.  
        with open("../edits_files/file_parts/lar_data.txt", 'w') as out_lar: #Writes a file of LAR data. 
            out_lar.writelines(lar_rows)
        with open("../edits_files/file_parts/ts_data.txt", 'w') as out_ts: #Writes a file of TS data. 
            out_ts.writelines(ts_row)
        
        #Prints the location of each data file. 
        statement = """
           LAR file saved as: "../edits_files/file_parts/lar_data.txt", 
           TS  file saved as: "../edits_files/file_parts/ts_data.txt" 
           """
        
        print(statement)
        return
            
    
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
         
    
    def assign_uli(self, df=None, ts_file=None,):
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
        
    def lar_to_hmda_file(self, lar_rows_df=None, ts_file=None):
        
        """
        Creates a HMDA submission file, passing in a dataframe of LAR rows, and the TS file. 
        
        """
        
        #Store the number of rows in the lar_rows dataframe. 
        row_count = len(lar_rows_df.index)
        
        #Replaces the lar_data text file with the lar_rows dataframe.
        lar_rows_df.to_csv("../edits_files/file_parts/lar_data.txt", sep="|", index=False, header=None)


        #Reads in TS file.
        ts_df = pd.read_csv(ts_file, delimiter="|", header=None, dtype='object',
                         keep_default_na=False)
        
        #Stores the second column of the TS file as 'bank'. 
        bank = ts_df.iloc[0][1]
        
        #Creates a new file path to place the new HMDA submission file. 
        filepath = "../edits_files/clean_files/" + bank + "/clean_file_" + str(row_count) + "_rows_" + str(bank) + ".txt"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        #Copies the TS text file into the filepath above and renames it. 
        sh.copyfile(ts_file, filepath)
        
        #Reads in lar_data text file and appends it to the Transmittal Sheet row in the new file. 
        with open("../edits_files/file_parts/lar_data.txt", 'r' ) as f:
            new_lars = f.readlines()

        with open(filepath, 'a') as append_lar:
            append_lar.writelines(new_lars)

        
        #Prints out a statement with the number of rows created, and the location of the new file. 
        statement1 = str("{:,}".format(row_count)) + " Row File Created for " + str(bank)
        statement2 = "File Path: " + str(filepath)
    
        print(statement1)
        print(statement2)
        
        return

