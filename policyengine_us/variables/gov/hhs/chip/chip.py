from policyengine_us.model_api import *


class chip(Variable):
    value_type = float
    entity = Person
    label = "CHIP"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        eligible = person("is_chip_eligible", period)
        # Use Medicaid value for now.
        benefit = person("medicaid_benefit_value", period)
        return eligible * benefit
