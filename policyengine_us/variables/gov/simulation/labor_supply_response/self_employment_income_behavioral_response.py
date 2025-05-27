from policyengine_us.model_api import *


class self_employment_income_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "self-employment income behavioral response"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        lsr = person("labor_supply_behavioral_response", period)
        emp_response = person("employment_income_behavioral_response", period)

        return lsr - emp_response
