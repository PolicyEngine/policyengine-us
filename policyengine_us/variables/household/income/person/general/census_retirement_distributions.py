from policyengine_us.model_api import *


class census_retirement_distributions(Variable):
    value_type = float
    entity = Person
    label = "Census money income retirement account distributions"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Distributions from retirement accounts that the Census Bureau counts "
        "as money income. Since the redesigned processing system the Current "
        "Population Survey introduced in 2019, which covers 2018 income, the "
        "survey leaves distributions to people under 58 out of total income. "
        "Census applies the test to age at the survey date; this variable uses "
        "age in the income year."
    )
    reference = (
        # Pages 57 and 58 define the distribution amounts by age.
        "https://www2.census.gov/programs-surveys/cps/datasets/2026/march/asec2026_ddl_pub_full.pdf#page=57",
        "https://cps.ipums.org/cps-action/variables/INCRETIR",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.household
        counted = person("age", period) >= (
            p.census_retirement_distributions_minimum_age
        )
        return counted * person("retirement_distributions", period)
