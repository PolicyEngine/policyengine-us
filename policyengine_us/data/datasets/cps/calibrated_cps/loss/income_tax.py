from typing import List, Tuple
import torch
import pandas as pd
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
import numpy as np

class IncomeTaxAGIBreakdown(LossCategory):
    policyengine_variable: str
    """The name of the variable in PolicyEngine-US that this metric is associated with (e.g. employment_income)."""

    parameter_name: str
    """The name of the parameter in the calibration parameters folder that this metric is associated with."""

    is_nonzero_count: bool = False
    """Whether this metric is a count of people, rather than the sum."""

    label: str
    """The label for this metric."""

    def get_comparisons(
        self, dataset: Dataset
    ) -> List[Tuple[str, float, torch.Tensor]]:
        parameter = get_parameter(
            self.calibration_parameters, self.parameter_name
        )(self.instant)
        values = getattr(dataset.tax_unit, self.policyengine_variable)
        agi = dataset.tax_unit.adjusted_gross_income
        tax_unit_household_id = dataset.tax_unit.household_id
        household_id = dataset.household.household_id
        # Iterate over brackets. Each bracket has a lower threshold and an amount.
        thresholds = parameter.thresholds
        amounts = parameter.amounts
        comparisons = []
        for i in range(len(thresholds)):
            lower_threshold = thresholds[i]
            upper_threshold = thresholds[i + 1] if i < len(thresholds) - 1 else np.inf
            within_bracket = (agi >= lower_threshold) * (agi < upper_threshold)
            if self.is_nonzero_count:
                tax_unit_is_nonzero = pd.Series((values > 0) * within_bracket) # Array, not series
                household_nonzero_count = tax_unit_is_nonzero.groupby(tax_unit_household_id).sum()
                household_values = household_nonzero_count[household_id].values
            else:
                tax_unit_values = pd.Series(values * within_bracket)
                household_values = tax_unit_values.groupby(tax_unit_household_id).sum()
                household_values = household_values[household_id].values
            comparisons.append(
                (
                    f"{self.label} {'aggregate' if not self.is_nonzero_count else 'count'} (${lower_threshold} <= AGI < ${upper_threshold})",
                    household_values,
                    amounts[i],
                )
            )
        
        return comparisons

class AGIByAGI(IncomeTaxAGIBreakdown):
    label = "AGI"
    is_nonzero_count = False
    policyengine_variable = "adjusted_gross_income"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.by_agi.aggregate.adjusted_gross_income"

class AGICountByAGI(IncomeTaxAGIBreakdown):
    label = "AGI"
    is_nonzero_count = True
    policyengine_variable = "adjusted_gross_income"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.by_agi.nonzero_count.adjusted_gross_income"

class IncomeTaxByAGI(IncomeTaxAGIBreakdown):
    label = "Income tax"
    is_nonzero_count = False
    policyengine_variable = "income_tax"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.by_agi.aggregate.income_tax"

class IncomeTaxCountByAGI(IncomeTaxAGIBreakdown):
    label = "Income tax"
    is_nonzero_count = True
    policyengine_variable = "income_tax"
    parameter_name = "us.programs.federal_income_tax.sources_of_income.by_agi.nonzero_count.income_tax"
