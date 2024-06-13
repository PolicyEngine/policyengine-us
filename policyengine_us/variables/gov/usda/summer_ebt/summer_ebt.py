from policyengine_us.model_api import *


class summer_ebt(Variable):
    value_type = float
    entity = Person
    label = "Summer EBT"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1762#b_2"

    def formula(person, period, parameters):
        amount = parameters(period).gov.usda.summer_ebt.amount
        eligible = person("is_summer_ebt_eligible", period)
        return eligible * amount
