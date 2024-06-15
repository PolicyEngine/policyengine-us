from policyengine_us.model_api import *


class s_corp_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "S-corporation income"
    unit = USD
    definition_period = YEAR
