from policyengine_us.model_api import *


class ss_full_retirement_age_months(Variable):
    value_type = int
    entity = Person
    definition_period = ETERNITY
    label = "Social Security full retirement age in months"
    documentation = (
        "Full retirement age for Social Security benefits, expressed in months"
    )
    reference = (
        "https://www.ssa.gov/OACT/ProgData/nra.html",
        "https://www.law.cornell.edu/uscode/text/42/416#l",
    )

    def formula(person, period, parameters):
        age = person("age", period)
        birth_year = period.start.year - age

        # Full retirement age schedule per 42 USC 416(l)
        # https://www.ssa.gov/OACT/ProgData/nra.html

        # Get FRA based on birth year from scale parameter
        p = parameters(period).gov.ssa.social_security

        # Use scale parameter to get FRA for each person's birth year
        fra_months = p.full_retirement_age_by_birth_year.calc(birth_year)

        return fra_months.astype(int)
