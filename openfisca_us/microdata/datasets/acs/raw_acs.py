from openfisca_us.microdata.utils import *
import requests
from io import BytesIO
import pandas as pd


@dataset
class RawACS:
    name = "raw_acs"

    def generate(year: int) -> None:
        url = f"https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_{year}_pu.dta"
        try:
            with pd.HDFStore(RawACS.file(year)) as storage:
                person = pd.read_stata(url).fillna(0)
                person.columns = person.columns.str.upper()
                storage["person"] = person
                storage["spm_unit"] = create_SPM_unit_table(person)
                storage["household"] = create_household_table(person)
        except Exception as e:
            RawACS.remove(year)
            raise ValueError(
                f"Attempted to extract and save the CSV files, but encountered an error: {e}"
            )


def create_SPM_unit_table(person: pd.DataFrame) -> pd.DataFrame:
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


def create_household_table(person: pd.DataFrame) -> pd.DataFrame:
    return person[["SERIALNO", "ST", "PUMA"]].groupby(person.SERIALNO).first()
