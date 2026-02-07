from policyengine_us.model_api import *


class il_pi_is_low_income(Variable):
    value_type = bool
    entity = Person
    label = "Low income for Illinois PI (Factor 6, 25 points)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=2",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        # Factor 6 (25 pts): Family income at or below 100% FPL.
        p = parameters(period).gov.states.il.isbe.pi.eligibility.income
        fpg = spm_unit("spm_unit_fpg", period)
        income = spm_unit("il_isbe_countable_income", period)
        threshold = fpg * p.low_income_rate
        return income <= threshold
