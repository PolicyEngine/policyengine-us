from policyengine_us.model_api import *


class care_and_support_expense(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = YEAR
    label = "Total expense for this person's care and support"
