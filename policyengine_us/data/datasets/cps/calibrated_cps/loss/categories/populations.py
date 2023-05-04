from survey_enhance.reweight import LossCategory
from policyengine_core.data import Dataset
import torch
from typing import List, Tuple
import numpy as np
import pandas as pd


def sum_by_household(values: pd.Series, dataset: Dataset) -> np.ndarray:
    return (
        pd.Series(values)
        .groupby(dataset.person.person_household_id.values)
        .sum()
        .values
    )


class Populations(LossCategory):
    weight = 1
    static_dataset = False

    def get_comparisons(
        self, dataset: Dataset
    ) -> List[Tuple[str, float, torch.Tensor]]:
        comparisons = []
        age = dataset.person.age
        parameters = self.calibration_parameters.populations
        comparisons += [
            (
                f"population_US",
                sum_by_household(np.ones_like(age), dataset),
                parameters.total,
            )
        ]
        household_state_codes = dataset.household.state_code
        for state in parameters.by_state._children:
            comparisons += [
                (
                    f"population_{state}",
                    sum_by_household(np.ones_like(age), dataset)
                    * (household_state_codes == state),
                    parameters.by_state._children[state],
                )
            ]

        return comparisons
