from policyengine_us.model_api import *


class child_care_expenses(Variable):
    value_type = float
    entity = Person
    label = "Pre subsidy child care expenses"
    definition_period = YEAR
    unit = USD
