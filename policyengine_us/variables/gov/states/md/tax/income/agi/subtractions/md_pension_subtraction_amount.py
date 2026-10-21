from policyengine_us.model_api import *


class md_pension_subtraction_amount(Variable):
    value_type = float
    entity = Person
    label = "MD pension subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://interactive.marylandtaxes.gov/Individuals/iFile_ChooseForm/PriorYearForms/Resident_Booklet_2021.pdf#page=13"
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
        # Under Md. Code Tax-General § 10-209(d)(1) and Form 502 instructions
        # (Worksheet 13A, line 1), military retirement income exceeding the
        # § 10-207(q) military retirement subtraction qualifies for the
        # general pension exclusion.
        military_income = person("military_retirement_income", period)
        military_subtraction = person(
            "md_military_retirement_subtraction_amount", period
        )
        excess_military = max_(0, military_income - military_subtraction)

        # calculate pension subtraction amount for each person
        peninc = add(person, period, p.pension.sources) + excess_military
        socsec = person("social_security", period)
        amount = min_(peninc, max_(0, p.pension.max_amount - socsec))
        # return pension subtraction amount for each eligible person
        return eligible * amount
