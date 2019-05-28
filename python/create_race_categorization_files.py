import file_generator
from file_generator import FileGenerator
from race_categorization import RaceCategorization
import utils
import glob
import os
import pandas as pd 
import utils

#Instantiates the RaceCategorization class. 
race_categorization = RaceCategorization()

#Generates a file and answer key for testing Joint Race: Condition 1. 
race_categorization.joint_condition_1()

#Generates a file and answer key for testing Joint Race: Condition 2.
race_categorization.joint_condition_2()

