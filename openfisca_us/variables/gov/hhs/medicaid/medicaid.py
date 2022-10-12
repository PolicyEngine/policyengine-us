from policyengine_us.model_api import *


class medicaid(Variable):
    value_type = float
    entity = Person
    label = "Medicaid"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a"

    def formula(person, period, parameters):
        eligible = person("is_medicaid_eligible", period)
        benefit = person("medicaid_benefit_value", period)
        return eligible * benefit
