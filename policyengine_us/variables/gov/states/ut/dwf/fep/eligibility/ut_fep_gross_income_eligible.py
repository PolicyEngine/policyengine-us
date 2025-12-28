from policyengine_us.model_api import *


class ut_fep_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Utah TANF under gross income test"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-200-239"
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        # Utah gross income test: gross income <= 185% of SNB (Standard Needs Budget)
        # Per R986-200-239(1), gross income must be <= 185% of SNB
        # The net income limit equals the SNB
        p = parameters(period).gov.states.ut.dwf.fep

        size = spm_unit("spm_unit_size", period)
        size_capped = min_(size, p.payment_standard.max_unit_size)

        # Standard Needs Budget (SNB) = net income limit
        snb = p.standard_needs_budget.amount[size_capped]
        gross_income_limit = snb * p.income.gross_income_limit.rate

        gross_income = spm_unit("ut_fep_gross_income", period)
        return gross_income <= gross_income_limit
