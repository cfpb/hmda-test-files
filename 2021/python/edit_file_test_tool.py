#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ast
import json
import os
from os.path import join, isfile
from os import listdir, makedirs, path

import pandas as pd
import yaml

#Edit report configurations are located in configurations/edit_report_config.yaml
import lar_generator
from rules_engine import rules_engine

pd.options.display.max_columns = 999
pd.options.display.max_rows = 999
pd.set_option('display.max_colwidth', -1)


# In[2]:


#load configurations
lar_config_file = 'configurations/clean_file_config.yaml'
bank_config = "configurations/ABHINAYAA_config.yaml"
geo_config_file='configurations/geographic_data.yaml'
filepaths_file = 'configurations/test_filepaths.yaml'
lar_schema_file="../schemas/lar_schema.json"
ts_schema_file="../schemas/ts_schema.json"
lar_2018_haeder = []

with open(lar_schema_file, "r") as in_schema:
    lar_schema = in_schema.readlines()
lar_schema = [line.strip("\n") for line in lar_schema]
lar_string = "".join([line for line in lar_schema])
lar_json = json.loads(lar_string)
lar_2018_header = []
for row in lar_json:
    lar_2018_header.append(row["field"])

          


# In[3]:


#open configuration files and load data
with open(bank_config) as f:
	bank_config_data = yaml.safe_load(f)

with open(lar_config_file, 'r') as f:
	lar_file_config_data = yaml.safe_load(f)

with open(filepaths_file, 'r') as f:
	filepaths = yaml.safe_load(f)

with open(geo_config_file, 'r') as f:
	geo_config = yaml.safe_load(f)

with open(bank_config, 'r') as f:
	bank_config_data = yaml.safe_load(f)

with open(geo_config["zip_code_file"], 'r') as f:
	zip_codes = json.load(f)
zip_codes.append("Exempt")


# In[4]:


geographic_data = pd.read_csv(geo_config['geographic_data_file'], delimiter='|', header=0,
	names=geo_config['file_columns'], dtype=object) #instantiate Census file data as dataframe

#create 11 digit Census Tract codes from 5 digit county and 6 digit tract
geographic_data['county_fips'] = geographic_data.apply(lambda x: str(x.state_code) + str(x.county), axis=1)
geographic_data["tract_fips"] = geographic_data.apply(lambda x: str(x.county_fips) + str(x.tracts), axis=1)

with open(geo_config["zip_code_file"], 'r') as f: 
	zip_codes = json.load(f)
zip_codes.append("Exempt")#add exempt as a valid ZIP Code

#instantiate lar generator to create random LAR and fixed TS data
lar_gen = lar_generator.lar_gen(lar_schema_file=lar_schema_file, ts_schema_file=ts_schema_file)

#instantiate rules engine to check conformity of synthetic data to FIG schema
#rules engine creates edit reports to see which edits were failed by which rows in which file
rules_engine = rules_engine(config_data=lar_file_config_data, state_codes=geo_config["state_codes"], state_codes_rev=geo_config["state_codes_rev"],
	geographic_data=geographic_data, full_lar_file_check=False)


# In[5]:


#set location for edit report CSV writing
edit_report_path = filepaths["edit_report_output_filepath"] 

#get paths to check for clean files (by bank name) 
#store as list to match edit files format
clean_filepath = [filepaths["clean_filepath"].format(bank_name=bank_config_data["name"]["value"])]

#get directories to check for files
bank_test_v_dir = filepaths["validity_filepath"].format(bank_name=bank_config_data["name"]["value"])
bank_test_s_dir = filepaths["syntax_filepath"].format(bank_name=bank_config_data["name"]["value"])
bank_test_q_dir = filepaths["quality_filepath"].format(bank_name=bank_config_data["name"]["value"])
bank_test_q_pass_dir = filepaths["quality_pass_s_v_filepath"].format(bank_name=bank_config_data["name"]["value"])

edit_filepaths = [bank_test_v_dir, bank_test_s_dir, bank_test_q_dir]
print("edit report save path", edit_report_path)
print("clean file dir", clean_filepath)
print("valdity test file dir", bank_test_v_dir)
print("syntax test file dir", bank_test_s_dir)
print("quality test file dir", bank_test_q_dir)
print("s/v clean quality test file dir", bank_test_q_pass_dir)


# In[6]:


def get_file_names(filepaths):
    """
    filepaths: list of paths to check for files
    file_names: list of files in the path(s)
    """
    file_names = []
    for path in filepaths:
    #concat edit file path to edit file name to make looping easier in edit check
        new_file_names = [path+f for f in listdir(path) if isfile(join(path, f))]
        file_names = file_names + new_file_names
    
    try:
        file_names = [f for f in file_names if '.DS_Store' not in f]
    except:
        print("no DS Store to remove")
    file_names.sort()
    print(len(file_names), "files found in {filepaths}".format(filepaths=filepaths))
    return file_names

