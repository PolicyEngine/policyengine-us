from policyengine_us.model_api import *


class nyc_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC taxable income"
    unit = USD
    definition_period = YEAR
