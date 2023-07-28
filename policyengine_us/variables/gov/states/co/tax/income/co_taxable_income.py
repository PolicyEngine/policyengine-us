from policyengine_us.model_api import *


class co_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
