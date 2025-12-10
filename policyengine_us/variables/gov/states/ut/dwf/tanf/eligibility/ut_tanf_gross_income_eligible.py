from policyengine_us.model_api import *


class ut_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Utah TANF under gross income test"
    definition_period = MONTH
    reference = (
        "https://adminrules.utah.gov/public/rule/R986-200/Current%20Rules"
    )
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        # Utah gross income test: gross income <= 185% of SNB
        p = parameters(period).gov.states.ut.dwf.tanf

        size = spm_unit("spm_unit_size", period)
        size_capped = min_(size, p.payment_standard.max_unit_size)

        gross_income = spm_unit("ut_tanf_gross_income", period)
        gross_limit = p.income.gross_income_limit.amount[size_capped]
        return gross_income <= gross_limit
