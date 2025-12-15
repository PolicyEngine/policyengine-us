from policyengine_us.model_api import *


class il_pi_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets income requirements for Illinois PI"
    definition_period = YEAR
    reference = "https://cecids.org/methodology/"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Income must be at or below 400% FPL.
        p = parameters(period).gov.states.il.isbe.pi.eligibility.income
        fpg = person.spm_unit("spm_unit_fpg", period)
        income = person.spm_unit("il_pi_countable_income", period)
        threshold = fpg * p.max_fpg_rate
        return income <= threshold
