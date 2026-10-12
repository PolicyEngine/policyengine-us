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
        "https://academic.oup.com/restud/article-abstract/72/2/395/1558553",
    ]

    def formula(person, period, parameters):
        elasticities = parameters(
            period
        ).gov.simulation.labor_supply_responses.elasticities
        base_elasticity = elasticities.income
        age = person("age", period.this_year)
        age_multiplier = where(
            age >= elasticities.income_age_threshold,
            elasticities.income_age_multiplier_over_threshold,
            1.0,
        )
        return base_elasticity * age_multiplier
