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

#Instantiates lar_gen class as lar_gen. 
lar_gen = lar_gen() 

class CustomTestFiles(object):
    
    """
    Returns a CustomTestFiles class object to create submission files
    with a specified number of rows.
    """
    
    def __init__(self, old_filepath, new_filepath):
        
        """Instantiates the class with an existing file.""" 
        
        #Stores the filepath to the old submission file. 
        self.old_filepath = old_filepath 
        #Stores the filepath for the new submission file. 
        self.new_filepath = new_filepath
        #Stores the filepath for the TS data.  
        self.ts_filepath = "../edits_files/file_parts/ts_data.txt" 
        #Stores the filepath for the LAR data. 
        self.lar_filepath = "../edits_files/file_parts/lar_data.txt"
        #Stores the filepath for the LAR schema.
        self.lar_schema_filepath = "../schemas/lar_schema.json"  
        
        print("Instantiated.")
            
    def create_file(self, row_count=None):
        """
        Creates a new custom file, passing in a row count. 
        """
        #Creates new files and stores dataframes for LAR and TS data.
        self.load_lar_ts_df() 

        #Saves a file of LAR with a new number of rows.
        self.new_lar_rows(row_count=row_count) 
        
        #Places the dataframe of LAR in a file with a TS row. 
        self.lar_to_hmda_file()  
    
    def load_lar_ts_df(self):  
        """
        Saves LAR and TS dataframes as objects in memory. 
        Loads the column names for the LAR dataframe.
        Stores variables for the bank name and LEI.  
        """
        #Opening the submission file.
        with open(self.old_filepath, 'r+' ) as f:  
            #Reading in the first row as the TS submission. 
            ts_row = f.readline()
            #Reading in the other rows as the LAR submission. 
            lar_rows = f.readlines() 
        
        #Writes a file of TS data. 
        with open(self.ts_filepath, 'w') as out_ts: 
            out_ts.writelines(ts_row)

        #Writes a file of LAR data.
        with open(self.lar_filepath, 'w') as out_lar: 
            out_lar.writelines(lar_rows)

        #Loads in the schema for the LAR data. 
        with open(self.lar_schema_filepath) as d: 
            headers = json.load(d)
            headers = pd.DataFrame(headers)
         
        #Saves a dataframe of TS data in memory. 
        self.ts_df = pd.read_csv(self.ts_filepath, 
            delimiter="|", header=None, dtype='object',
            keep_default_na=False) 

        #Saves a dataframe of LAR data in memory. 
        self.lar_df = pd.read_csv(self.lar_filepath, 
            delimiter="|", header=None, dtype='object',
            keep_default_na=False) 

        #Places the column names to the LAR data. 
        self.lar_df.columns = headers['field'] 
        
        #Stores the second column of the TS data as "bank_name." 
        self.bank_name = self.ts_df.iloc[0][1]
        
        #Stores the second column of the LAR data as "lei."    
        self.lei = self.lar_df.iloc[0][1]
    
    def new_lar_rows(self, row_count=None):
        """
        Returns LAR data with a specified number of rows.
        """

        #Stores the LAR dataframe as a new LAR dataframe. 
        new_lar_df = self.lar_df

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
        
        """Applies the unique_uli function to the new LAR dataframe 
        to generate a unique set of ULIs."""  
        self.new_lar_df = self.unique_uli(new_lar_df)

        #Saves the new dataframe to the lar_filepath. 
        self.new_lar_df.to_csv(self.lar_filepath, sep="|", 
            index=False, header=None) 
        
        #Stores the raw data from the lar_filepath.
        #This variable will be used in the lar_to_hmda_file function. 
        with open(self.lar_filepath, 'r' ) as f:
            self.new_lar_data = f.readlines()

        #Stores the new number of rows.
        self.new_row_count = len(self.new_lar_df.index)
         
    def unique_uli(self, new_lar_df = None):
        """Generates a new set of ULI's for a LAR dataframe."""
        
        #Copying over ULIs with the LEI.
        new_lar_df["uli"] = new_lar_df["uli"].apply(lambda x: 
            self.lei)  
        
        """Generates a loan ID as a random 23-character 
        string for each LEI.""" 
        new_lar_df["uli"] = new_lar_df["uli"].apply(lambda x: x + 
            lar_gen.char_string_gen(23)) 
        
        # Adds a check digit to each.
        new_lar_df['uli'] = new_lar_df["uli"].apply(lambda x: x + 
            lar_gen.check_digit_gen(ULI=x))

        """If ULIs are duplicated, the unique_uli function 
        is applied again.""" 
        if len(new_lar_df['uli']) > len(set(new_lar_df['uli'])):
            print("Re-Running")
            self.unique_uli(new_lar_df)
        else:
            print("Unique ULIs Assigned")

        return new_lar_df  
        
    def lar_to_hmda_file(self):
        
        """
        Creates a HMDA submission file, passing in a dataframe of LAR 
        rows, the TS file, and a filepath to store the file. 
        """

        #Creates a filepath to store the new HMDA submission file.
        os.makedirs(os.path.dirname(self.new_filepath), exist_ok=True)
        
        """Copies the TS text file into the new filepath specified 
        in the function."""
        sh.copyfile(self.ts_filepath, self.new_filepath) 
        
        #Reads in the new_filepath text file and appends the LAR data. 
        with open(self.new_filepath, 'a') as append_lar:
            append_lar.writelines(self.new_lar_data)

        """Prints out a statement with the number of rows created, 
        and the location of the new file."""
        statement = (str("{:,}".format(self.new_row_count)) + 
            " Row File Created for " + str(self.bank_name) + 
            " File Path: " + str(self.new_filepath))
        
        print(statement)
