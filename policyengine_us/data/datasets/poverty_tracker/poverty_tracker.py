from policyengine_core.data import Dataset
from typing import Type
import pandas as pd
from pathlib import Path
from policyengine_us.data.storage import STORAGE_FOLDER
import os


class PovertyTracker(Dataset):
    name = "poverty_tracker"
    label = "Poverty Tracker"
    data_format = Dataset.ARRAYS
    time_period = "2023"
    file_path = STORAGE_FOLDER / "poverty_tracker.h5"

    # Fetch the secret URL from the environment variable.
    # Replace with a valid URL if running locally.
    POVERTY_TRACKER_URL = os.environ.get("POVERTYTRACKER_RAW_URL")

    def generate(self):
        household_df = self.load_pt_data()
        situations = household_df.apply(get_hh_situtation, axis=1)

        if not self.POVERTY_TRACKER_URL:
            raise ValueError(
                "The POVERTY_TRACKER_URL environment variable is not set!"
            )

        person_ids = []
        person_group_ids = []
        group_ids = []

        data = {
            "age": [],
            "employment_income": [],
        }

        current_person_id = 0
        current_group_id = 0
        group_ids = household_df["public_id"].values
        for situation in situations:
            for person in situation["people"]:
                person_ids.append(current_person_id)
                person_group_ids.append(group_ids[current_group_id])

                age = situation["people"][person]["age"]
                employment_income = situation["people"][person][
                    "employment_income"
                ]

                # Clarify why age is sometimes directly in situation["people"][person]["age"] and sometimes in situation["people"][person]["age"][TAX_YEAR_STR]
                data["age"].append(
                    age.get(TAX_YEAR_STR) if isinstance(age, dict) else age
                )
                data["employment_income"].append(
                    employment_income.get(TAX_YEAR_STR)
                    if isinstance(employment_income, dict)
                    else employment_income
                )

                current_person_id += 1

            current_group_id += 1

        data["in_nyc"] = [True] * len(group_ids)
        data["state_name"] = ["NY"] * len(group_ids)

        group_id_names = [
            "tax_unit",
            "marital_unit",
            "spm_unit",
            "household",
            "family",
        ]

        for group_id_name in group_id_names:
            data[group_id_name + "_id"] = group_ids
            data["person_" + group_id_name + "_id"] = person_group_ids

        data["person_id"] = person_ids

        self.save_dataset(data)

    def load_pt_data(
        self,
        url: str = POVERTY_TRACKER_URL,
    ) -> pd.DataFrame:
        """
        Loads household-level raw PovertyTracker dataset.
        """
        # Download raw data from PovertyTracker website.
        pt = pd.read_csv(url)

        # Filter to only 2019 and 2020 (else q16surveyyear is NaN).
        pt = pt[pt["q16surveyyear"].notnull()].reset_index(drop=True)

        # Other adult and child household income.
        pt["other_household_income"] = pt[
            [
                "imp_q16incothhh_adult_tc",
                "imp_q16incothhh_child_tc",
                "imp_q16incothhh_tc",
            ]
        ].sum(axis=1)

        # Rename columns.
        COLUMNS_TO_RENAME = {
            "q16a3_age_tc": "age",
            "imp_q16earnhd_tc": "household_head_income",
            "imp_q16earnsp_tc": "spouse_income",
            "imp_q16moop_tc": "medical_out_of_pocket_expenses",
            "imp_q16chwoop_tc": "childcare_and_work_expenses",
            "imp_q16incsnap_tc": "snap_income",
            "imp_q16incret_tc": "retirement_income",
            "imp_q16incdis_tc": "disability_income",
            "imp_q16incui_tc": "unemployment_income",
            "q16a4": "respondent_lives_with_others",  # 1/2/97/98/99 Yes/No/NoAnswer/Don't know/Refused
            # "qopmres": "income",
        }
        for i in range(1, 10):
            COLUMNS_TO_RENAME[f"q16a4_rel{i}"] = f"relationship_to_relative{i}"
            COLUMNS_TO_RENAME[f"q16a4_age{i}_tc"] = f"age_of_relative{i}"

        pt.rename(columns=COLUMNS_TO_RENAME, inplace=True)

        # Replace 970 (unknown) with 40 (default age)
        pt["age"] = pt["age"].replace(970, 40)

        return pt.rename(columns=COLUMNS_TO_RENAME)


