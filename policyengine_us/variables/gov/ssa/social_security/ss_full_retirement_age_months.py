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

        return select(
            [
                birth_year <= 1937,
                birth_year == 1938,
                birth_year == 1939,
                birth_year == 1940,
                birth_year == 1941,
                birth_year == 1942,
                (birth_year >= 1943) & (birth_year <= 1954),
                birth_year == 1955,
                birth_year == 1956,
                birth_year == 1957,
                birth_year == 1958,
                birth_year == 1959,
                birth_year >= 1960,
            ],
            [
                780,  # 65 years * 12 months
                782,  # 65 years 2 months
                784,  # 65 years 4 months
                786,  # 65 years 6 months
                788,  # 65 years 8 months
                790,  # 65 years 10 months
                792,  # 66 years
                794,  # 66 years 2 months
                796,  # 66 years 4 months
                798,  # 66 years 6 months
                800,  # 66 years 8 months
                802,  # 66 years 10 months
                804,  # 67 years
            ],
        )

