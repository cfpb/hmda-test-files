## Repository Purpose:
This repository contains code used to generate synthetic LAR files. These files will be used to support the development of the 2018 HMDA data submission platform. The success of the HMDA program requires that the data submitted meet the technical and business requirements of the HMDA Platform. The code and test files in this repository will provide a standardized means of checking the implementation of the business rules for data submission in the HMDA Platform.

## Repository Use Cases:
- Enable business analysts to test the 2018 HMDA Platform
- Provide files to check API returns
- Provide a resource for developers to use while implementing business rules in code
- Provide synthetic data files meeting the 2018 HMDA schema to be used in training


## Dependencies
- Python 3.5 or greater
- [Jupyter Notebooks](http://jupyter.org/): `pip install jupyter`
- [Pandas](http://pandas.pydata.org/): `pip install pandas`

## Generating Clean File
Clean files will pass the HMDA edits (business rules for data submission). These files are used as the base for generating files that will fail edits.
To generate clean files:
- `python generate_clean_files.py`: running [this script](https://github.com/cfpb/hmda-test-files/blob/master/python/generate_clean_files.py) will create the edits_files directory and a data file that will pass the HMDA edit checks. The file will have a number of rows set in the YAML [configuration file](https://github.com/cfpb/hmda-test-files/blob/master/python/config.yaml). Other variables, such as data ranges can also be set in this file.

## Generating Test Files
Test files will fail at least one (and sometimes more than one) edit. These files will be used as a double check for the implementation of the HMDA edits for the 2018 HMDA Platform. 

Creating test files is a two step process. The generation of edit test files requires a clean data file to be present. A clean file is created when [generate_clean_files](https://github.com/cfpb/hmda-test-files/blob/master/python/generate_clean_files.py) is run. Running [generate test files](https://github.com/cfpb/hmda-test-files/blob/master/python/generate_error_files.py) modifies the data from the clean file and saves it with the name of the edit check that it will fail. If edit files already exist with the same names as those produced by this script, they will be overwrriten.

To generate test files:
- `python generate_clean_files.py`: running [this script](https://github.com/cfpb/hmda-test-files/blob/master/python/generate_clean_files.py) creates clean synthetic data file. This data file passes HMDA edit rules. The data ranges used in file creation are configured by making changes to the [configuration file](https://github.com/cfpb/hmda-test-files/blob/master/python/config.yaml) which is written in YAML.
- `python generate_error_files`: running [this script](https://github.com/cfpb/hmda-test-files/blob/master/python/generate_error_files.py) produces a file that will fail conditions for each edit (other edits may also fail). These files are written to the appropriate directory based on edit type, such as /edits_files/syntax/s300.txt. The file name indicates which edit the file is designed to test. If an edit has multiple conditions, a file will be made for each condition in the format /edits_files/syntax/s301_1.txt.

## Repository Structure
- [Python](https://github.com/Kibrael/2018_test_files/tree/master/python):
    - Contains the notebooks and python scripts used to generate synthetic LAR data, perturb the data so that it fails specific business rules, and code to check that the produced files fail as expeced.

- [Schemas](https://github.com/Kibrael/2018_test_files/tree/master/schemas)
    - Contains JSON objects that represent the data structures for LAR and Transmittal Sheet as defined by the [2018 HMDA FIG](https://www.consumerfinance.gov/data-research/hmda/static/for-filers/2018/2018-HMDA-FIG.pdf)

- [Dependencies](https://github.com/Kibrael/2018_test_files/tree/master/dependancies)
    - Contains files used in the generation of synthetic LAR data.
        - Tract to CBSA data for 2015 (most current year)
        - A file containing a list of US ZIP codes

## Additional Utilities
In addition to test file creation features, the repository contains utility functions that work with existing test file data. These functions assist in creating test files with further customization, such as files with a large number of rows or files as part of a new institution. Most of these functions are located in python/utils.py. The functions included are:
- [write_file](https://github.com/cfpb/hmda-test-files/blob/ce12748672f83bd7ead396ccf0ed395dbb02a29a/python/utils.py#L23): Which writes TS and LAR data frames to a HMDA submission test file with a specified file path and directory. 
- [read_data_file](https://github.com/cfpb/hmda-test-files/blob/ce12748672f83bd7ead396ccf0ed395dbb02a29a/python/utils.py#L60): Which reads in a HMDA submission test file and outputs a TS and LAR data frame. 
- [unique_uli](https://github.com/cfpb/hmda-test-files/blob/ce12748672f83bd7ead396ccf0ed395dbb02a29a/python/utils.py#L83): Writes a set of unique ULI’s with check digits to a LAR data frame given an LEI input. 
- [new_lar_rows](https://github.com/cfpb/hmda-test-files/blob/ce12748672f83bd7ead396ccf0ed395dbb02a29a/python/utils.py#L111): Duplicates or retracts rows in a LAR data frame to produce a file with a certain number of rows. This function can create LAR data frames with large row counts. 
- [row_by_row_modification](https://github.com/cfpb/hmda-test-files/blob/ce12748672f83bd7ead396ccf0ed395dbb02a29a/python/utils.py#L147): This function changes a LAR data frame given changes specified in a yaml file. It allows users to test for minor changes in LAR data.
- [change_bank](https://github.com/cfpb/hmda-test-files/blob/ce12748672f83bd7ead396ccf0ed395dbb02a29a/python/utils.py#L147): Changes TS and LAR data frames to a new test institution with an institution name, LEI, and Tax ID. 
- [check_digit_gen](https://github.com/cfpb/hmda-test-files/blob/ce12748672f83bd7ead396ccf0ed395dbb02a29a/python/utils.py#L201): Generates and appends a check digit to a ULI.   


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
