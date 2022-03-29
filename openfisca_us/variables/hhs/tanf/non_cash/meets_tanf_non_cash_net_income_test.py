from openfisca_us.model_api import *


class meets_tanf_non_cash_net_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets net income test for TANF non-cash benefit"
    documentation = "Income eligibility (net income as a percent of the poverty line) for TANF non-cash benefit for SNAP BBCE"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        state = spm_unit.household("state_code_str", period)
        # All limits and incomes here expressed as % of FPG.
        limits = parameters(period).hhs.tanf.non_cash.income_limit
        hheod = spm_unit("is_tanf_non_cash_hheod", period)
        hheod_net_limit_applies = limits.net_applies.hheod[state].astype(bool)
        non_hheod_net_limit_applies = limits.net_applies.non_hheod[
            state
        ].astype(bool)
        net_limit_applies = where(
            hheod, hheod_net_limit_applies, non_hheod_net_limit_applies
        )
        net_income = spm_unit("snap_net_income_fpg_ratio", period)
        net_limit = parameters(period).usda.snap.income.limit.net
        # Either the net limit doesn't apply or they pass it.
        return ~net_limit_applies | (net_income <= net_limit)
