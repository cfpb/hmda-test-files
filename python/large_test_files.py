#The following code imports the required packages.
import math
import json
import os
import pandas as pd
import random
import string
import time
import yaml
import utils

from lar_generator import lar_gen #Imports lar_gen class. 

#Instantiates lar_gen class as lar_gen. 
lar_gen = lar_gen() 

def unique_uli(new_lar_df = None, lei=None):
    """Generates a new set of ULI's for a LAR dataframe."""
    
    #Copying over ULIs with the LEI.
    new_lar_df["uli"] = new_lar_df["uli"].apply(lambda x: 
        lei)  
    
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

class LargeTestFiles(object):
    
    """
    Returns a LargeTestFiles class object to create submission files
    with a specified number of rows.
    """
    
    def __init__(self, source_filepath, source_filename, 
        output_filepath, output_filename):
        
        """Instantiates the class with an existing file.""" 
        
        #Stores the filepath to the source submission file. 
        self.source_filepath = source_filepath 
        #Stores the filepath for the output submission file. 
        self.output_filepath = output_filepath

        #Stores the filename to the source submission file. 
        self.source_filename = source_filename 
        #Stores the filename for the output submission file. 
        self.output_filename = output_filename
         
        print("Instantiated.")
            
    def create_file(self, row_count=None):
        """
        Creates a new large test file, passing in a row count to 
        set a maximum number of rows. 
        """
        self.ts_df, self.lar_df = utils.read_data_file(path=self.source_filepath, 
            data_file=self.source_filename)

        #Stores the second column of the TS data as "bank_name." 
        self.bank_name = self.ts_df.iloc[0][1]
        
        #Stores the second column of the LAR data as "lei."    
        self.lei = self.lar_df.iloc[0][1]

        #Changes the TS row to the number of rows specified. 
        self.ts_df['lar_entries'] = str(row_count)

        #Creates a dataframe of LAR with the number of rows specified.
        new_lar_df = self.new_lar_rows(row_count=row_count)

        #Writes file to the output filename and path. 
        utils.write_file(path=self.output_filepath, ts_input=self.ts_df, 
            lar_input=new_lar_df, name=self.output_filename)
        
        """Prints out a statement with the number of rows created, 
        and the location of the new file."""
        statement = (str("{:,}".format(row_count)) + 
            " Row File Created for " + str(self.bank_name) + 
            " File Path: " + str(self.output_filepath+self.output_filename))
        
        print(statement)
    
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
        new_lar_df = unique_uli(new_lar_df=new_lar_df, lei=self.lei)

        return new_lar_df  

       
