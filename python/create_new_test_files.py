#!/usr/bin/env python
# coding: utf-8

# # Creating Custom Row HMDA Submission Test Files
# 
"""This notebook demonstrates a class for creating custom row HMDA 
submission test files."""

# In[3]:


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

from custom_test_files import CustomTestFiles 



# ### Custom_Test_Files Class
# 

"""The following demonstrates a function from the Custom_Test_Files 
class that creates test files with a custom number of rows. The class is 
instantiated with an existing file and a filepath for the 
newly created file."""

# In[4]:


#The class is instantiated with an existing clean file
custom_file = CustomTestFiles(old_filepath = "../edits_files/clean_file_1000_rows.txt", 
	new_filepath= "../edits_files/clean_file_4000_rows.txt" )


# In[5]:


custom_file.create_file(row_count=4000)






