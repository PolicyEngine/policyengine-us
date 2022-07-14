# data/geography

This folder contains scripts and datasets used for geographic mappings and imputations.

## `create_zip_code_dataset.py`

This script generates the dataset `zip_codes.csv.gz`, which contains a row for every ZIP code, providing its:
* ZIP code tabulation area
* County
* Population
* State

The dataset is pre-generated and stored in the repo, so it'd only need to be updated when new ACS 5-year estimates come out.
