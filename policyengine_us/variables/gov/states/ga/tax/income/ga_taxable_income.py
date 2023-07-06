from policyengine_us.model_api import *


class ga_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
