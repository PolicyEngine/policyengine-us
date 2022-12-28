from policyengine_us.model_api import *


class equiv_household_net_income(Variable):
    value_type = float
    entity = Household
    label = "equivalised net income"
    definition_period = YEAR
    unit = USD
    adds = ["spm_unit_oecd_equiv_net_income"]
