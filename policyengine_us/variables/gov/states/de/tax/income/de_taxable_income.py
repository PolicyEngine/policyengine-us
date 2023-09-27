from policyengine_us.model_api import *


class de_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
