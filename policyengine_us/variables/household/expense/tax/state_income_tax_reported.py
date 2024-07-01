from policyengine_us.model_api import *


class state_income_tax_reported(Variable):
    value_type = float
    entity = Person
    label = "reported State income tax"
    unit = USD
    definition_period = YEAR
