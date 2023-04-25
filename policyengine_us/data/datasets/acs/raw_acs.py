from io import BytesIO
import logging
from typing import List
from zipfile import ZipFile
import pandas as pd
from policyengine_core.data import PublicDataset
import requests
from tqdm import tqdm
from policyengine_us.data.storage import policyengine_us_MICRODATA_FOLDER


logging.getLogger().setLevel(logging.INFO)

PERSON_COLUMNS = [
    "SERIALNO",  # Household ID
    "SPORDER",  # Person number within household
    "PWGTP",  # Person weight
    "AGEP",  # Age
    "CIT",  # Citizenship
    "MAR",  # Marital status
    "WAGP",  # Wage/salary
    "SSP",  # Social security income
    "SSIP",  # Supplemental security income
    "SEX",  # Sex
    "SEMP",  # Self-employment income
    "SCHL",  # Educational attainment
    "RETP",  # Retirement income
    "PAP",  # Public assistance income
    "OIP",  # Other income
    "PERNP",  # Total earnings
    "PINCP",  # Total income
    "POVPIP",  # Income-to-poverty line percentage
    "RAC1P",  # Race
]

HOUSEHOLD_COLUMNS = [
    "SERIALNO",  # Household ID
    "PUMA",  # PUMA area code
    "ST",  # State code
    "ADJHSG",  # Adjustment factor for housing dollar amounts
    "ADJINC",  # Adjustment factor for income
    "WGTP",  # Household weight
    "NP",  # Number of persons in household
    "BDSP",  # Number of bedrooms
    "ELEP",  # Electricity monthly cost
    "FULP",  # Fuel monthly cost
    "GASP",  # Gas monthly cost
    "RMSP",  # Number of rooms
    "RNTP",  # Monthly rent
    "TEN",  # Tenure
    "VEH",  # Number of vehicles
    "FINCP",  # Total income
    "GRNTP",  # Gross rent
]


class RawACS(PublicDataset):
    name = "raw_acs"
    label = "Raw ACS"
    is_openfisca_compatible = False
    folder_path = policyengine_us_MICRODATA_FOLDER

    def generate(self, year: int) -> None:
        year = int(year)
        if year in self.years:
            self.remove(year)

        spm_url = f"https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_{year}_pu.dta"
        person_url = f"https://www2.census.gov/programs-surveys/acs/data/pums/{year}/1-Year/csv_pus.zip"
        household_url = f"https://www2.census.gov/programs-surveys/acs/data/pums/{year}/1-Year/csv_hus.zip"

        # The data dictionary for 2019 can be found here: https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2019.pdf

        try:
            with pd.HDFStore(RawACS.file(year)) as storage:
                # Household file
                logging.info(f"Downloading household file")
                household = concat_zipped_csvs(
                    household_url, "psam_hus", HOUSEHOLD_COLUMNS
                )
                # Remove group quarters (zero weight)
                household = household[
                    ~household.SERIALNO.str.contains("2019GQ")
                ]
                household["SERIALNO"] = household["SERIALNO"].apply(
                    lambda x: int(x.replace("2019HU", ""))
                )
                storage["household"] = household
                # Person file
                logging.info(f"Downloading person file")
                person = concat_zipped_csvs(
                    person_url, "psam_pus", PERSON_COLUMNS
                )
                person = person[~person.SERIALNO.str.contains("2019GQ")]
                person["SERIALNO"] = person["SERIALNO"].apply(
                    lambda x: int(x.replace("2019HU", ""))
                )
                storage["person"] = person
                # SPM unit file
                logging.info(f"Downloading SPM unit file")
                spm_person = pd.read_stata(spm_url).fillna(0)
                spm_person.columns = spm_person.columns.str.upper()
                create_spm_unit_table(storage, spm_person)
        except Exception as e:
            RawACS.remove(year)
            logging.error(
                f"Attempted to extract and save the CSV files, but encountered an error: {e}"
            )
            raise e


RawACS = RawACS()


def concat_zipped_csvs(
    url: str, prefix: str, columns: List[str]
) -> pd.DataFrame:
    """Downloads the ACS microdata, which is a zip file containing two halves in CSV format.

    Args:
        url (str): The URL of the data server.
        prefix (str): The prefix of the filenames, before a/b.csv.
        columns (List[str]): The columns to filter (avoids hitting memory limits).

    Returns:
        pd.DataFrame: The concatenated DataFrame.
    """
    req = requests.get(url, stream=True)
    with BytesIO() as f:
        pbar = tqdm()
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                pbar.update(len(chunk))
                f.write(chunk)
        f.seek(0)
        zf = ZipFile(f)
        logging.info(f"Loading the first half of the dataset")
        a = pd.read_csv(zf.open(prefix + "a.csv"), usecols=columns)
        logging.info(f"Loading the second half of the dataset")
        b = pd.read_csv(zf.open(prefix + "b.csv"), usecols=columns)
    logging.info(f"Concatenating datasets")
    res = pd.concat([a, b]).fillna(0)
    res.columns = res.columns.str.upper()
    return res


def create_spm_unit_table(storage: pd.HDFStore, person: pd.DataFrame) -> None:
    SPM_UNIT_COLUMNS = [
        "CAPHOUSESUB",
        "CAPWKCCXPNS",
        "CHILDCAREXPNS",
        "EITC",
        "ENGVAL",
        "EQUIVSCALE",
        "FEDTAX",
        "FEDTAXBC",
        "FICA",
        "GEOADJ",
        "MEDXPNS",
        "NUMADULTS",
        "NUMKIDS",
        "NUMPER",
        "POOR",
        "POVTHRESHOLD",
        "RESOURCES",
        "SCHLUNCH",
        "SNAPSUB",
        "STTAX",
        "TENMORTSTATUS",
        "TOTVAL",
        "WCOHABIT",
        "WICVAL",
        "WKXPNS",
        "WUI_LT15",
        "ID",
    ]
    spm_table = (
        person[["SPM_" + column for column in SPM_UNIT_COLUMNS]]
        .groupby(person.SPM_ID)
        .first()
    )

    original_person_table = storage["person"]
    # Ensure that join keys are the same type.
    JOIN_COLUMNS = ["SERIALNO", "SPORDER"]
    original_person_table[JOIN_COLUMNS] = original_person_table[
        JOIN_COLUMNS
    ].astype(int)
    person[JOIN_COLUMNS] = person[JOIN_COLUMNS].astype(int)
    # Add SPM_ID from the SPM person table to the original person table.
    combined_person_table = pd.merge(
        original_person_table,
        person[JOIN_COLUMNS + ["SPM_ID"]],
        on=JOIN_COLUMNS,
    )

    storage["person"] = combined_person_table
    storage["spm_unit"] = spm_table
