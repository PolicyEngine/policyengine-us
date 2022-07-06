from openfisca_us.model_api import *


class meets_tanf_non_cash_gross_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets gross income test for TANF non-cash benefit"
    documentation = "Income eligibility (gross income as a percent of the poverty line) for TANF non-cash benefit for SNAP BBCE"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        state = spm_unit.household("state_code_str", period)
        # All limits and incomes here expressed as % of FPG.
        limits = parameters(period).gov.hhs.tanf.non_cash.income_limit
        gross_limit = limits.gross[state]
        gross_income = spm_unit("snap_gross_income_fpg_ratio", period)
        return gross_income <= gross_limit
