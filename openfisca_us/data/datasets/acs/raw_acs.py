from io import BytesIO
import logging
from zipfile import ZipFile
import pandas as pd
from openfisca_tools.data import PublicDataset
import h5py
import requests
from tqdm import tqdm
from openfisca_us.data.datasets.cps.raw_cps import RawCPS
from openfisca_us.data.storage import OPENFISCA_US_MICRODATA_FOLDER
from pandas import DataFrame, Series
import numpy as np

logging.getLogger().setLevel(logging.INFO)


class RawACS(PublicDataset):
    name = "raw_acs"
    label = "Raw ACS"
    is_openfisca_compatible = False
    folder_path = OPENFISCA_US_MICRODATA_FOLDER

    def generate(self, year: int) -> None:
        year = int(year)
        if year in self.years:
            self.remove(year)

        
        spm_url = f"https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_{year}_pu.dta"
        person_url = f"https://www2.census.gov/programs-surveys/acs/data/pums/{year}/1-Year/csv_pus.zip"
        household_url = f"https://www2.census.gov/programs-surveys/acs/data/pums/{year}/1-Year/csv_hus.zip"
        try:
            with pd.HDFStore(RawACS.file(year)) as storage:
                # Household file
                logging.info(f"Downloading household file")
                storage["household"] = concat_zipped_csvs(household_url, "psam_hus")
                # Person file
                logging.info(f"Downloading person file")
                storage["person"] = concat_zipped_csvs(person_url, "psam_pus")
                # SPM unit file
                logging.info(f"Downloading SPM unit file")
                spm_person = pd.read_stata(spm_url).fillna(0)
                spm_person.columns = spm_person.columns.str.upper()
                storage["spm_unit"] = create_spm_unit_table(spm_person)
        except Exception as e:
            RawACS.remove(year)
            raise ValueError(
                f"Attempted to extract and save the CSV files, but encountered an error: {e}"
            )

RawACS = RawACS()

def concat_zipped_csvs(url: str, prefix: str) -> pd.DataFrame:
    # Creates a DataFrame with the two csvs inside a zip file from a URL.
    req = requests.get(url, stream=True)
    with BytesIO() as f:
        pbar = tqdm()
        for chunk in req.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                pbar.update (len(chunk))
                f.write(chunk)
        f.seek(0)
        zf = ZipFile(f)
        a = pd.read_csv(zf.open(prefix + "a.csv"))
        b = pd.read_csv(zf.open(prefix + "b.csv"))
    res = pd.concat([a, b]).fillna(0)
    res.columns = res.columns.str.upper()
    return res


def create_spm_unit_table(person: pd.DataFrame) -> pd.DataFrame:
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
    return (
        person[["SPM_" + column for column in SPM_UNIT_COLUMNS]]
        .groupby(person.SPM_ID)
        .first()
    )
