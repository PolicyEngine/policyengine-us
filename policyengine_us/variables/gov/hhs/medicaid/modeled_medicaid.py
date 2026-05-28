from policyengine_us.model_api import *


class modeled_medicaid(Variable):
    value_type = float
    entity = Person
    label = "Modeled Medicaid"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a"
    defined_for = "medicaid_enrolled"
    adds = ["modeled_medicaid_cost"]
