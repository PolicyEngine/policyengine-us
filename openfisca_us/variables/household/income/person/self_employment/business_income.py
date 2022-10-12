from policyengine_us.model_api import *


class business_income(Variable):
    value_type = float
    entity = Person
    label = "Business income (losses ignored)"
    unit = USD
    documentation = "Business income, capped at zero."
    definition_period = YEAR

    def formula(person, period, parameters):
        profit = person("self_employment_income", period)
        rents = person("rental_income", period)
        positive_profit = max_(profit, 0)
        positive_rents = max_(rents, 0)
        return positive_profit + positive_rents
