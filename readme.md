## Repository Purpose:
This repository contains code used to generate synthetic LAR files. These files will be used to support the development of the 2018 HMDA data submission platform and platforms in the future. The success of the HMDA program requires that the data submitted meet the technical and business requirements of the HMDA Platform. The code and test files in this repository will provide a standardized means of checking the implementation of the business rules for data submission in the HMDA Platform.

## Repository Use Cases:
- Enable business analysts to test the 2018 HMDA Platform
- Provide files to check API returns
- Provide a resource for developers to use while implementing business rules in code
- Provide synthetic data files meeting the 2018 HMDA schema to be used in training

## Repository Structure
- [Python](https://github.com/cfpb/hmda-test-files/tree/master/python):
    - Contains the notebooks and python scripts used to generate synthetic LAR data, perturb the data so that it fails specific business rules, and code to check that the produced files fail edits as expected.

- [Schemas](https://github.com/cfpb/hmda-test-files/tree/master/schemas)
    - Contains JSON objects that represent the data structures for LAR and Transmittal Sheet as defined by the [2018 HMDA FIG](https://s3.amazonaws.com/cfpb-hmda-public/prod/help/2018-hmda-fig-2018-hmda-rule.pdf)

- [Dependencies](https://github.com/cfpb/hmda-test-files/tree/master/dependencies)
    - Contains files used in the generation of synthetic LAR data.
        - Tract to CBSA data for 2015
        - A file containing a list of US ZIP codes

## Dependencies
- Python 3.5 or greater
- [Jupyter Notebooks](http://jupyter.org/): `pip install jupyter`
- [Pandas](http://pandas.pydata.org/): `pip install pandas`

## The FileGenerator Class. 
The `FileGenerator()` class is located in [`file_generator.py`](https://github.com/cfpb/hmda-test-files/blob/master/python/file_generator.py) and instantiates without any inputs in the function call. The class uses data stored with yaml configuration files in the 
[`python/configurations/`](https://github.com/cfpb/hmda-test-files/tree/master/python/configurations) directory. The following yaml configuration files can be altered to create HMDA submission test files.  

-[`test_filepaths.yaml`](https://github.com/cfpb/hmda-test-files/blob/master/python/configurations/test_filepaths.yaml) holds the filepath names for storing clean files, edit test files, log files, and edit reports as well as the paths to the TS and LAR schemas. 

-[`geography_data.yaml`](https://github.com/cfpb/hmda-test-files/blob/master/python/configurations/geographic_data.yaml) holds the filepaths for geographic dependency data such as the tract to CBSA file. The configuration includes the column names for the CBSA file and the columns used for file creation. The file also contains a path to a list of zip codes and a dictionary of FIPS state codes. 

-[`clean_file_config.yaml`](https://github.com/cfpb/hmda-test-files/blob/master/python/configurations/clean_file_config.yaml) holds values for the test institution, file length, and file name for generating a clean HMDA submission file for testing. Other variables, such as data ranges can also be set in this file. 

Clean files will pass syntax and validity edits. Edit test files will fail at least one (and sometimes more than one) edit. These files will be used as a double check for the implementation of the HMDA edits for the 2018 HMDA Platform. Creating edit test files is a two step process. The generation of edit test files requires a clean data file to be present. If edit files already exist with the same names as those produced by this script, they will be overwritten.

Edit test files are written to the directory indicated in `test_filepaths.yaml` based on edit type, such as /edits_files/test_files/Bank1/syntax/s300.txt. The file name indicates which edit the file is designed to test. If an edit has multiple conditions, a file will be made for each condition in the format /edits_files/test_files/Bank1/syntax/s301_1.txt.

### Changing Edit Logic and the Classes Used for File Creation 
The FileGenerator Class relies on four other classes, each with its own role in file creation. 

-`lar_generator` in [`lar_generator.py`](https://github.com/cfpb/hmda-test-files/blob/master/python/lar_generator.py) creates raw TS and LAR rows, the values of which are then manipulated to create clean test files or edit test files. 

-`rules_engine` in [`rules_engine.py`](https://github.com/cfpb/hmda-test-files/blob/master/python/rules_engine.py) contains logic for each edit. LAR and TS dataframes are passed into this class, and its methods output edit details that show among its fields the edit name, the status of the edit (failed or passed), the number of rows failed by the edit, if any, and the ULI's or 
NULIs (loan ID) of the rows that fail the edit. Each method creates a results dataframe that holds the rows that have failed the specific edit. The class then wraps the results into an edit report that can be parsed by other methods in the repository.  

- `lar_constraints` in [`lar_constraints.py`](https://github.com/cfpb/hmda-test-files/blob/master/python/rules_engine.py) contains methods for creating clean LAR rows that conform to pass syntax or validity edits. New edit logic methods must be made in terms of changing a TS or LAR row. 

- `test_data` in [`test_file_generator.py`](https://github.com/cfpb/hmda-test-files/blob/master/python/test_file_generator.py) contains methods that manipulate LAR or TS dataframes to fail a specific syntax or validity edit. New edit logic methods must be made in terms of changing a TS or LAR dataframe.

Each edit logic method in `lar_constraints`, `test_data`, and `rules_engine` is prefaced with 's', 'v', or 'q' to indicate a syntax, validity or quality edit respectively.

### Validating Quality Edit Files and Creating Edit Reports
The `test_data` logic for creating quality edit test files may cause rows to fail not only quality edits, but also syntax or validity edits in the creation process. One method in the FileGenerator class, `validate_quality_edit_file(quality_filename)` takes a quality edit test file from the quality filepaths directory in `test_filepaths.yaml`, drops rows that have syntax or validity edits, and duplicates the remaining clean rows to the length of the original file. The file is then saved in a new directory.

FilesGenerator also contains a method, `edit_report` that produces an edit report for a test file which is stored locally as a csv file. The edit report csv is stored in a directory and with a filename specified in `test_filepaths.yaml` 

## The Large Test Files Script
The Large Test Files script in [`large_test_files_script.py`](https://github.com/cfpb/hmda-test-files/blob/master/python/large_test_files_script.py) creates a test file based on existing test file data to create a new file with a larger number of rows. The script would only need to be run, and the attributes of the new file to be created can be changed with [`large_file_script_config.yaml`](https://github.com/cfpb/hmda-test-files/blob/master/python/configurations/large_file_script_config.yaml) in `python/configurations`. Files can be created with any number of rows, and can be made for any test institution so long as the Institution Name, LEI and Tax ID are provided in the configuration file. The configuration file stores filepaths for source data, as well as the filepaths for output. 

In addition, the script contains functionality for changing values by column and row using a yaml configuration. An example of this yaml configuration is located in `python/configurations/` as 
[`row_by_row_modification.yaml.`](https://github.com/cfpb/hmda-test-files/blob/master/python/configurations/row_by_row_modification.yaml) The script can contain a path to a yaml configuration to initiate this functionality. 

## Getting Started: Generating Clean Files, Edit Test Files, and Large Files. 
The function method `create_files(kind)` outputs a clean test file or a set of edit test files, with an input indicating the kinds of file to be created, `"clean_file"` or `"error_files"`. The `kind` keyword in the function is inputted as a string. 

A suggested workflow for creating test files:

1) *Instantiate FileGenerator*: Instantiate `FileGenerator()` to a python object in a script in the `python/` directory. Such as `file = FileGenerator()`.

2) *Adjust Configuration Files*: Make modifications to `test_filepaths.yaml`, `geography_data.yaml`, and `clean_file_config.yaml` for the kind of clean file to be produced. 

3) *Create a Clean File*: Run `file.create_files(kind='clean_file')` in the script to produce a clean file saved in a directory specified in `test_filepaths.yaml`. 

4) *Create Edit Test Files*: The clean file generated will then be used to create edit test files. Run 
`file.create_files(kind='error_files')` to produce syntax, validity, and quality edits files for the test institution in filepaths specified in `test_filepaths.yaml`. 

5) *Validate Quality Edit Test Files*: Ensure that quality edit test files are free of syntax and validity edits. Run `file.validate_quality_edit_file(quality_filename=[quality_file.txt])` in a python script on a quality edit filename.  

6) *Create a Large File*: Modify `large_file_script_config.yaml` and set the source filepath and source filename to the clean file created. Set the number of rows and/or change the test institution information. Set the filepath and name of the output file. Set the number of rows. Optionally, provide a row by row modification yaml file. Run `large_test_files_script.py` in terminal and create the large file. 


## Additional Utilities
In addition to test file creation features, the repository contains utility functions that work with existing test file data. These functions assist in creating test files with further customization, such as files with a large number of rows or files as part of a new institution. The functions are located in [`python/utils.py`](https://github.com/cfpb/hmda-test-files/blob/master/python/utils.py). 

These functions include:
- `write_file(path, ts_input, lar_input, name="test_file.txt")` 
	Writes TS and LAR dataframes to a HMDA submission test file with a specified file path and directory. 

- `read_data_frames(ts_df, lar_df)` 
	Reads in a HMDA submission test file and outputs a TS and LAR dataframe. 

- `unique_uli(new_lar_df, lei)`
	Writes a set of unique ULI’s with check digits to a LAR dataframe given an LEI input. 

- `new_lar_rows(row_count, lar_df, ts_df)` 
	Duplicates or retracts rows in a LAR dataframe to produce a file with a certain number of rows. Provides capabilities for creating LAR dataframes with large row counts. 

- `row_by_row_modification(lar_df, yaml_filepath='configurations/row_by_row_modification.yaml')`
	Changes a LAR dataframe given changes specified in a yaml file. It allows users to test for minor changes in LAR data.

- `change_bank(ts_data, lar_data, new_bank_name, 
	new_lei, new_tax_id)`
	Changes TS and LAR dataframes to a new test institution with a new Institution Name, LEI, and Tax ID. 

- `check_digit_gen(valid=True, ULI)`
	 Generates and appends a check digit to a ULI.   

## Data Generation Notes:
These values must be changed manually in the config.yaml file
- Name: Bank0
- LEI: B90YWS6AFX2LGWOXJ1LD
- Tax ID: 01-0123456

- Name: Bank1
- LEI: BANK1LEIFORTEST12345
- Tax ID: 02-1234567

----
## Open source licensing info
1. [TERMS](TERMS.md)
2. [LICENSE](https://github.com/cfpb/hmda-platform/blob/master/LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)
----