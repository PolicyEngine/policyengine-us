from policyengine_us.model_api import *


class id_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
