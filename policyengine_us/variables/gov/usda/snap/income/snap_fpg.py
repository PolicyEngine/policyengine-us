from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg
from policyengine_us.variables.gov.usda.snap.income.snap_income_standard_helpers import (
    _snap_fpg_context,
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
        # PDF pages 1-2.
        "https://fns-prod.azureedge.us/sites/default/files/resource-files/FY17-Income-Eligibility-Standards.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        n = spm_unit("snap_unit_size", period)
        p1, pn = snap_monthly_fpg_amounts(spm_unit, period, parameters)
        linear_monthly_fpg = p1 + pn * (n - 1)
        state_group, guideline_date = _snap_fpg_context(spm_unit, period)
        table = parameters(guideline_date).gov.hhs.fpg_table
        if not table.in_effect:
            return linear_monthly_fpg

        use_table = (
            np.isin(state_group, list(table.amount))
            & np.isfinite(n)
            & (n >= table.min_household_size)
            & (n == np.floor(n))
        )
        # Keep the original monthly arithmetic outside HHS's source domain.
        return where(
            use_table,
            fpg(n, state_group, guideline_date, parameters) / MONTHS_IN_YEAR,
            linear_monthly_fpg,
        )
