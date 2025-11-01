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

AMI_COLUMNS = [
    "stusps",  # State Postal Code
    "state",  # 2 Digit State FIPS Code
    "state_name",  # State Name
    "hud_area_code",  # HUD Specific Area Code
    "county",  # 3 Digit County FIPS Code
    "County_Name",  # County Name
    "county_town_name",  # Town Name for areas in New England (Connecticut, Maine, Massachusetts, New Hampshire, Rhode Island, Vermont)- Otherwise, County Name
    "metro",  # 1 if area is in a Metropolitan Statistical Area- 0 if not
    "HUD_Area_Name",  # HUD Area Name
    "fips",  # Concatenated 2 Digit State FIPS Code, 3 Digit County FIPS Code, and 5 Digit County Subdivision FIPS Code
    "median2023",  # 2023 HUD Area Median Family Income   --- NOTE: FIX FOR all years
    "l50_1",  # 2023 1-Person Very Low (50%) Income Limit
    "l50_2",  # 2023 2-Person Very Low (50%) Income Limit
    "l50_3",  # 2023 3-Person Very Low (50%) Income Limit
    "l50_4",  # 2023 4-Person Very Low (50%) Income Limit
    "l50_5",  # 2023 5-Person Very Low (50%) Income Limit
    "l50_6",  # 2023 6-Person Very Low (50%) Income Limit
    "l50_7",  # 2023 7-Person Very Low (50%) Income Limit
    "l50_8",  # 2023 8-Person Very Low (50%) Income Limit
    "ELI_1",  # 2023 1-Person Extremely Low (30%) Income Limit
    "ELI_2",  # 2023 2-Person Extremely Low (30%) Income Limit
    "ELI_3",  # 2023 3-Person Extremely Low (30%) Income Limit
    "ELI_4",  # 2023 4-Person Extremely Low (30%) Income Limit
    "ELI_5",  # 2023 5-Person Extremely Low (30%) Income Limit
    "ELI_6",  # 2023 6-Person Extremely Low (30%) Income Limit
    "ELI_7",  # 2023 7-Person Extremely Low (30%) Income Limit
    "ELI_8",  # 2023 8-Person Extremely Low (30%) Income Limit
    "l80_1",  # 2023 1-Person  Low (80%) Income Limit
    "l80_2",  # 2023 2-Person  Low (80%) Income Limit
    "l80_3",  # 2023 3-Person  Low (80%) Income Limit
    "l80_4",  # 2023 4-Person  Low (80%) Income Limit
    "l80_5",  # 2023 5-Person  Low (80%) Income Limit
    "l80_6",  # 2023 6-Person  Low (80%) Income Limit
    "l80_7",  # 2023 7-Person  Low (80%) Income Limit
    "l80_8",  # 2023 8-Person  Low (80%) Income Limit
]

FMR_COLUMNS = [
    "fips",  # Concatenated 2 Digit State FIPS Code, 3 Digit County FIPS Code, and 5 Digit County Subdivision FIPS Code
    "hud_area_name",  # HUD Area Name
    "hud_area_code",  # HUD Specific Area Code
    "countyname",  # County Name
    "county_town_name",  # Town Name for areas in New England (Connecticut, Maine, Massachusetts, New Hampshire, Rhode Island, Vermont)- Otherwise, County Name
    "state",  # 2 Digit State FIPS Code
    "state_alpha",  # State Postal Code
    "metro",  # 1 if area is in a Metropolitan Statistical Area- 0 if not
    "pop2020",  # 2020 Population
    "fmr_0",  # 0-Bedroom Fair Market Rent
    "fmr_1",  # 1-Bedroom Fair Market Rent
    "fmr_2",  # 2-Bedroom Fair Market Rent
    "fmr_3",  # 3-Bedroom Fair Market Rent
    "fmr_4",  # 4-Bedroom Fair Market Rent
]



