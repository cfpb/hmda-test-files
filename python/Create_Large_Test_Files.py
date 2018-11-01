#!/usr/bin/env python
# coding: utf-8

# # Creating Custom Row HMDA Submission Test Files
# 
# This notebook demonstrates a class for creating custom row HMDA submission test files.

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

from lar_generator import lar_gen #Imports lar_gen class. 
from custom_test_files import Custom_Test_Files
lg = lar_gen() #Instantiates lar_gen class as lg. 


# ### Custom_Test_Files Class
# 
# The following demonstrates a function from the Custom_Test_Files class that creates test files with a custom number of rows. The class is instantiated with an existing file to create a new file with a specified row count. This set of functions is from the Custom_Test_Files class defined below.

# In[4]:


#The class is instantiated with an existing clean file
cf = Custom_Test_Files(filename = "../edits_files/file_parts/clean_file_1000_rows_Bank1.txt")


# In[5]:


cf.create_file(row_count=4000, save_file = "../edits_files/new_files/clean_file_4000_rows_Bank1.txt")


# In[ ]:




