from policyengine_us.model_api import *


class personal_interest(Variable):
    value_type = float
    entity = Person
    label = "Personal interest"
    unit = USD
    definition_period = YEAR
