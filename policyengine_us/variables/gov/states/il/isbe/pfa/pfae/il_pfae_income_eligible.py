from policyengine_us.model_api import *


class il_pfae_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Child meets income requirements for Illinois PFAE"
    definition_period = YEAR
    reference = "https://www.isbe.net/pages/preschool-for-all.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # PFAE requires income at or below 200% FPL (stricter than PFA's 400%).
        p = parameters(period).gov.states.il.isbe.pfa.pfae.income
        fpg = person.spm_unit("spm_unit_fpg", period)
        income = person.spm_unit("il_pfa_countable_income", period)
        threshold = fpg * p.max_fpg_rate
        return income <= threshold
