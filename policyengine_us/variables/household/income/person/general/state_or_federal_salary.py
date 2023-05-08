from policyengine_us.model_api import *


class state_or_federal_salary(Variable):
    value_type = float
    entity = Person
    label = "state or federal salary"
    unit = USD
    definition_period = YEAR
