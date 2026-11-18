from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class wy_lieap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Federal poverty guideline for the Wyoming LIEAP household"
    defined_for = StateCode.WY
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        # Rule 8(a)(ii)(S).
        "https://www.law.cornell.edu/regulations/wyoming/agency-049/subagency-0024/chapter-1/049-1-Wyo-Code-R-SSSS-1-8",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wy.dfs.lieap.income
        size = spm_unit("wy_lieap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        return where(size > 0, guideline, 0)
