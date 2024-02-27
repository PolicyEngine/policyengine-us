from policyengine_core.data import Dataset
import numpy as np
from policyengine_us.data.storage import STORAGE_FOLDER
from tqdm import tqdm


class PUF_2023(Dataset):
    name = "puf_2023"
    label = "PUF"
    time_period = "2023"
    data_format = Dataset.ARRAYS
    file_path = STORAGE_FOLDER / "puf_2023.h5"

    def generate(self):
        # First pass: single person tax units.
        from policyengine_us.data.datasets.cps.enhanced_cps.process_puf import (
            load_puf,
            impute_missing_demographics,
        )

        puf, demographics = load_puf()
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
