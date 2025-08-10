from policyengine_us.model_api import *


class ss_earnings_test_applicable(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Social Security earnings test applies"
    documentation = "Whether the Social Security earnings test applies to this person (under FRA)"
    reference = "https://www.ssa.gov/OACT/COLA/rtea.html"

    def formula(person, period, parameters):
        age = person("age", period)
        fra_months = person("ss_full_retirement_age_months", period)
        fra_years = fra_months / MONTHS_IN_YEAR

        # Earnings test applies if under FRA
        return age < fra_years
