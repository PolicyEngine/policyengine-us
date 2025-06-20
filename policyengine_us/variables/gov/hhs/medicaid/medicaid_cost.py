from policyengine_us.model_api import *


class medicaid_cost(Variable):
    value_type = float
    entity = Person
    label = "Medicaid_cost"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a"
    defined_for = "medicaid_enrolled"
    adds = ["medicaid_cost_if_enrolled"]
