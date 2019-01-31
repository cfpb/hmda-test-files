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

def unique_uli(new_lar_df = None, lei=None):
    """
    Generates a new set of ULI's for a LAR dataframe.

    """
    
    #Copying over ULIs with the LEI.
    new_lar_df["uli"] = new_lar_df["uli"].apply(lambda x: 
        lei)  
    
    #Generates a loan ID as a random 23-character 
    #string for each LEI.
    new_lar_df["uli"] = new_lar_df["uli"].apply(lambda x: x + 
        lar_gen.char_string_gen(23)) 
    
    # Adds a check digit to each.
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