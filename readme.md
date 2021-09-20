## Table of Contents
- [Purpose](https://github.com/cfpb/hmda-test-files#purpose)
- [Structure](https://github.com/cfpb/hmda-test-files#structure)
- [Dependancies](https://github.com/cfpb/hmda-test-files#dependencies)
- [Generating Clean Files](https://github.com/cfpb/hmda-test-files#generating-clean-files)
- [Generating Test Files](https://github.com/cfpb/hmda-test-files#generating-test-files)
- [Generating Large Files](https://github.com/cfpb/hmda-test-files#generating-large-files)
- [Generating Edit Reports](https://github.com/cfpb/hmda-test-files#generating-edit-reports)
- [Data Generation Notes](https://github.com/cfpb/hmda-test-files#data-generation-notes)


## Purpose and Scope:
This repository contains code used to generate synthetic LAR and TS files. The test files repository has file creation for the 2018 and 2019 collection years. 

Two types of files can be created: clean files and test files. Clean files will pass all edit checks in the FIG for the relevant year, while test files will fail the edit in the file name. Test files may also fail some additional edits, this is known behavior.

## Structure
Each year listed in the parent directory contains its own codebase for creating test files. Each year relates to a HMDA collection year. Test files are year specific due to changes in the HMDA FIG.

- [2018/python](2018/python) and [2019/python](2019/python) contain the notebooks and python scripts used to generate both clean and test files.

- [2018/schemas](2018/schemas) and [2019/schemas](2019/schemas) contain schemas for the LAR and TS in JSON format. These schemas are taken from the [2018 HMDA FIG](https://s3.amazonaws.com/cfpb-hmda-public/prod/help/2018-hmda-fig-2018-hmda-rule.pdf) and the [2019 HMDA FIG](https://s3.amazonaws.com/cfpb-hmda-public/prod/help/2019-hmda-fig.pdf)

- [2018/dependencies](2018/dependencies) and [2019/dependencies](2019/dependencies) contain supplemental data files used in the generation of clean and test files. 
       - Relevant FFIEC Census data, see [this repo](https://github.com/cfpb/hmda-census) for more information
       - A file containing a list of US ZIP codes


## Dependencies
- [Python 3.5 or greater](https://www.python.org/downloads/)
- [Jupyter Notebooks](http://jupyter.org/): `pip3 install jupyter`
- [Pandas](http://pandas.pydata.org/): `pip3 install pandas`
- Other required Python libraries can be installed with `pip3 install -r requirements.txt`


## Generating Clean Files

These files are used as the base for generating files that will fail edits. Running the following scripts will create the edits_files directory and a data file that will pass the HMDA edit checks. The file will have a number of rows set in a YAML clean file configuration for each directory. Other variables, such as data ranges can also be set in the configuration files.

Configuration values for clean files can be changed using the:
- [2021 Clean File Configuration](2021/python/configurations/clean_file_config.yaml)
- [2020 Clean File Configuration](2020/python/configurations/clean_file_config.yaml)
- [2019 Clean File Configuration](2019/python/configurations/clean_file_config.yaml)
- [2018 Clean File Configuration](2018/python/configurations/clean_file_config.yaml). 

Additional configuration options are available in the configuration folders by year:
- [2021](2021/python/configurations)
- [2020](2020/python/configurations)
- [2019](2019/python/configurations)
- [2018](2018/python/configurations)


For 2019, 2020, and 2021:
1. Navigate to the `<year>/python` directory
2. Run `python3 generate_clean_files.py`
4. The clean test file will be created with the following path: `{year}/edits_files/{bank name}/clean_files/{Bank Name}_clean_{row count}.txt`.

For 2018:
1. Navigate to the `2018/python` directory
2. Run `python3 generate_2018_clean_files.py`
3. The clean test file will be created in a new edits_files directory under `2018/edits_files/clean_files/{Bank Name}/` with the filename `clean_file_{Number or Rows}_{Bank Name}.txt`


## Generating Test Files
The generation of edit test files requires a clean data file to be present.[The steps above](readme.md/#generating-clean-files) outline the process to create the clean data files. 

Test files will be created using a clean file of the length specifid in the `file_length` value fo the [clean file configuration](2019/python/configurations/clean_file_config.yaml).

Test files will be written to sub directories based on the type of edit they fail:
`edits_files/{bank name}/test_files/{edit type}/{bank name}_{edit name}_{row count}.txt`

Existing test files of the same length will be overwritten.
These filepaths can be changed in [test filepaths configuration](2019/python/configurations/test_filepaths.yaml).


To create test files for 2019, 2020, and 2021: 
1. Navigate to the `<year>/python` directory.
2. Run `python3 generate_error_files.py`

To create test files for 2018: 
1. Navigate to the `2018/python` directory.
2. Run `python3 generate_2018_error_files.py`

The error files for testing syntax, validity, and quality edit test files will be created in the following diretories:  
	- Syntax: `{year}/edits_files/test_files/{Bank Name}/syntax`  
	- Validity: `{year}/edits_files/test_files/{Bank Name}/validity`  
	- Quality: `{year}/edits_files/test_files/{Bank Name}/quality`  
	- Quality (Adjusted to pass syntax and validity): `{year}/edits_files/test_files/{Bank Name}/quality_pass_s_v`  


## Generating Large Files 
Due to code design and the edit rules for the LAR data generating synthetic data files of large size was time prohibitive. The [large file generation script](2019/python/generate_large_files.py) takes a different approach by using a clean file base and copying rows until the desired file size is created.

To generate large files for 2019, 2020, and 2021: 
1. Navigate to the `<year>/python` directory
2. Run `python3 generate_large_files.py`

- To set the large file size for 2019 edit the `large_file_write_length` value in the [clean configuration](2019/python/configurations/clean_file_config.yaml).
To set the base file used to create large files edit the `large_file_base_length` value in the [clean configuration](2019/python/configurations/clean_file_config.yaml).
- To set the large file size for 2020, and 2021, edit the `large_file_write_length` value in the [2020 large configuration](2020/python/configurations/large_file_config.yaml),
or [2021 large configuration](2021/python/configurations/large_file_config.yaml).
To set the base file used to create large files edit the `large_file_base_length` value in the [2020 large configuration](2020/python/configurations/large_file_config.yaml),
  or [2021 large configuration](2021/python/configurations/large_file_config.yaml).
  - For 2020 and 2021, `large_file_base_length` value in `large_file_config.yaml` should correspond with `file_length` value in `bank1_config.yaml`,
  as the generated clean file being the base for generating the large file, and the filenames corresponds with record numbers.

*Note: the 2018 process is different than 2019.*
To generate large files for 2018: 
1. Navigate to the `2018/python` directory.
2. Adjust the [2018 File Large File Script Configuration](2018/python/configurations/test_filepaths.yaml) to specify bank name, lei, tax id, row count, output filepath, and output filename. 
3. Run `python3 large_test_files_script.py` to produce the large file. 


## Generating Edit Reports
Edit reports provide a summary of the syntax, validity, or quality edits passed or failed in a test submission file. The edit report contains the following fields. 

* edit name
* status (pass/fail)
* number of rows failed
* ULIs/NULIs of rows that failed (as a list). 

Edit reports can be generated for any synthetic submission file. Configuration options include (with defaulted values):

To generate edit reports for 2019 and 2020:  
1. Navigate to the `<year>/python` directory.
2. Adjust the Edit Report Configuration to specify output. 
	- [2021](2021/python/configurations/edit_report_config.yaml)
	- [2020](2020/python/configurations/edit_report_config.yaml)
	- [2019](2019/python/configurations/edit_report_config.yaml)
3. Run `python3 generate_edit_report.py` to produce the edit report in the directory according to the configuration file. 

To generate edit reports for 2018:  
1. Navigate to the 2018/python directory.
2. Adjust the [2018 Edit Report Configuration](2018/python/configurations/edit_report_config.yaml) to specify output. 
3. Run `python3 generate_edit_report.py` to produce the edit report in the directory according to the configuration file. 

----
## Data Generation Notes:
The default values for Bank0 are listed below. 

- Name: `Bank0`
- LEI: `B90YWS6AFX2LGWOXJ1LD`
- Tax ID: `01-0123456`

The default values for Bank1 are listed below. 

- Name: `Bank1`
- LEI: `BANK1LEIFORTEST12345`
- Tax ID: `02-1234567`

Other test bank LEIs:
- BANK3LEIFORTEST12345
- BANK4LEIFORTEST12345
- 999999LE3ZOZXUS7W648
- 28133080042813308004

----
## Open source licensing info
1. [TERMS](TERMS.md)
2. [LICENSE](https://github.com/cfpb/hmda-platform/blob/master/LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)
----
