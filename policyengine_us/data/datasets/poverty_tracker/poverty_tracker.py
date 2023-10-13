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

        columns_to_rename = {
            # "imp_qearnhd_tc": "hh_head_earnings", # not currently used
            # "imp_qearnsp_tc": "spouse_earnings", # not currently used
            "imp_qage_tc": "age",
            "qopmres": "income",
        }

        return pt.rename(columns=columns_to_rename)


def extract_hh_data(observation: pd.Series) -> dict:
    """
    Takes in a row of the PovertyTracker dataframe and extracts
    information on relatives living with the household head.
    """
    relatives_dict = {}

    # If someone(s) else lives with respondent, q16a4 = 1.
    if observation["q16a4"] != 1:
        return relatives_dict

    var_number = 1
    relative_var = "q16a4_rel" + str(var_number)
    dependent_counter = 1
    while pd.notnull(relative_var) and var_number < 10:
        if observation[relative_var] == 1:  # Spouse
            partner_age = observation[f"q16a4_age{var_number}_tc"]
            relatives_dict["your partner"] = {
                "age": partner_age if partner_age != 970 else 40
            }

        elif observation[relative_var] in [
            3,
            4,
            5,
            7,
        ]:  # child, stepchild, grandchild, or foster child
            relative_age = observation[f"q16a4_age{var_number}_tc"]
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
                "employment_income": {TAX_YEAR_STR: row["income"]},
            }
        },
        "families": {"your family": {"members": ["you"]}},
        "marital_units": {},
        "tax_units": {"your tax unit": {"members": ["you"]}},
        "spm_units": {
            "your household": {
                "members": [
                    "you",
                    # "your partner",
                    # "your first dependent"
                ]
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
