from policyengine_us.model_api import *


class foreign_earned_income_exclusion_gross_person_reported(Variable):
    value_type = float
    entity = Person
    label = "Reported own gross foreign earned income and housing exclusions"
    unit = USD
    definition_period = YEAR
    default_value = -1
    documentation = (
        "Line 43 of the Form 2555 the person files, the line 36 housing "
        "exclusion plus the line 42 foreign earned income exclusion, as "
        "supplied. Each spouse who claims the exclusion files a separate Form "
        "2555, so on a joint return enter each spouse's own line 43. An "
        "amount of zero or more is used as entered. A negative amount, such as "
        "the default -1, means not supplied: "
        "foreign_earned_income_exclusion_gross_person then uses the "
        "return's line 43 for the head of a return with one head or spouse, "
        "and zero otherwise, whatever other people report. As with every "
        "input, Core carries an amount into a later year only when no one "
        "has an amount for that year: once anyone enters an amount for a "
        "year, a person whose amount was entered only for an earlier year "
        "gets the default in that year. Enter each person's amount for every "
        "year calculated."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/911#a",
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
        # Married couples: each spouse figures the exclusion on a separate
        # Form 2555, and the joint return excludes the sum.
        "https://www.irs.gov/pub/irs-prior/i2555--2025.pdf#page=6",
    )
