from policyengine_us.model_api import *


class nm_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM
