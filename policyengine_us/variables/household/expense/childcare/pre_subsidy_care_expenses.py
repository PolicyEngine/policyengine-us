from policyengine_us.model_api import *


class pre_subsidy_care_expenses(Variable):
    value_type = float
    entity = Person
    label = "Pre subsidy care expenses"
    definition_period = MONTH
    unit = USD
