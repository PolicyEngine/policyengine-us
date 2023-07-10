from typing import List, Tuple
import torch
from policyengine_core.data import Dataset
from survey_enhance.reweight import LossCategory
from policyengine_core.parameters import (
    ParameterNode,
    uprate_parameters,
    get_parameter,
)
from pathlib import Path
from survey_enhance.reweight import LossCategory
from policyengine_core.data import Dataset
import torch
from typing import List, Tuple
from policyengine_us.system import system


class NationalMetric(LossCategory):
    policyengine_variable: str
    """The name of the variable in PolicyEngine-US that this metric is associated with (e.g. employment_income)."""

    parameter_name: str
    """The name of the parameter in the calibration parameters folder that this metric is associated with."""

    is_nonzero_count: bool = False
    """Whether this metric is a count of people, rather than the sum."""

    def get_comparisons(
        self, dataset: Dataset
    ) -> List[Tuple[str, float, torch.Tensor]]:
        parameter = get_parameter(
            self.calibration_parameters, self.parameter_name
        )(self.instant)
        values = getattr(dataset.household, self.policyengine_variable)
        name = self.__class__.__name__
        if self.is_nonzero_count:
            values = values > 0
        return [(name, values, parameter)]
