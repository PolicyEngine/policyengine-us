from policyengine_us.model_api import *


class mt_total_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana total income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
