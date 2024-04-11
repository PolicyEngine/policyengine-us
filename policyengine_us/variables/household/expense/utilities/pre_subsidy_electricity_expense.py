from policyengine_us.model_api import *


class pre_subsidy_electricity_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pre subsidy electricity expense"
    unit = USD
    definition_period = YEAR
