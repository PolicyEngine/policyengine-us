import pandas as pd
import requests
from tqdm import tqdm
from pathlib import Path
import os
import zipfile
import shutil

STATE_NAMES = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]
STATE_CODES = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]
STATE_CODES = [x.lower() for x in STATE_CODES]
DATA_FOLDER = Path("data")
DATA_FOLDER.mkdir(exist_ok=True)

dfs = []
for state_name, state_code in tqdm(
    zip(STATE_NAMES, STATE_CODES), desc="Downloading Census data"
):
    data_url = f"https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/{state_name}/{state_code}2020.pl.zip"
    # Download the file and save to a folder called "block_level_population_data_by_state/"
    r = requests.get(data_url)
    with open(DATA_FOLDER / f"{state_code}2020.pl.zip", "wb") as f:
        f.write(r.content)
    # Unzip the file
    with zipfile.ZipFile(
        DATA_FOLDER / f"{state_code}2020.pl.zip", "r"
    ) as zip_ref:
        zip_ref.extractall(DATA_FOLDER / f"{state_code}2020.pl")
    # Delete the zip file
    os.remove(DATA_FOLDER / f"{state_code}2020.pl.zip")
    # Read the file
    df = pd.read_csv(
        DATA_FOLDER / f"{state_code}2020.pl/{state_code}geo2020.pl",
        sep="|",
        low_memory=False,
        encoding="ISO-8859-1",
    )
    df["state"] = state_code
    dfs += [df]
    full_df = pd.concat(dfs)
    full_df.to_csv(DATA_FOLDER / "50_state_block_data.csv", index=False)
    shutil.rmtree(DATA_FOLDER / f"{state_code}2020.pl")
