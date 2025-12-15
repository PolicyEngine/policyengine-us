from policyengine_us.model_api import *


class il_pfa_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Child meets income requirements for Illinois PFA"
    definition_period = YEAR
    reference = "https://www.isbe.net/pages/preschool-for-all.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Income must be at or below 400% FPL for secondary priority enrollment.
        p = parameters(period).gov.states.il.isbe.pfa.eligibility.income
        fpg = person.spm_unit("spm_unit_fpg", period)
        income = person.spm_unit("il_pfa_countable_income", period)
        threshold = fpg * p.secondary_priority_rate
        return income <= threshold