def generate_edit_report(file_list, save_name, edits_list=["s","v","q","m"], save_path=edit_report_path, 
                         save_report=True):
    """
    file_list: list of files to check against rules engine
    edits_list: list of edit types to check options are s, v, q, m
    """
    #set up data frame seed for edit report to use as a base for concatenation
    report_df = pd.DataFrame([], columns=['file_name', 'edit_name', 'row_type', 'field', 'fail_count', 'failed_rows', "file_edit_name"], index=[0])
    for file in file_list: #iterate over clean test files and create report results for each
        rules_engine.reset_results() #clear previous edit report results
        #print(file) #display current working file
        ts_df, lar_df = rules_engine.split_ts_row(file) #split TS row from LAR data for dataframe usage
        #load current file data to rules engine to create edit report
        rules_engine.load_ts_data(ts_df)
        rules_engine.load_lar_data(lar_df)
        #generate edit report
        new_results_df = rules_engine.create_edit_report(edits_list)
        new_results_df["file_name"] = file #label file_name in report
        new_results_df["file_edit_name"] = new_results_df.file_name.apply(lambda x: x.split("/")[-1].split("_")[-1].replace(".txt",""))
        report_df = pd.concat([report_df, new_results_df])
        report_df.reset_index(drop=True, inplace=True)
        report_df.drop(0, inplace=True)
    if save_report:
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        report_df.to_csv(save_path + save_name, sep="|", index=False)
    return report_df

### check if all files were created: use rules engine list
#get list of ones missing



# In[7]:


clean_files = get_file_names(clean_filepath)
clean_report_df = generate_edit_report(clean_files, save_name=filepaths['clean_file_report_output_filename'].format(bank_name=bank_config_data["name"]["value"]))


# In[25]:


clean_report_df[clean_report_df.fail_count>0].edit_name.unique()


# In[9]:



edit_files = get_file_names(edit_filepaths)
edit_report_df = generate_edit_report(edit_files, save_name=
                                      filepaths['edit_report_output_filename'].format(bank_name=
                                                                                      bank_config_data["name"]["value"]))


# In[34]:


#edit_report_df[((edit_report_df.file_edit_name.isin(["q648", "q651"]))&(edit_report_df.fail_count>0))&
 #             (edit_report_df.edit_name.apply(lambda x: x[:1] in ("s", "v")))]

edit_report_df[(edit_report_df.file_name==edit_report_df.file_edit_name)]

edit_report_df.file_edit_name.unique()
edit_report_df[["edit_name", "fail_count", "field", "file_edit_name", "file_name", "row_type"]][(edit_report_df.fail_count>=500)&
                                                     (edit_report_df.file_name.apply(lambda x: "q" not in x))&
                                                     (edit_report_df.edit_name.apply(lambda x: x[:1] in ("s", "v")))&
                                                    (edit_report_df.apply(lambda x: ))]


# In[14]:


data_file = "../edits_files/Abhinayaa Bank/test_files/validity/Abhinayaa Bank_500_v673_1.txt"
ts_df, lar_df = rules_engine.split_ts_row(data_file)
lar_df.head()
type(lar_df)


# ### Read Edit Reports

# In[12]:


def get_fail_ulis(report_df, edit_name_list, file_name):
    """
    returns a list of ULIs failing the specified edits
    edit_name_list: list of edits IE q648
    file_name: name of file in edit report IE Chynna Bank_clean_500_rows.txt
    """
    fail_rows = report_df.failed_rows[(report_df.file_name==file_name)&
               (report_df.edit_name.isin(edit_name_list))].iloc[0]
    fail_rows = fail_rows.strip("']['").split(", ")
    fail_rows = [row.replace("'","") for row in fail_rows]
    return fail_rows


# In[13]:


clean_report_df = pd.read_csv(edit_report_path +                              filepaths['clean_file_report_output_filename'].format(bank_name=bank_config_data["name"]["value"]),
                            sep="|")

clean_report_df[(clean_report_df.file_name=="Chynna Bank_clean_500_rows.txt")&
               (clean_report_df.edit_name.isin(["q648"]))]

q648_fails = get_fail_ulis(clean_report_df, ["q648"], "Chynna Bank_clean_500_rows.txt")
clean_report_df[(clean_report_df.file_name=="Chynna Bank_clean_500_rows.txt")&
               (clean_report_df.failed_rows.apply(lambda x: len(x) !=2))]

clean_report_df[clean_report_df.edit_name.apply(lambda x: x[:1]=="v")]


# In[ ]:


print(bank_clean_dir)
col_list = ["action_taken", "uli", "lei"]
test_file_df = pd.read_csv(bank_clean_dir+"Chynna Bank_clean_500_rows.txt", sep="|", header=None, names=lar_2018_header,
                           skiprows=[0], dtype=object)
test_file_df[col_list][test_file_df.uli.isin(q648_fails)]


# #1) If Action Taken equals 1, 2, 3, 4, 5, 7, or 8, the first
# 20 characters of the ULI should match the reported
# LEI.

# In[ ]:


#load edit file report
test_report_df = pd.read_csv(edit_report_path +                              filepaths['edit_report_output_filename'].format(bank_name=bank_config_data["name"]["value"]),
                            sep="|")

test_report_df[test_report_df.file_name=="../edits_files/Chynna Bank/test_files/quality/Chynna Bank_500_q648.txt"]
test_report_df.iloc[:,:-2][test_report_df.edit_name=="v610_2"]


# In[ ]:


test_file_df = pd.read_csv("../edits_files/Chynna Bank/test_files/quality/Chynna Bank_500_q651.txt", sep="|", header=None, names=lar_2018_header,
                           skiprows=[0], dtype=object, keep_default_na=False)
test_file_df[["action_taken", "app_date"]]#[(test_file_df.action_taken.isin(["6"]))]#&(~test_file_df.app_date.isin(["NA"]))]


# In[ ]:


len(test_file_df[((test_file_df.app_date=="NA")&(test_file_df.action_taken!="6"))|
				((test_file_df.action_taken=="6")&(test_file_df.app_date!="NA"))])


# In[ ]:


test_report_df


# In[ ]:




