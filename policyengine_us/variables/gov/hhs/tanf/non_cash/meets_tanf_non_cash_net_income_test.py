from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.snap.income.snap_income_standard_helpers import (
    snap_monthly_income_standard,
)


class meets_tanf_non_cash_net_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets net income test for TANF non-cash benefit"
    documentation = "Income eligibility (net income as a percent of the poverty line) for TANF non-cash benefit for SNAP BBCE"
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        # Determine if the net income limit applies to the household.
        applies = parameters(period).gov.hhs.tanf.non_cash.income_limit.net_applies
        state = spm_unit.household("state_code_str", period)
        # Varies depending on if the household has elderly and disabled people.
        hheod = spm_unit("is_tanf_non_cash_hheod", period)
        net_limit_applies = where(
            hheod, applies.hheod[state], applies.non_hheod[state]
        ).astype(bool)
        net_income = spm_unit("snap_net_income", period)
        net_limit = parameters(period).gov.usda.snap.income.limit.net
        # Mirror meets_snap_net_income_test: the monthly standard is the
        # poverty guideline times the net limit, rounded up to the next
        # whole dollar per 7 CFR 273.9(a)(3)(ii), compared against the
        # whole-dollar rounded net income. A raw ratio comparison would deny
        # households sitting exactly at the published standard.
        limit = snap_monthly_income_standard(spm_unit, period, parameters, net_limit)
        # Either the net limit doesn't apply or they pass it.
        return ~net_limit_applies | (net_income <= limit)
