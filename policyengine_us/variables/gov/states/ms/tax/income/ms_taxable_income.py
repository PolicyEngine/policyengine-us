from policyengine_us.model_api import *


class ms_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
