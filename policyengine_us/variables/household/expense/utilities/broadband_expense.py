from policyengine_us.model_api import *


class broadband_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Broadband expense"
    unit = USD
    definition_period = YEAR
