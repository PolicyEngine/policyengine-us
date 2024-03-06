from policyengine_us.model_api import *


class investment_in_529_plan_indv(Variable):
    value_type = float
    entity = Person
    label = "Individual 529 plan investment amounts"
    unit = USD
    documentation = (
        "Amount invested in a 529 savings plan for each contributor."
    )
    definition_period = YEAR
