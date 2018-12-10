#!/usr/bin/env python
# coding: utf-8

# # Creating Large HMDA Submission Test Files
# 
"""This notebook demonstrates a class for creating large HMDA 
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

from large_test_files import LargeTestFiles 



# ### LargeTestFiles Class
# 

"""The following demonstrates a function from the LargeTestFiles
class that creates test files with a new maximum number of rows. The class is 
instantiated with a source file and a filename for the ouput of the
newly created file."""

# In[4]:


#The class is instantiated with an existing source file. 
large_file = LargeTestFiles(
	source_filename="../edits_files/clean_file_1000_rows.txt", 
	output_filename="../edits_files/clean_file_4000_rows.txt" )


# In[5]:


large_file.create_file(row_count=4000)






