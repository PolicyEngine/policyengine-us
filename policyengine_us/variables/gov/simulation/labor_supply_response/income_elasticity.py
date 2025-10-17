from policyengine_us.model_api import *


class income_elasticity(Variable):
    value_type = float
    entity = Person
    label = "income elasticity of labor supply"
    unit = "/1"
    definition_period = YEAR
    reference = [
        "https://www.cbo.gov/publication/43675",
        "https://www.cbo.gov/publication/43676",
    ]

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.simulation.labor_supply_responses.elasticities.income

        # Check if global override is set
        if p.all != 0:
            return p.all

        # Use age-specific elasticities
        age = person("age", period.this_year)
        is_65_or_over = age >= 65

        elasticities = where(
            is_65_or_over,
            p.by_age["65_and_over"],
            p.by_age.under_65,
        )

        return elasticities
