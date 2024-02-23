from policyengine_core.data import Dataset
from policyengine_us.data.datasets.cps.cps import CPS_2023
from policyengine_us.data.storage import STORAGE_FOLDER
import numpy as np
import pandas as pd


class PUFExtendedCPS_2023(Dataset):
    name = "puf_extended_cps_2023"
    label = "PUF-extended CPS (2023)"
    file_path = STORAGE_FOLDER / "puf_extended_cps_2023.h5"
    data_format = Dataset.ARRAYS
    time_period = "2023"

    def generate(self):
        from .process_puf import (
            FINANCIAL_SUBSET as FINANCIAL_VARIABLES,
            puf_imputed_cps_person_level,
        )

        person_df = puf_imputed_cps_person_level()
        new_data = {}
        cps = CPS_2023()
        cps_data = cps.load()
        for variable in list(set(cps.variables) | set(FINANCIAL_VARIABLES)):
            if "_id" in variable:
                # Append on a copy multiplied by 10
                new_data[variable] = np.concatenate(
                    [cps_data[variable][...], cps_data[variable][...] + 1e8]
                )
            elif "_weight" in variable:
                # Append on a zero-weighted copy
                new_data[variable] = np.concatenate(
                    [
                        cps_data[variable][...],
                        np.zeros_like(cps_data[variable][...]),
                    ]
                )
            else:
                # Append on a copy
                if variable in FINANCIAL_VARIABLES:
                    if variable not in cps.variables:
                        if variable == "social_security":
                            ## SS is an edge case
                            original_values = (
                                cps_data["social_security_retirement"][...]
                                + cps_data["social_security_disability"][...]
                            )
                        else:
                            original_values = np.zeros_like(
                                cps_data["employment_income"][...]
                            )
                    else:
                        original_values = cps_data[variable][...]
                    new_data[variable] = np.concatenate(
                        [original_values, person_df[variable].values]
                    )
                else:
                    new_data[variable] = np.concatenate(
                        [cps_data[variable][...], cps_data[variable][...]]
                    )

        # Flag if record is from imputed from PUF or straight from CPS.
        new_data["is_imputed_from_puf"] = np.concatenate(
            [
                np.zeros_like(cps_data["age"][...]),
                np.ones_like(cps_data["age"][...]),
            ]
        ).astype(bool)

        self.save_dataset(new_data)
