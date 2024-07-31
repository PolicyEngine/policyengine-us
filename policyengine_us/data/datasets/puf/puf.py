from policyengine_core.data import Dataset
import numpy as np
from policyengine_us.data.storage import STORAGE_FOLDER
from tqdm import tqdm

EXTRA_PUF_VARIABLES = [
    "e02000",
    "e26270",
    "e19200",
    "e18500",
    "e19800",
    "e20400",
    "e20100",
    "e00700",
    "e03270",
    "e24515",
    "e03300",
    "e07300",
    "e62900",
    "e32800",
    "e87530",
    "e03240",
    "e01100",
    "e01200",
    "e24518",
    "e09900",
    "e27200",
    "e03290",
    "e58990",
    "e03230",
    "e07400",
    "e11200",
    "e07260",
    "e07240",
    "e07600",
    "e03220",
    "p08000",
    "e03400",
    "e09800",
    "e09700",
    "e03500",
    "e87521",
]


class PUF(Dataset):
    time_period = None
    data_format = Dataset.ARRAYS

    def generate(
        self, puf_file_path: str = None, puf_demographics_path: str = None
    ):
        # First pass: single person tax units.
        from policyengine_us.data.datasets.cps.enhanced_cps.process_puf import (
            load_puf,
            impute_missing_demographics,
            uprate_puf,
        )

        puf, demographics = load_puf(
            puf_file_path=puf_file_path, puf_demographics_path=None
        )
        puf = uprate_puf(puf, self.time_period)
        puf = impute_missing_demographics(puf, demographics)

        VARIABLES = [
            "person_id",
            "tax_unit_id",
            "marital_unit_id",
            "spm_unit_id",
            "family_id",
            "household_id",
            "person_tax_unit_id",
            "person_marital_unit_id",
            "person_spm_unit_id",
            "person_family_id",
            "person_household_id",
            "age",
            "employment_income",
            "household_weight",
            "is_male",
        ] + list(FINANCE_VARIABLE_RENAMES.values())

        self.holder = {variable: [] for variable in VARIABLES}

        i = 0
        for _, row in tqdm(puf.iterrows(), total=len(puf)):
            i += 1
            tax_unit_id = i
            self.add_tax_unit(row, tax_unit_id)
            self.add_filer(row, tax_unit_id)
            if row["marital_filing_status"] == 2:
                self.add_spouse(row, tax_unit_id)

            DEPENDENT_COLUMNS = [
                "exemptions_children_living_at_home",
                "exemptions_children_living_away_from_home",
                "exemptions_other_dependents",
            ]
            count_dependents = int(sum(row[dep] for dep in DEPENDENT_COLUMNS))

            for j in range(count_dependents):
                self.add_dependent(row, tax_unit_id, j)

        groups_assumed_to_be_tax_unit_like = [
            "family",
            "spm_unit",
            "household",
        ]

        for group in groups_assumed_to_be_tax_unit_like:
            self.holder[f"{group}_id"] = self.holder["tax_unit_id"]
            self.holder[f"person_{group}_id"] = self.holder[
                "person_tax_unit_id"
            ]

        for key in self.holder:
            self.holder[key] = np.array(self.holder[key]).astype(float)

        self.save_dataset(self.holder)

    def add_tax_unit(self, row, tax_unit_id):
        self.holder["tax_unit_id"].append(tax_unit_id)

    def add_filer(self, row, tax_unit_id):
        person_id = int(tax_unit_id * 1e2 + 1)
        self.holder["person_id"].append(person_id)
        self.holder["person_tax_unit_id"].append(tax_unit_id)
        self.holder["person_marital_unit_id"].append(person_id)
        self.holder["marital_unit_id"].append(person_id)

        self.holder["age"].append(
            decode_age_filer(row["age_range_primary_filer"])
        )

        earnings_split = row["earnings_split_joint_returns"]
        if earnings_split > 0:
            SPLIT_DECODES = {
                1: 0,
                2: 0.25,
                3: 0.75,
                4: 1,
            }
            lower = SPLIT_DECODES[earnings_split]
            upper = SPLIT_DECODES[earnings_split + 1]
            earnings_percentage = 1 - np.random.uniform(lower, upper)
        else:
            earnings_percentage = 1

        self.holder["employment_income"].append(
            row["employment_income"] * earnings_percentage
        )

        self.holder["household_weight"].append(row["decimal_weight"])

        self.holder["is_male"].append(row["gender_primary_filer"] == 1)

        for key in FINANCE_VARIABLE_RENAMES:
            self.holder[FINANCE_VARIABLE_RENAMES[key]].append(row[key])

    def add_spouse(self, row, tax_unit_id):
        person_id = int(tax_unit_id * 1e2 + 2)
        self.holder["person_id"].append(person_id)
        self.holder["person_tax_unit_id"].append(tax_unit_id)
        self.holder["person_marital_unit_id"].append(person_id - 1)

        self.holder["age"].append(
            self.holder["age"][-1]
        )  # Assume same age as filer for now

        earnings_split = row["earnings_split_joint_returns"]
        if earnings_split > 0:
            SPLIT_DECODES = {
                1: 0,
                2: 0.25,
                3: 0.75,
                4: 1,
            }
            lower = SPLIT_DECODES[earnings_split]
            upper = SPLIT_DECODES[earnings_split + 1]
            earnings_percentage = np.random.uniform(lower, upper)
        else:
            earnings_percentage = 0

        self.holder["employment_income"].append(
            row["employment_income"] * earnings_percentage
        )

        # 96% of joint filers are opposite-gender

        is_opposite_gender = np.random.uniform() < 0.96
        opposite_gender_code = 0 if row["gender_primary_filer"] == 1 else 1
        same_gender_code = 1 - opposite_gender_code
        self.holder["is_male"].append(
            opposite_gender_code if is_opposite_gender else same_gender_code
        )

        for key in FINANCE_VARIABLE_RENAMES:
            self.holder[FINANCE_VARIABLE_RENAMES[key]].append(0)

    def add_dependent(self, row, tax_unit_id, dependent_id):
        person_id = int(tax_unit_id * 1e2 + 3 + dependent_id)
        self.holder["person_id"].append(person_id)
        self.holder["person_tax_unit_id"].append(tax_unit_id)
        self.holder["person_marital_unit_id"].append(person_id)
        self.holder["marital_unit_id"].append(person_id)

        self.holder["age"].append(
            decode_age_dependent(row[f"age_dependent_{dependent_id + 1}"])
        )
        self.holder["employment_income"].append(0)

        for key in FINANCE_VARIABLE_RENAMES:
            self.holder[FINANCE_VARIABLE_RENAMES[key]].append(0)

        self.holder["is_male"].append(np.random.choice([0, 1]))


