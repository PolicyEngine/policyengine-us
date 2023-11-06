from policyengine_us.model_api import *


class ri_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island taxable income"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR
