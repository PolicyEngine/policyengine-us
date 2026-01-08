from policyengine_us.model_api import *


class va_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=58"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.tanf.income.deductions
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        # Apply child support disregard
        child_support = add(spm_unit, period, ["child_support_received"])
        child_support_disregard = min_(child_support, p.child_support)
        return max_(gross_unearned - child_support_disregard, 0)
