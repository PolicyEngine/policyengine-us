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
        "and zero otherwise, whatever other people report. An entry for a "
        "calendar year applies only to that year, and one keyed by a period "
        "of several years or by a year that starts after January, such as "
        "year:2024:3 or year:2025-07, applies to no year. Because of its "
        "formula, Core does not count this as an input variable, so "
        "Simulation.to_input_dict() and to_input_dataframe() leave a supplied "
        "amount out unless include_computed_variables=True; supply it in the "
        "situation or with set_input."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/911#a",
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
        # Married couples: each spouse figures the exclusion on a separate
        # Form 2555, and the joint return excludes the sum.
        "https://www.irs.gov/pub/irs-prior/i2555--2025.pdf#page=6",
    )

    def formula(person, period, parameters):
        # The formula stops Core carrying and uprating an entry into later years.
        return person.filled_array(-1)