class RawHUDUSER(PublicDataset):
    class RawHUDUSER(PublicDataset):
        name = "raw_huduser"
        label = "Raw HUDUSER"
        is_openfisca_compatible = False
        folder_path = policyengine_us_MICRODATA_FOLDER

        def generate(self, year: int) -> None:
            year = int(year)
            if year in self.years:
                self.remove(year)
                
            yearShort = year % 100            
            #spm_url = f"https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_{year}_pu.dta"
            ami_url = f"https://www.huduser.gov/portal/datasets/il/il{yearShort}/Section8-FY{yearShort}.xlsx"
            fmr_url = f"https://www.huduser.gov/portal/datasets/fmr/fmr{year}/FY{yearShort}_FMRs.xlsx"
            # The data dictionary for 2019 can be found here: https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2019.pdf

            try:
                with pd.HDFStore(RawHUDUSER.file(year)) as storage:
                    # Household file
                    logging.info(f"Downloading ami file")
                    ami_data = pd.read_excel(ami_url, usecols=AMI_COLUMNS)
                    # Remove group quarters (zero weight)
                    #     household = household[
                    #         ~household.SERIALNO.str.contains("2019GQ")
                    #     ]
                    # household["SERIALNO"] = household["SERIALNO"].apply(
                    #     lambda x: int(x.replace("2019HU", ""))
                    # )
                    storage["ami"] = ami_data
                    # Person file
                    logging.info(f"Downloading fmr file")
                    fmr_data = pd.read_excel(fmr_url, usecols=FMR_COLUMNS)
                    # person = person[~person.SERIALNO.str.contains("2019GQ")]
                    # person["SERIALNO"] = person["SERIALNO"].apply(
                    #     lambda x: int(x.replace("2019HU", ""))
                    # )
                    storage["fmr"] = fmr_data

                    # Assuming the common column is "fips"
                    combined_data = pd.merge(ami_data, fmr_data, on="fips")

                    # Dropping repeated columns
                    combined_data = combined_data.loc[:, ~combined_data.columns.duplicated()]

                    storage["huduser"] = combined_data

                    # SPM unit file
                    # logging.info(f"Downloading SPM unit file")
                    # spm_person = pd.read_stata(spm_url).fillna(0)
                    # spm_person.columns = spm_person.columns.str.upper()
                    # create_spm_unit_table(storage, spm_person)
            except Exception as e:
                RawHUDUSER.remove(year)
                logging.error(
                    f"Attempted to extract and save the CSV files, but encountered an error: {e}"
                )
                raise e


RawHUDUSER = RawHUDUSER()


# def concat_zipped_csvs(
#     url: str, prefix: str, columns: List[str]
# ) -> pd.DataFrame:
#     """Downloads the HUDUSER microdata, which is a zip file containing two halves in CSV format.

#     Args:
#         url (str): The URL of the data server.
#         prefix (str): The prefix of the filenames, before a/b.csv.
#         columns (List[str]): The columns to filter (avoids hitting memory limits).

#     Returns:
#         pd.DataFrame: The concatenated DataFrame.
#     """
#     req = requests.get(url, stream=True)
#     with BytesIO() as f:
#         pbar = tqdm()
#         for chunk in req.iter_content(chunk_size=1024):
#             if chunk:  # filter out keep-alive new chunks
#                 pbar.update(len(chunk))
#                 f.write(chunk)
#         f.seek(0)
#         zf = ZipFile(f)
#         logging.info(f"Loading the first half of the dataset")
#         a = pd.read_csv(zf.open(prefix + "a.csv"), usecols=columns)
#         logging.info(f"Loading the second half of the dataset")
#         b = pd.read_csv(zf.open(prefix + "b.csv"), usecols=columns)
#     logging.info(f"Concatenating datasets")
#     res = pd.concat([a, b]).fillna(0)
#     res.columns = res.columns.str.upper()
#     return res


# def create_spm_unit_table(storage: pd.HDFStore, person: pd.DataFrame) -> None:
#     SPM_UNIT_COLUMNS = [
#         "CAPHOUSESUB",
#         "CAPWKCCXPNS",
#         "CHILDCAREXPNS",
#         "EITC",
#         "ENGVAL",
#         "EQUIVSCALE",
#         "FEDTAX",
#         "FEDTAXBC",
#         "FICA",
#         "GEOADJ",
#         "MEDXPNS",
#         "NUMADULTS",
#         "NUMKIDS",
#         "NUMPER",
#         "POOR",
#         "POVTHRESHOLD",
#         "RESOURCES",
#         "SCHLUNCH",
#         "SNAPSUB",
#         "STTAX",
#         "TENMORTSTATUS",
#         "TOTVAL",
#         "WCOHABIT",
#         "WICVAL",
#         "WKXPNS",
#         "WUI_LT15",
#         "ID",
#     ]
#     spm_table = (
#         person[["SPM_" + column for column in SPM_UNIT_COLUMNS]]
#         .groupby(person.SPM_ID)
#         .first()
#     )

#     original_person_table = storage["person"]
#     # Ensure that join keys are the same type.
#     JOIN_COLUMNS = ["SERIALNO", "SPORDER"]
#     original_person_table[JOIN_COLUMNS] = original_person_table[
#         JOIN_COLUMNS
#     ].astype(int)
#     person[JOIN_COLUMNS] = person[JOIN_COLUMNS].astype(int)
#     # Add SPM_ID from the SPM person table to the original person table.
#     combined_person_table = pd.merge(
#         original_person_table,
#         person[JOIN_COLUMNS + ["SPM_ID"]],
#         on=JOIN_COLUMNS,
#     )

#     storage["person"] = combined_person_table
#     storage["spm_unit"] = spm_table
