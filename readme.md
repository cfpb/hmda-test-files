## Repository Purpose:
This repository contains code used to generate synthetic LAR files. Currently, the test files repository supports file creation for submission years, 2018 and 2019. The success of the HMDA program requires that the data submitted meet the technical and business requirements of the HMDA Platform. The code and test files in this repository will provide a standardized means of checking the implementation of business rules for data submission in the HMDA Platform.

## Repository Use Cases:
- Enable business analysts to test the HMDA Platform. 
- Provide files to check API returns
- Provide a resource for developers to use while implementing business rules in code
- Provide synthetic data files meeting HMDA schemas for 2018 and 2019 to be used in training

## Repository Structure
Each year listed in the parent directory contains its own codebase for running test files for that submission year. Users should navigate to each year directory to run scripts and view code.  
- [2018/python](https://github.com/cfpb/hmda-test-files/tree/master/2018/python) and [2019/python](https://github.com/cfpb/hmda-test-files/tree/master/2019/python):
    - Contains the notebooks and python scripts used to generate synthetic LAR data, perturb the data so that it fails specific business rules, and code to check that the produced files fail edits as expected.

- [2018/schemas](https://github.com/cfpb/hmda-test-files/tree/master/2018/schemas) and [2019/schemas](https://github.com/cfpb/hmda-test-files/tree/master/2019/schemas)
    - Contains JSON objects that represent the data structures for LAR and Transmittal Sheet as defined by the [2018 HMDA FIG](https://s3.amazonaws.com/cfpb-hmda-public/prod/help/2018-hmda-fig-2018-hmda-rule.pdf) and the [2019 HMDA FIG](https://s3.amazonaws.com/cfpb-hmda-public/prod/help/2019-hmda-fig.pdf)

- [2018/dependencies](https://github.com/cfpb/hmda-test-files/tree/master/2018/dependencies) and [2019/dependencies](https://github.com/cfpb/hmda-test-files/tree/master/2019/dependencies)
    	- Contains files used in the generation of synthetic LAR data.
        - Tract to CBSA data.
        - A file containing a list of US ZIP codes

To read further about the file generation features for each year, please refer to the documents below:

[2018 File Generation Features](https://github.com/cfpb/hmda-test-files/tree/master/2018/2018_File_Generation_Features.md)
[2019 File Generation Features](https://github.com/cfpb/hmda-test-files/tree/master/2019/2019_File_Generation_Features.md) 
## Dependencies
- Python 3.5 or greater
- [Jupyter Notebooks](http://jupyter.org/): `pip install jupyter`
- [Pandas](http://pandas.pydata.org/): `pip install pandas`

## Generating Clean Files
Clean files will pass the HMDA edits (business rules for data submission). These files are used as the base for generating files that will fail edits. Running the following scripts will create the edits_files directory and a data file that will pass the HMDA edit checks. The file will have a number of rows set in a YAML clean file configuration for each directory. Other variables, such as data ranges can also be set in the configuration files.

For 2019:
1. Run `cd 2019/python` to navigate to the python directory. 
2. Adjust the [2019 Clean File Configuration](https://github.com/cfpb/hmda-test-files/tree/master/2019/configurations/clean_file_config.yaml) for bank name, LEI, Tax ID and number of rows. 
3. Run `python3 generate_2019_clean_files.py`
4. The clean test file should appear in a new edits_files directory under `2019/edits_files/clean_files/{Bank Name}/` with the filename `clean_file_{Number or Rows}_{Bank Name}.txt`. 

Note: the filepath and filename for clean files can be adjusted in the [2019 Test Filepaths](https://github.com/cfpb/hmda-test-files/tree/master/2019/configurations/test_filepaths.yaml) YAML configuration file under `clean_filepath` and `clean_filename` keys. 

For 2018:
1. Run `cd 2018/python` to navigate to the python directory. 
2. Adjust the [2018 Clean File Configuration](https://github.com/cfpb/hmda-test-files/tree/master/2018/configurations/clean_file_config.yaml) for bank name, LEI, Tax ID and number of rows. 
3. Run `python3 generate_2018_clean_files.py`
4. The clean test file should appear in a new edits_files directory under `2018/edits_files/clean_files/{Bank Name}/` with the filename `clean_file_{Number or Rows}_{Bank Name}.txt`. 

Note: the filepath and filename for clean files can be adjusted in the [2018 Test Filepaths](https://github.com/cfpb/hmda-test-files/tree/master/2018/configurations/test_filepaths.yaml) YAML configuration file under `clean_filepath` and `clean_filename` keys. 

## Generating Test Files
Test files will fail at least one (and sometimes more than one) edit. These files are used as a double check for the implementation of the HMDA edits in the HMDA Platform for each submission year.

Creating test files is a two step process. The generation of edit test files requires a clean data file to be present. A clean file is created when generate clean files scripts are run. Running generate test files modifies the data from the clean file and saves it with the name of the edit check that it will fail. If edit files already exist with the same names as those produced by this script, they will be overwrriten.

These files are written to the appropriate directory based on edit type, such as 2019/edits_files/test_files/{Bank Name}/syntax/s300.txt. The file name indicates which edit the file is designed to test. If an edit has multiple conditions, a file will be made for each condition in the format 2019/edits_files/test_files/{Bank Name}/syntax/s301_1.txt.

For 2019: 
1. Run `cd 2019/python` to navigate to the python directory. 
2. Run `python3 generate_2019_error_files.py`
3. The error files files for testing syntax, validity, and quality edit test files should appear in the following diretories:
	- Syntax: `2019/edits_files/test_files/{Bank Name}/syntax`
	- Validity: `2019/edits_files/test_files/{Bank Name}/validity`
	- Quality: `2019/edits_files/test_files/{Bank Name}/quality`

Note: the filepath and filename for test files can be adjusted in the [2019 Test Filepaths](https://github.com/cfpb/hmda-test-files/tree/master/2019/configurations/test_filepaths.yaml) YAML configuration file under the keys, `syntax_filepath`, `validity_filepath`, and `quality_filepath`.  

For 2018: 
1. Run `cd 2018/python` to navigate to the python directory. 
2. Run `python3 generate_2018_error_files.py`
3. The error files files for testing syntax, validity, and quality edit test files should appear in the following diretories:
	- Syntax: `2018/edits_files/test_files/{Bank Name}/syntax`
	- Validity: `2018/edits_files/test_files/{Bank Name}/validity`
	- Quality: `2018/edits_files/test_files/{Bank Name}/quality`

Note: the filepath and filename for test files can be adjusted in the [2018 Test Filepaths](https://github.com/cfpb/hmda-test-files/tree/master/2018/configurations/test_filepaths.yaml) YAML configuration file under the keys, `syntax_filepath`, `validity_filepath`, and `quality_filepath`. 

## Generating Large Files 
Often, large files would need to be generated to support load testing. The repository allows users to creates a test file based on existing test file data to create a new file with a larger number of rows.

To generate large files for 2019: 
1. Run `cd 2019/python` to navigate to the python directory.
2. Adjust the [2019 File Large File Script Configuration](https://github.com/cfpb/hmda-test-files/tree/master/2019/configurations/test_filepaths.yaml) to specify bank name, lei, tax id, row count, output filepath, and output filename. 
3. Run `python3 large_test_files_script.py` to produce the large file. 

To generate large files for 2018: 
1. Run `cd 2018/python` to navigate to the python directory.
2. Adjust the [2018 File Large File Script Configuration](https://github.com/cfpb/hmda-test-files/tree/master/2018/configurations/test_filepaths.yaml) to specify bank name, lei, tax id, row count, output filepath, and output filename. 
3. Run `python3 large_test_files_script.py` to produce the large file. 


## Data Generation Notes:
These values must be changed manually in the config.yaml file in each year directory. 
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