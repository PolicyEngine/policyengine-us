from policyengine_us.model_api import *


class il_pi_is_deep_poverty(Variable):
    value_type = bool
    entity = Person
    label = "In deep poverty or receiving TANF for Illinois PI (Factor 4)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=2",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        # Factor 4 (50 pts): Family income at or below 50% FPL and/or receiving TANF.
        p = parameters(period).gov.states.il.isbe.pi.eligibility.income
        fpg = spm_unit("spm_unit_fpg", period)
        income = spm_unit("il_isbe_countable_income", period)
        threshold = fpg * p.deep_poverty_rate
        is_below_50_fpl = income <= threshold
        receives_tanf = spm_unit("il_tanf", period) > 0
        return is_below_50_fpl | receives_tanf
