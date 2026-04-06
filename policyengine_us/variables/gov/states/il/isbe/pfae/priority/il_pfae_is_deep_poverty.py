from policyengine_us.model_api import *


class il_pfae_is_deep_poverty(Variable):
    value_type = bool
    entity = Person
    label = "Family income at or below 50% FPL (50-point factor for IL PFAE)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/pdg-eg-grant-enrollment-form.pdf#page=2",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Deep poverty (income <= 50% FPL) is a highest priority factor.
        # Per the ISBE PDG enrollment form, Factor 4 includes "Family income at
        # or below 50% of the federal poverty guidelines."
        p = parameters(period).gov.states.il.isbe.pfae.eligibility.income
        spm_unit = person.spm_unit
        fpg = spm_unit("spm_unit_fpg", period)
        income = spm_unit("il_isbe_countable_income", period)
        threshold = fpg * p.deep_poverty_rate
        return income <= threshold
