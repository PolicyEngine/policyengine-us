from policyengine_us.model_api import *


class il_pfae_is_low_income(Variable):
    value_type = bool
    entity = Person
    label = "Family income at or below 100% FPL (secondary priority factor)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/pages/preschool-for-all.aspx",
        "https://www.isbe.net/Documents/pdg-eg-grant-enrollment-form.pdf#page=2",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.isbe.pfae.eligibility.income
        fpg = person.spm_unit("spm_unit_fpg", period)
        income = person.spm_unit("il_isbe_countable_income", period)
        threshold = fpg * p.low_income_rate
        return income <= threshold
