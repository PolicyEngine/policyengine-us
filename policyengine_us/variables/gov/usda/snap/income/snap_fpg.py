from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.snap.income.snap_income_standard_helpers import (
    snap_monthly_fpg_amounts,
)


class snap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP federal poverty guideline"
    unit = USD
    documentation = "The federal poverty guideline used to determine SNAP eligibility."
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        n = spm_unit("snap_unit_size", period)
        p1, pn = snap_monthly_fpg_amounts(spm_unit, period, parameters)
        return p1 + pn * (n - 1)
