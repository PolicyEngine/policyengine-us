from policyengine_us.model_api import *


class il_pfa_is_low_income(Variable):
    value_type = bool
    entity = Person
    label = "Child is low income for Illinois PFA"
    definition_period = YEAR
    reference = "https://www.isbe.net/pages/preschool-for-all.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Low income: income at or below 200% FPL.
        p = parameters(period).gov.states.il.isbe.pfa.eligibility.income
        fpg = person.spm_unit("spm_unit_fpg", period)
        income = person.spm_unit("il_pfa_countable_income", period)
        threshold = fpg * p.low_income_rate
        return income <= threshold
