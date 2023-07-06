from policyengine_us.model_api import *


class mi_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan taxable income"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
