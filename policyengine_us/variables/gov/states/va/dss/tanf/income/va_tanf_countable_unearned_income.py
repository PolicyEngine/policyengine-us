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
        p = parameters(period).gov.states.va.dss.tanf.income.deduction.unearned
        person = spm_unit.members
        gross_unearned = spm_unit.sum(
            person("tanf_gross_unearned_income", period)
        )
        # Apply child support disregard
        child_support = add(spm_unit, period, ["child_support_received"])
        child_support_disregard = min_(child_support, p.monthly_child_support)
        countable_unearned = gross_unearned - child_support_disregard
        # For TANF-UP, also disregard unemployment compensation
        up_tanf_eligibility = spm_unit("va_up_tanf_eligibility", period)
        unemployment_compensation = add(
            spm_unit, period, ["unemployment_compensation"]
        )
        return where(
            up_tanf_eligibility,
            countable_unearned - unemployment_compensation,
            countable_unearned,
        )
