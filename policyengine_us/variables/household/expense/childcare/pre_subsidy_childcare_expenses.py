from policyengine_us.model_api import *


class pre_subsidy_childcare_expenses(Variable):
    value_type = float
    entity = Person
    label = "Pre subsidy child care expenses"
    definition_period = YEAR
    unit = USD