def extract_hh_data(observation: pd.Series) -> dict:
    """
    Takes in a row of the PovertyTracker dataframe and extracts
    information on relatives living with the household head.
    """
    relatives_dict = {}

    if observation["respondent_lives_with_others"] != 1:
        return relatives_dict

    var_number = 1
    relative_var = f"relationship_to_relative{var_number}"
    dependent_counter = 1
    while pd.notnull(relative_var) and var_number < 10:
        if observation[relative_var] == 1:  # Spouse
            partner_age = observation[f"age_of_relative{var_number}"]
            relatives_dict["your partner"] = {
                "age": partner_age if partner_age != 970 else 40,
                "employment_income": {
                    TAX_YEAR_STR: observation["spouse_income"]
                },
            }

        elif observation[relative_var] in [
            3,
            4,
            5,
            7,
        ]:  # child, stepchild, grandchild, or foster child
            relative_age = observation[f"age_of_relative{var_number}"]
            if relative_age < 18:  # assume only children are dependents
                relatives_dict[f"dependent{dependent_counter}"] = {
                    "age": relative_age if relative_age != 970 else 40
                }
            dependent_counter += 1

        var_number += 1

    return relatives_dict


TAX_YEAR = 2023
TAX_YEAR_STR = str(TAX_YEAR)


def get_hh_situtation(row: pd.Series):
    situation_dict = {
        "people": {
            "you": {
                "age": {TAX_YEAR_STR: row["age"]},
                "employment_income": {
                    TAX_YEAR_STR: row["household_head_income"]
                },
                "medical_out_of_pocket_expenses": {
                    TAX_YEAR_STR: row["medical_out_of_pocket_expenses"]
                },
            }
        },
        "families": {"your family": {"members": ["you"]}},
        "marital_units": {},
        "tax_units": {"your tax unit": {"members": ["you"]}},
        "spm_units": {
            "your household": {
                "members": [
                    "you",
                ],
                "childcare_expenses": {
                    TAX_YEAR_STR: row["childcare_and_work_expenses"]
                },
                "snap": {TAX_YEAR_STR: row["snap_income"]},
            }
        },
        "households": {
            "your household": {
                "members": ["you"],
                "state_name": {TAX_YEAR_STR: "NY"},
                "in_nyc": True,
            }
        },
    }

    hh_data = extract_hh_data(row)
    situation_dict["people"].update(hh_data)

    # Add spouse and dependents to families, marital_units, tax_units, spm_units
    family_members = ["you"]
    marital_unit_members = ["you"]
    for member, member_data in hh_data.items():
        family_members.append(member)
        marital_unit_members.append(member)
        situation_dict["people"][member].update(
            {"employment_income": {TAX_YEAR_STR: 0}}
        )
        situation_dict["tax_units"]["your tax unit"]["members"].append(member)
        situation_dict["spm_units"]["your household"]["members"].append(member)
        situation_dict["households"]["your household"]["members"].append(
            member
        )

        # marital_unit_id = "{}'s marital unit".format(member)
        # situation_dict["marital_units"][marital_unit_id] = {
        #     "members": [member]
        # }

        # if member.startswith("dependent"):
        #     situation_dict["marital_units"][marital_unit_id]["marital_unit_id"] = {
        #         TAX_YEAR_STR: dependent_counter
        #     }
        #     dependent_counter += 1

    situation_dict["families"]["your family"]["members"] = family_members
    situation_dict["marital_units"]["your marital unit"] = {
        "members": marital_unit_members
    }

    return situation_dict
