from policyengine_us.model_api import *


class md_pension_subtraction_amount(Variable):
    value_type = float
    entity = Person
    label = "MD pension subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=13"
    defined_for = StateCode.MD

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.tax.income.agi.subtractions
        # determine pension subtraction eligiblity for each person
        dependent = person("is_tax_unit_dependent", period)
        min_age = p.pension.min_age
        elderly = person("age", period) >= min_age
        disabled = person("is_disabled", period)
        partner_is_disabled = person("has_disabled_spouse", period)
        eligible = ~dependent & (elderly | disabled | partner_is_disabled)
        # calculate pension subtraction amount for each person
        peninc = person("taxable_pension_income", period)
        socsec = person("social_security", period)
        amount = min_(peninc, max_(0, p.pension.max_amount - socsec))
        # return pension subtraction amount for each eligible person
        return eligible * amount
