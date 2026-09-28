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
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.9#a_3",
        "https://www.law.cornell.edu/uscode/text/7/2014#c",
    )

    def formula(spm_unit, period, parameters):
        n = spm_unit("snap_unit_size", period)
        p1, pn = snap_monthly_fpg_amounts(spm_unit, period, parameters)
        return p1 + pn * (n - 1)
