from policyengine_us.model_api import *


class md_pension_subtraction_amount(Variable):
    value_type = float
    entity = Person
    label = "MD pension subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://interactive.marylandtaxes.gov/Individuals/iFile_ChooseForm/PriorYearForms/Resident_Booklet_2021.pdf#page=13",
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-209",
        # Pension Exclusion Computation Worksheet (13A), line 3.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=14",
    )
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
        # Worksheet 13A, line 3, and Tax-General 10-209(b)(2): "any payment
        # received as old age, survivors, or disability benefits under the
        # Social Security Act, the Railroad Retirement Act, or both", whether
        # or not federal AGI includes them, so both railroad tiers count.
        federal_benefits = add(
            person,
            period,
            [
                "social_security",
                "railroad_social_security_equivalent_benefits",
                "taxable_railroad_pension_benefits",
                "tax_exempt_railroad_pension_benefits",
            ],
        )
        amount = min_(peninc, max_(0, p.pension.max_amount - federal_benefits))
        # return pension subtraction amount for each eligible person
        return eligible * amount
