from policyengine_us.model_api import *


class il_pi_is_low_income(Variable):
    value_type = bool
    entity = Person
    label = "Low income for Illinois PI"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/prevention-initiative-manual.pdf"
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Low income: income at or below 200% FPL.
        p = parameters(period).gov.states.il.isbe.pi.eligibility.income
        fpg = person.spm_unit("spm_unit_fpg", period)
        income = person.spm_unit("il_pi_countable_income", period)
        threshold = fpg * p.low_income_rate
        return income <= threshold
