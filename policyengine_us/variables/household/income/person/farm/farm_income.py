from policyengine_us.model_api import *


class farm_income(Variable):
    value_type = float
    entity = Person
    label = "Farm income"
    unit = USD
    documentation = "Income from agricultural businesses. Do not include this income in self-employment income."
    definition_period = YEAR
