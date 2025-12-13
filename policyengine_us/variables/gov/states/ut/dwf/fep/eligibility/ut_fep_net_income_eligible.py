from policyengine_us.model_api import *


class ut_fep_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Utah TANF under net income test"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-200-239"
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        # Utah net income test: countable income < 100% of SNB (strict less than)
        p = parameters(period).gov.states.ut.dwf.fep

        size = spm_unit("spm_unit_size", period)
        size_capped = min_(size, p.payment_standard.max_unit_size)

        countable_income = spm_unit("ut_fep_countable_income", period)
        return countable_income < p.standard_needs_budget.amount[size_capped]
