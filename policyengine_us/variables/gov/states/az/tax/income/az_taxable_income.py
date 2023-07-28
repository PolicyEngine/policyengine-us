from policyengine_us.model_api import *


class az_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
