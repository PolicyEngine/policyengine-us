from policyengine_us.model_api import *


class spm_unit_net_income_reported(Variable):
    value_type = float
    entity = SPMUnit
    label = "Reported net income"
    unit = USD
    definition_period = YEAR
