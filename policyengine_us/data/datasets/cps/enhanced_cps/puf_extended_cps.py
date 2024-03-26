from policyengine_core.data import Dataset
from policyengine_us.data.datasets.cps.cps import CPS_2022
from policyengine_us.data.storage import STORAGE_FOLDER
import numpy as np


class PUFExtendedCPS(Dataset):
    data_format = Dataset.ARRAYS
    cps = None

    def generate(self):
        from .process_puf import (
            FINANCIAL_SUBSET as FINANCIAL_VARIABLES,
            puf_imputed_cps_person_level,
        )
        from policyengine_us.system import system
        from policyengine_us import Microsimulation

        person_df, tax_unit_df = puf_imputed_cps_person_level(
            time_period=self.time_period
        )
        new_data = {}
        cps = self.cps()
        input_data_sim = Microsimulation(dataset=self.cps)
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
                        entity = system.variables[variable].entity.key
                        original_values = np.zeros_like(
                            cps_data[f"{entity}_id"][...]
                        )
                    else:
                        original_values = input_data_sim.calculate(
                            variable, self.time_period
                        ).values
                    imputed_data = (
                        person_df[variable].values
                        if variable in person_df
                        else tax_unit_df[variable].values
                    )
                    new_data[variable] = np.concatenate(
                        [original_values, imputed_data]
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


class PUFExtendedCPS_2022(PUFExtendedCPS):
    time_period = 2022
    name = "puf_extended_cps_2022"
    label = "PUF-extended CPS (2022)"
    cps = CPS_2022
    file_path = STORAGE_FOLDER / "puf_extended_cps_2022.h5"
