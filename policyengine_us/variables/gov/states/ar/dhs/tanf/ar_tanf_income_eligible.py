from policyengine_us.model_api import *


class ar_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arkansas TANF income eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = StateCode.AR

    def formula(spm_unit, period, parameters):
        # Per 208.00.13 Ark. Code R. Section 001, Section 3.3
        p = parameters(period).gov.states.ar.dhs.tanf.income

        # Step 1: Gross income test - must be below 185% FPL
        fpg = spm_unit("spm_unit_fpg", period)
        gross_income_limit = fpg * p.gross_income_limit.rate

        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        gross_income = gross_earned + gross_unearned

        passes_gross_test = gross_income < gross_income_limit

        # Step 2: Net income test - countable income must be at or below $223
        countable_income = spm_unit("ar_tanf_countable_income", period)
        passes_net_test = countable_income <= p.eligibility_standard.amount

        return passes_gross_test & passes_net_test
