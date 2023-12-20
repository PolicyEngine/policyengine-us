from policyengine_us.model_api import *


class ky_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
