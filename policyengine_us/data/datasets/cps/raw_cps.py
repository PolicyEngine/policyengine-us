from io import BytesIO
from zipfile import ZipFile
from policyengine_core.data import PublicDataset
import pandas as pd
import requests
from tqdm import tqdm
from policyengine_us.data.storage import policyengine_us_MICRODATA_FOLDER

TAX_UNIT_COLUMNS = [
    "ACTC_CRD",
    "AGI",
    "CTC_CRD",
    "EIT_CRED",
    "FEDTAX_AC",
    "FEDTAX_BC",
    "MARG_TAX",
    "STATETAX_A",
    "STATETAX_B",
    "TAX_INC",
]

SPM_UNIT_COLUMNS = [
    "ACTC",
    "CAPHOUSESUB",
    "CAPWKCCXPNS",
    "CHILDCAREXPNS",
    "CHILDSUPPD",
    "EITC",
    "ENGVAL",
    "EQUIVSCALE",
    "FAMTYPE",
    "FEDTAX",
    "FEDTAXBC",
    "FICA",
    "GEOADJ",
    "HAGE",
    "HHISP",
    "HMARITALSTATUS",
    "HRACE",
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
    "WEIGHT",
    "WFOSTER22",
    "WICVAL",
    "WKXPNS",
    "WNEWHEAD",
    "WNEWPARENT",
    "WUI_LT15",
    "ID",
]
SPM_UNIT_COLUMNS = ["SPM_" + column for column in SPM_UNIT_COLUMNS]
PERSON_COLUMNS = [
    "PH_SEQ",
    "PF_SEQ",
    "P_SEQ",
    "TAX_ID",
    "SPM_ID",
    "A_FNLWGT",
    "A_LINENO",
    "A_SPOUSE",
    "A_AGE",
    "A_SEX",
    "PEDISEYE",
    "MRK",
    "WSAL_VAL",
    "INT_VAL",
    "SEMP_VAL",
    "FRSE_VAL",
    "DIV_VAL",
    "RNT_VAL",
    "SS_VAL",
    "UC_VAL",
    "ANN_VAL",
    "PNSN_VAL",
    "OI_OFF",
    "OI_VAL",
    "CSP_VAL",
    "PAW_VAL",
    "SSI_VAL",
    "RETCB_VAL",
    "CAP_VAL",
    "WICYN",
    "VET_VAL",
    "WC_VAL",
    "DIS_VAL1",
    "DIS_VAL2",
    "CHSP_VAL",
    "PHIP_VAL",
    "MOOP",
    "PEDISDRS",
    "PEDISEAR",
    "PEDISOUT",
    "PEDISPHY",
    "PEDISREM",
    "PEPAR1",
    "PEPAR2",
    "DIS_SC1",
    "DIS_SC2",
]


class RawCPS(PublicDataset):
    name = "raw_cps"
    label = "Raw CPS"
    folder_path = policyengine_us_MICRODATA_FOLDER
    is_openfisca_compatible = False

    def generate(self, year: int) -> pd.DataFrame:
        """Generates the raw CPS dataset.

        Args:
            year (int): The year of the raw CPS to use.
        """
        # Files are named for a year after the year the survey represents.
        # For example, the 2020 CPS was administered in March 2021, so it's
        # named 2021.
        file_year = int(year) + 1
        file_year_code = str(file_year)[-2:]

        CPS_URL_BY_YEAR = {
            2020: "https://www2.census.gov/programs-surveys/cps/datasets/2021/march/asecpub21csv.zip",
            2021: "https://www2.census.gov/programs-surveys/cps/datasets/2022/march/asecpub22csv.zip",
        }

        if year not in CPS_URL_BY_YEAR:
            raise ValueError(f"No raw CPS data URL known for year {year}.")

        url = CPS_URL_BY_YEAR[year]

        response = requests.get(url, stream=True)
        total_size_in_bytes = int(
            response.headers.get("content-length", 200e6)
        )
        progress_bar = tqdm(
            total=total_size_in_bytes,
            unit="iB",
            unit_scale=True,
            desc="Downloading ASEC",
        )
        if response.status_code == 404:
            raise FileNotFoundError(
                "Received a 404 response when fetching the data."
            )
        try:
            with BytesIO() as file, pd.HDFStore(
                self.file(year), mode="w"
            ) as storage:
                content_length_actual = 0
                for data in response.iter_content(int(1e6)):
                    progress_bar.update(len(data))
                    content_length_actual += len(data)
                    file.write(data)
                progress_bar.set_description("Downloaded ASEC")
                progress_bar.total = content_length_actual
                progress_bar.close()
                zipfile = ZipFile(file)
                with zipfile.open(f"pppub{file_year_code}.csv") as f:
                    storage["person"] = pd.read_csv(
                        f,
                        usecols=PERSON_COLUMNS
                        + SPM_UNIT_COLUMNS
                        + TAX_UNIT_COLUMNS,
                    ).fillna(0)
                    person = storage["person"]
                with zipfile.open(f"ffpub{file_year_code}.csv") as f:
                    person_family_id = person.PH_SEQ * 10 + person.PF_SEQ
                    family = pd.read_csv(f).fillna(0)
                    family_id = family.FH_SEQ * 10 + family.FFPOS
                    family = family[family_id.isin(person_family_id)]
                    storage["family"] = family
                with zipfile.open(f"hhpub{file_year_code}.csv") as f:
                    person_household_id = person.PH_SEQ
                    household = pd.read_csv(f).fillna(0)
                    household_id = household.H_SEQ
                    household = household[
                        household_id.isin(person_household_id)
                    ]
                    storage["household"] = household
                storage["tax_unit"] = RawCPS._create_tax_unit_table(person)
                storage["spm_unit"] = RawCPS._create_spm_unit_table(person)
        except Exception as e:
            self.remove(year)
            raise ValueError(
                f"Attempted to extract and save the CSV files, but encountered an error: {e} (removed the intermediate dataset)."
            )

    @staticmethod
    def _create_tax_unit_table(person: pd.DataFrame) -> pd.DataFrame:
        tax_unit_df = person[TAX_UNIT_COLUMNS].groupby(person.TAX_ID).sum()
        tax_unit_df["TAX_ID"] = tax_unit_df.index
        return tax_unit_df

    @staticmethod
    def _create_spm_unit_table(person: pd.DataFrame) -> pd.DataFrame:
        return person[SPM_UNIT_COLUMNS].groupby(person.SPM_ID).first()


RawCPS = RawCPS()
