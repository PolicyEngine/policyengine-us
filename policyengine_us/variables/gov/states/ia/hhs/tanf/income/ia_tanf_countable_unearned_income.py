from policyengine_us.model_api import *


class ia_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.tanf.income
        unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        # Per IAC 441-41.27: $50 child support disregard per eligible group
        return max_(unearned - p.child_support_disregard.amount, 0)
