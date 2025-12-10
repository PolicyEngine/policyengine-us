from policyengine_us.model_api import *


class ut_tanf_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Utah TANF under net income test"
    definition_period = MONTH
    reference = (
        "https://adminrules.utah.gov/public/rule/R986-200/Current%20Rules"
    )
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        # Utah net income test: countable income < 100% of SNB (strict less than)
        p = parameters(period).gov.states.ut.dwf.tanf

        size = spm_unit("spm_unit_size", period)
        size_capped = min_(size, p.payment_standard.max_unit_size)

        countable_income = spm_unit("ut_tanf_countable_income", period)
        net_limit = p.income.net_income_limit.amount[size_capped]
        return countable_income < net_limit
