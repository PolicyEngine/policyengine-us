from policyengine_us.model_api import *


class nyc_taxable_income_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC taxable income deductions"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"
