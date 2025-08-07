from policyengine_us.model_api import *


class meets_tanf_non_cash_net_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets net income test for TANF non-cash benefit"
    documentation = "Income eligibility (net income as a percent of the poverty line) for TANF non-cash benefit for SNAP BBCE"
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        # Determine if the net income limit applies to the household.
        applies = parameters(
            period
        ).gov.hhs.tanf.non_cash.income_limit.net_applies
        state = spm_unit.household("state_code_str", period)
        # Varies depending on if the household has elderly and disabled people.
        hheod = spm_unit("is_tanf_non_cash_hheod", period)
        net_limit_applies = where(
            hheod, applies.hheod[state], applies.non_hheod[state]
        ).astype(bool)
        # All limits and incomes here expressed as % of FPG.
        net_income = spm_unit("snap_net_income_fpg_ratio", period)
        net_limit = parameters(period).gov.usda.snap.income.limit.net
        # Either the net limit doesn't apply or they pass it.
        return ~net_limit_applies | (net_income <= net_limit)
