from policyengine_us.model_api import *


class meets_tanf_non_cash_gross_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets gross income test for TANF non-cash benefit"
    documentation = "Income eligibility (gross income compared to the state's published standard) for TANF non-cash benefit for SNAP BBCE"
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        # Use the gross-test income concept so states electing full
        # counting of certain ineligible aliens' income under the gross
        # income test (7 CFR 273.11(c)(3)(i)) apply it to this categorical
        # eligibility screen as well.
        gross_income = spm_unit("snap_gross_test_income", period)
        limit = spm_unit("tanf_non_cash_gross_income_limit", period)
        return gross_income <= limit
