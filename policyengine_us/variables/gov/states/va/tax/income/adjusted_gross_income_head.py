from policyengine_us.model_api import *


class adjusted_gross_income_head(Variable):
    value_type = float
    entity = Person
    label = "Adjusted gross income of head"
    unit = USD
    definition_period = YEAR
