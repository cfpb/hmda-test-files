# Repository Purpose:
This repository contains code used to generate synthetic LAR files. These files will be used to support the development of the 2018 HMDA data submission platform. The success of the HMDA program requires that the data submitted meet the technical and business requirements of the HMDA Platform. The code and test files in this repository will provide a standardized means of checking the implementation of the business rules for data submission in the HMDA Platform.

## Repository Use Cases:
- Enable business analysts to test the 2018 HMDA Platform
- Provide files to check API returns
- Provide a resource for developers to use while implementing business rules in code


## Dependancies
- US Census tract to CBSA data for the most current year
- Python 3.5 or greater
- TBD: A full list of packages used can be found in [requirements.txt](https://github.com/cfpb/hmda-viz-prototype/blob/gh-pages/processing/requirements.txt)
    - `pip install -r requirements.txt` to install the requirements

## Repository Workflow
- The [Test file maker](https://github.com/Kibrael/2018_test_files/blob/master/python/2018_test_file_maker.ipynb) uses the classes [lar_generator]() and [lar_constraints]() to first create a Python dictionary of synthetic data, and then apply business rules to ensure that the data are valid for submission.
- The valid files are then perturbed so that the data is invalid and fails for specific edits. A file will be created for each edit (and possibley each condition specified in an edit). These files will have known fail returns to enable implementation of business rules and then test the rules once implemented. (not finished)
- A Python rules engine is then used to validate the test files for each edit. Ideally, the files will fail only the edit for which they are named, however, this may not be possible given the large number of rules that implicate multiple fields. (not finished)

## Repository Structure
- [Python](https://github.com/Kibrael/2018_test_files/tree/master/python):
    - Contains the notebooks and python scripts used to generate synthetic LAR data, perturb the data so that it fails specific business rules, and code to check that the produced files fail as expeced.

- [Schemas](https://github.com/Kibrael/2018_test_files/tree/master/schemas)
    - Contains JSON objects that represent the data structures for LAR and Transmittal Sheet as defined by the [2018 HMDA FIG](https://www.consumerfinance.gov/data-research/hmda/static/for-filers/2018/2018-HMDA-FIG.pdf)

- [Dependancies](https://github.com/Kibrael/2018_test_files/tree/master/dependancies)
    - Contains files used in the generation of synthetic LAR data.
        - Currently contains tract to CBSA data for 2015 (most current year)


----
## Open source licensing info
1. [TERMS](TERMS.md)
2. [LICENSE](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)
----
