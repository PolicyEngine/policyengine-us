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
        comparisons += [
            (
                f"people",
                sum_by_household(np.ones_like(age), dataset),
                330_000_000,
            )
        ]

        return comparisons
