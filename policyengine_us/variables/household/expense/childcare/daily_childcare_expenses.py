from policyengine_us.model_api import *


class daily_childcare_expenses(Variable):
    value_type = float
    entity = Person
    label = "Daily child care expenses"
    definition_period = YEAR
    unit = USD
