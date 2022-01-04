from openfisca_us.model_api import *


class meets_tanf_non_cash_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets income test for TANF non-cash benefit"
    documentation = "Income eligibility (gross income as a percent of the poverty line) for TANF non-cash benefit for SNAP BBCE"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        state = spm_unit.household("state_code_str", period)
        limits = parameters(period).hhs.tanf.non_cash
        income_limit_fpg = limits.gross_income_limit_fpg[state]
        income_fpg = spm_unit("snap_gross_income_fpg_ratio", period)
        return income_fpg <= income_limit_fpg
