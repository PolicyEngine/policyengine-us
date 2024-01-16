from policyengine_us.model_api import *


class employment_income_last_year(Variable):
    value_type = float
    entity = Person
    label = "Label"
    unit = USD
    documentation = "Description"
    definition_period = YEAR
