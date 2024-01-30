from policyengine_us.model_api import *


class spm_unit_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Net income"
    definition_period = YEAR
    unit = USD

    adds = ["spm_unit_market_income", "spm_unit_benefits"]
    subtracts = ["spm_unit_taxes", "spm_unit_spm_expenses"]
