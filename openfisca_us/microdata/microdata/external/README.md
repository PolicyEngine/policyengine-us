# external

This folder will contain `*.h5` files that hold datasets not compatible with OpenFisca-US - for example, the raw CPS or ACS data, as it is still preferable to contain these datasets in a single file rather than many CSV files in nested folders. Each non-compatible dataset file should use the same schema - a Pandas HD5 store, where each file is loaded to a dictionary-like object in which each table of the dataset is a DataFrame.
