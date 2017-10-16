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
- `python generate_test_files`: running [this script] (https://github.com/cfpb/hmda-test-files/blob/master/python/generate_error_files.py) produces a file that will fail conditions for each edit (other edits may also fail). These files are written to the appropriate directory based on edit type, such as /edits_files/syntax/s300.txt. The file name indicates which edit the file is designed to test. If an edit has multiple conditions, a file will be made for each condition in the format /edits_files/syntax/s301_1.txt.

## Repository Structure
- [Python](https://github.com/Kibrael/2018_test_files/tree/master/python):
    - Contains the notebooks and python scripts used to generate synthetic LAR data, perturb the data so that it fails specific business rules, and code to check that the produced files fail as expeced.

- [Schemas](https://github.com/Kibrael/2018_test_files/tree/master/schemas)
    - Contains JSON objects that represent the data structures for LAR and Transmittal Sheet as defined by the [2018 HMDA FIG](https://www.consumerfinance.gov/data-research/hmda/static/for-filers/2018/2018-HMDA-FIG.pdf)

- [Dependencies](https://github.com/Kibrael/2018_test_files/tree/master/dependancies)
    - Contains files used in the generation of synthetic LAR data.
        - Tract to CBSA data for 2015 (most current year)
        - A file containing a list of US ZIP codes


----
## Open source licensing info
1. [TERMS](TERMS.md)
2. [LICENSE](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)
----
