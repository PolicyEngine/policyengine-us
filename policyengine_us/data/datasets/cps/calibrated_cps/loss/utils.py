from typing import List, Tuple
import torch
from policyengine_core.data import Dataset
from survey_enhance.reweight import LossCategory
from policyengine_core.parameters import ParameterNode, uprate_parameters, get_parameter
from pathlib import Path
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


class NationalMetric(LossCategory):
    policyengine_variable: str
    """The name of the variable in PolicyEngine-US that this metric is associated with (e.g. employment_income)."""

    policyengine_entity: str
    """The name of the entity in PolicyEngine-US that this variable is associated with (e.g. person)."""

    should_sum_by_household: bool = False
    """Whether this metric should be summed by household."""

    parameter_name: str
    """The name of the parameter in the calibration parameters folder that this metric is associated with."""

    is_nonzero_count: bool = False
    """Whether this metric is a count of people, rather than the sum."""

    def get_comparisons(self, dataset: Dataset) -> List[Tuple[str, float, torch.Tensor]]:
        parameter = get_parameter(self.full_calibration_parameters, self.parameter_name)(self.instant)
        values = getattr(getattr(dataset, self.policyengine_entity), self.policyengine_variable)
        if self.should_sum_by_household:
            values = sum_by_household(values, dataset)
        name = self.policyengine_variable
        if self.is_nonzero_count:
            values = values > 0
            name += "_count"
        return [(name, values, parameter)]
        