class PUF_2022(PUF):
    label = "PUF (2022)"
    name = "puf_2022"
    time_period = 2022
    file_path = STORAGE_FOLDER / "puf_2022.h5"
    url = "release://policyengine/non-public-microdata/puf-2022/puf_2022.h5"


class PUF_2015(PUF):
    label = "PUF (2015)"
    name = "puf_2015"
    time_period = 2015
    file_path = STORAGE_FOLDER / "puf_2015.h5"


FINANCE_VARIABLE_RENAMES = dict(
    self_employment_income="self_employment_income",
    taxable_interest_income="taxable_interest_income",
    tax_exempt_interest_income="tax_exempt_interest_income",
    qualified_dividend_income="qualified_dividend_income",
    non_qualified_dividend_income="non_qualified_dividend_income",
    taxable_pension_income="taxable_pension_income",
    social_security="social_security",
    long_term_capital_gains="long_term_capital_gains",
    short_term_capital_gains="short_term_capital_gains",
    rental_income="rental_income",
    farm_rent_income="farm_rent_income",
    farm_income="farm_income",
    partnership_s_corp_income="partnership_s_corp_income",
    schedule_e_net_income_loss="schedule_e_net_income",
)

FINANCE_VARIABLE_RENAMES.update(
    {variable: variable for variable in EXTRA_PUF_VARIABLES}
)


def decode_age_filer(age_range):
    if age_range == 0:
        return 40
    AGERANGE_FILER_DECODE = {
        1: 0,
        2: 26,
        3: 35,
        4: 45,
        5: 55,
        6: 65,
        7: 80,
    }
    lower = AGERANGE_FILER_DECODE[age_range]
    upper = AGERANGE_FILER_DECODE[age_range + 1]
    return np.random.randint(lower, upper)


def decode_age_dependent(age_range):
    if age_range == 0:
        return 0
    AGERANGE_DEPENDENT_DECODE = {
        0: 0,
        1: 0,
        2: 5,
        3: 13,
        4: 17,
        5: 19,
        6: 25,
        7: 30,
    }
    lower = AGERANGE_DEPENDENT_DECODE[age_range]
    upper = AGERANGE_DEPENDENT_DECODE[age_range + 1]
    return np.random.randint(lower, upper)
