from policyengine_us.model_api import *


class care_and_support_costs(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = YEAR
    label = "Total costs for this person's care and support"
