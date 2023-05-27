from policyengine_us.model_api import *


class mt_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
