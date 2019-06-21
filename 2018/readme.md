# 2018 File Generation Features

## Overview
The scripts used in this repository for generating clean files, edit files, and edit reports use methods from the FileGenerator class. Clean files will pass syntax and validity edits. Edit test files will fail at least one (and sometimes more than one) edit. These files will be used as a double check for the implementation of the HMDA edits for the 2018 HMDA Platform. Creating edit test files is a two step process. The generation of edit test files requires a clean data file to be present. If edit files already exist with the same names as those produced by this script, they will be overwritten.

The `FileGenerator()` class is located in [`file_generator.py`](https://github.com/cfpb/hmda-test-files/blob/master/2018/python/file_generator.py) and can be instantiated without any inputs. The class uses data stored with yaml configuration files in the [`python/configurations/`](https://github.com/cfpb/hmda-test-files/tree/master/2018/python/configurations) directory. 

Edit test files are written to the directory indicated in `test_filepaths.yaml`based on edit type, such as /edits_files/test_files/Bank1/syntax/s300.txt. The file name indicates which edit the file is designed to test. If an edit has multiple conditions, a file will be made for each condition in the format /edits_files/test_files/Bank1/syntax/s301_1.txt. If multiple permutations of the same condtion are tested, the files will have an alphabetic naming convention, such as /edits_files/test_files/Bank1/validity/v715_a.txt.

The FileGenerator Class relies on four other classes, each with its own role in file creation:

lar_generator in [`lar_generator.py`](https://github.com/cfpb/hmda-test-files/blob/master/2018/python/lar_generator.py) 

Creates raw TS and LAR rows using the [TS and LAR schema.json files located in /schemas/](https://github.com/cfpb/hmda-test-files/blob/master/2018/schemas) , the values of which are then manipulated to create clean test files or edit test files.

`rules_engine` in [`rules_engine.py`](https://github.com/cfpb/hmda-test-files/blob/master/2018/python/rules_engine.py) 

Contains logic for each edit. The rules engine can generate an edit report for a passed file. This report contains the following fields:

* edit name
* status (pass/fail)
* number of rows failed
* ULIs/NULIs of rows that failed (as a list)
    
The report is created as a dataframe that can be passed to other methods of the class and is also written to CSV.

LAR and TS dataframes are passed into this class, and its methods output edit details that show among its fields the edit name, the status of the edit (failed or passed), the number of rows failed by the edit, if any, and the ULI's or NULIs (loan ID) of the rows that fail the edit. Each method creates a results dataframe that holds the rows that have failed the specific edit. The class then wraps the results into an edit report that can be parsed by other methods in the repository.  

`lar_constraints` in [`lar_constraints.py`](https://github.com/cfpb/hmda-test-files/blob/master/2018/python/rules_engine.py) 

This class contains methods that modify synthetic LAR rows that fail edits so that they pass those edits. Because the lar_constraints class changes LAR rows sequentially and with set values, it may change values to pass an edit, while failing edits previously corrected. To create clean files, the synthetic rows are passed between lar_constraints and rules_engine, until there are no more syntax or validity edits present. 

`test_data` in [`test_file_generator.py`](https://github.com/cfpb/hmda-test-files/blob/master/2018/python/test_file_generator.py) 

Contains methods that manipulate LAR or TS dataframes to fail a specific syntax or validity edit. Because the test_data class changes LAR rows sequentially and with set values, it may fail other edits while changing values in the synthetic LAR to fail a specific edit.

Note: changes to the clean data do not create exhaustive test cases for each edit. 

Each edit logic method in `lar_constraints`, `test_data`, and `rules_engine` is prefaced with 's', 'v', or 'q' to indicate a syntax, validity or quality edit respectively.

## Configurations 
The following yaml configuration files and values can be changed to alter the output of HMDA submission test files. 

### [Test Files Configuration](https://github.com/cfpb/hmda-test-files/blob/master/2018/python/configurations/test_filepaths.yaml)

| Key| Default Value|Data Type| Expanation |
|:-------------|:-------------|:--------|:--------|
|clean_filepath | `../edits_files/clean_files/{bank_name}/`|String| Filepath for generated clean files. Note: the filepath needs to contain `{bank_name}` for formatting the institution name to the path. |
| clean_filename|`clean_file_{n}_rows_{bank_name}.txt`|String|Filename for generated clean files. Note: the filepath needs to contain `{bank_name}` and `{n}` for formatting the institution name and number of rows to the filename. |
| validity_filepath | `../edits_files/test_files/{bank_name}/validity/`|String|Filepath for generated validity edit test files. Note: the filepath needs to contain `{bank_name}` for formatting the institution name to the path.|
|syntax_filepath |`../edits_files/test_files/{bank_name}/syntax/`|String|Filepath for generated syntax edit test files. Note: the filepath needs to contain `{bank_name}` for formatting the institution name to the path. 
|quality_filepath | `../edits_files/test_files/{bank_name}/quality/`|String|Filepath for generated quality edit test files. Note: the filepath needs to contain `{bank_name}` for formatting the institution name to the path. 
| quality_pass_s_v_filepath|`../edits_files/test_files/{bank_name}/quality_pass_s_v/`|String| Filepath for generated quality edit test files that also pass syntax and validity edits. Note: the filepath needs to contain `{bank_name}` for formatting the institution name to the path |
ts_schema_json | `../schemas/ts_schema.json`|String|Filename for the Transmital Sheet schema. 
lar_schema_json| `../schemas/lar_schema.json`|String|Filename for the Loan Application Register schema. |
log_filename | `"clean_files_log.txt"` |String|Filename for the log file detailing iterations in the file creation process.|
log_mode|`'w'`|String|The mode for logging files. Currently, the log mode is set to writer over the previous file (`'a'`). This configuration can be changed to append log entries to the same file (`'a'`).


### [Geographic Data Configuration](https://github.com/cfpb/hmda-test-files/blob/master/2018/python/configurations/geographic_data.yaml)

|Key|Default Value|Data Type|Expanation|
|:-------------|:-------------|:--------|:--------|
|crosswalk_data_file |`../dependencies/census_2018_MSAMD_name.txt`|String|Filepath and name for geographic cross walk data located in the [dependencies folder](https://github.com/cfpb/hmda-test-files/blob/master/2018/dependencies/). The crosswalk data file contains relationships between variables such as state, county, census tract, MSA, and population that are used to generate clean files and edit files. |
| zip_code_file|`../dependencies/zip_codes.json`|String|Filepath and name for a JSON file containing zip codes.|
| validity_filepath |`../edits_files/test_files/{bank_name}/validity/`|String|Filepath for generated validity edit test files. Note: the filepath needs to contain `{bank_name}` for formatting the institution name to the path.|
|file_columns |`['collection_year', 'msa_md', 'state_code', 'county', 'tracts', 'ffiec_median_family_income', 'population','minority_population_%', 'number_of_owner_occupied_units', 'number_of_1_to_4_family_units', 'fract_mfi', 'tract_to_msa_income_%', 'median_age', 'small_county', 'msa_md_name']`|Array| A list of columns for the crosswalk data. Note: while column names may be changed, users cannot change the following column names without changing the FileGenerator class: 'stateCode', 'county','tracts', and 'smallCounty.'|
state_codes|`{'AL':'01', 'AK':'02', 'AZ':'04', 'AR':'05', 'CA':'06', 'CO':'08','CT':'09', 'DE':'10', 'DC':'11', 'FL':'12', 'GA':'13', 'HI':'15', 'ID':'16', 'IL':'17','IN':'18', 'IA':'19', 'KS':'20', 'KY':'21', 'LA':'22', 'ME':'23', 'MD':'24', 'MA':'25', 'MI':'26', 'MN':'27', 'MS':'28', 'MO':'29', 'MT':'30', 'NE':'31', 'NV':'32', 'NH':'33', 'NJ':'34', 'NM':'35', 'NY':'36', 'NC':'37', 'ND':'38', 'OH':'39', 'OK':'40', 'OR':'41', 'PA':'42', 'RI':'44', 'SC':'45', 'SD':'46', 'TN':'47', 'TX':'48', 'UT':'49', 'VT':'50', 'VA':'51', 'WA':'53', 'WV':'54', 'WI':'55', 'WY':'56', 'AS':'60', 'PR':'72', 'VI':'78'}`|Object|A dictionary of two-letter state codes to FIPS state codes.
state_FIPS_to_abbreviation|`{'01':'AL', '02':'AK', '04':'AZ', '05':'AR', '06':'CA', '08':'CO', '09':'CT', '10':'DE', '11':'DC', '12':'FL', '13':'GA', '15':'HI', '16':'ID', '17':'IL', '18':'IN', '19':'IA', '20':'KS', '21':'KY', '22':'LA', '23':'ME', '24':'MD', '25':'MA', '26':'MI', '27':'MN', '28':'MS', '29':'MO', '30':'MT', '31':'NE', '32':'NV', '33':'NH', '34':'NJ', '35':'NM', '36':'NY', '37':'NC', '38':'ND', '39':'OH', '40':'OK', '41':'OR', '42':'PA', '44':'RI', '45':'SC', '46':'SD', '47':'TN', '48':'TX', '49':'UT', '50':'VT', '51':'VA', '53':'WA', '54':'WV', '55':'WI', '56':'WY', '60':'AS', '72':'PR', '78':'VI'}`|Object|A dictionary of FIPS state codes to two-letter state codes. 

# [Clean File Configuration](https://github.com/cfpb/hmda-test-files/blob/master/2018/python/configurations/clean_file_config.yaml) 

Holds values for the test institution, file length, and file name for generating a TS Sheet and LAR rows for a clean HMDA submission file. Other variables, such as data ranges can also be set in this file. For each key, the configuration has a description, data type, and value. The default configuration is listed below. 

|Key|Description|Type|Default Value
|:-------------|:-------------|:--------|:--------
clean_file|The file used to create error files|File|`clean_file_100_rows_Bank1.txt`
file_length|The number of lines in the clean data file|Integer|`100`
name|The name of the institution filing data|File|`Bank1`
lei|The Legal Entity Identifier of the institution|String|`BANK1LEIFORTEST12345`
tax_id|The federal tax ID of the filing institution|String|`02-1234567`
calendar_year|The year of activity|String|`2018`
calendar_quarter|The calendar quarter to which the filing relates|Integer|`4`
contact_name|The name of the contact person for the institution|String|`Mr. Smug Pockets`
contact_tel|The telephone number of the contact person|String|`555-555-5555`
contact_email|The email of the contact person|String|`pockets@ficus.com`    
street_addy|Property street address|String|`1234 Hocus Potato Way`
city|Office city|String|`Tatertown`
state|Office state|String|`UT`
zip_code|Office ZIP code|String|`84096`
agency_code|The agency code of the filing institution|Integer|`9`
max_age||Integer|`110`
max_amount|Maximum loan amount in dollars|Integer|`467000`
max_income|Maximum applicant income in thousands|Integer|`300`
max_rs|Maximum rate spread|Integer|`100`
max_credit_score|Maximum credit score|Integer|`840`
min_credit_score|Minimum credit score|Integer|`650`
loan_costs|Maximum loan costs|Integer|`10000`
points_and_fees|Maximum points and fees|Integer|`10000`
orig_charges|Maximum origination charges|Integer|`10000`
discount_points|Maximum discount points cost|Integer|`10000`
lender_credits|Maximum lender credits|Integer|`10000`
interest_rate|Maximum interest rate|Integer|`25`
penalty_max|Maximum prepayment penalty term|Integer|`36`
dti|Maximum debt to income ratio|Integer|`100`
cltv|Combinted loan to value ratio|Integer|`120`
loan_term|Maximum loan term|Integer|`360`
intro_rate|Maximum introductory rate period|Integer|`36`
max_units|Maximum total units|Integer|`30`
prop_val_max|Maximum property value in dollars|Integer|`1000000`
prop_val_min|Minimum property value in dollars|Integer|`100000`

### Validating Quality Edit Files and Creating Edit Reports
The `test_data` logic for creating quality edit test files may cause rows to fail not only quality edits, but also syntax or validity edits in the creation process. The validate_quality_edit_file() method creates quality edit test files that do not have validity or syntax errors. This method uses the quality file path in `test_filepaths.yaml` to find a clean file for a specified quality edit. This clean file is used to source rows that pass validity and syntax edits that fail quality. This row is used as a base to construct a file of the length specified in the [Clean File Configuration](https://github.com/cfpb/hmda-test-files/blob/master/2018/python/configurations/clean_file_config.yaml). File outputs from this process are saved in the directory specified in [Test Files Configuration](https://github.com/cfpb/hmda-test-files/blob/master/2018/python/configurations/test_filepaths.yaml).

FileGenerator contains a method, `edit_report` that produces a report stored as a csv in the local path specified in [test_filepaths.yaml](https://github.com/cfpb/hmda-test-files/blob/master/2018/python/configurations/test_filepaths.yaml) 

## Additional Utilities
the repository contains utility functions that allow for further file customization. The functions are located in [`python/utils.py`](https://github.com/cfpb/hmda-test-files/blob/master/2018/python/utils.py). 

Function|Inputs|Description|
|:-------------|:-------------|:-------------|
`write_file`|`(path, ts_input, lar_input, name="test_file.txt")`| Writes TS and LAR dataframes to a HMDA submission test file (a single TS row and one to N LAR rows) with a specified file path and directory. 
`read_data_frames`|`(ts_df, lar_df)`| Reads in a HMDA submission test file and outputs both TS and LAR dataframes. 
`unique_uli`|`(new_lar_df, lei)`|Replaces existing ULIs in a LAR dataframe with a unique set of ULIs. 
`new_lar_rows`|`(row_count, lar_df, ts_df)`|Creates test files with customizable record count and data variables for testing load and edge cases. 
`row_by_row_modification`|`(lar_df, yaml_filepath='configurations/row_by_row_modification.yaml')`|Changes a LAR dataframe given changes specified in a yaml file. It allows users to test for minor changes in LAR data.
`change_bank`|`(ts_data, lar_data, new_bank_name, new_lei, new_tax_id)`|Changes TS and LAR dataframes to a new test institution with a new Institution Name, LEI, and Tax ID. 
`check_digit_gen`|`(valid=True, ULI)`|Generates and appends a check digit to a ULI.  