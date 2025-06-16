from policyengine_us.model_api import *


class medicaid_enrolled(Variable):
    value_type = float
    entity = Person
    label = "Medicaid enrolled"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a"
    defined_for = "is_medicaid_eligible"
    adds = ["takes_up_medicaid_if_eligible"]
