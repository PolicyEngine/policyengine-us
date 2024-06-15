from policyengine_us.model_api import *


class estate_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "income from estates"
    unit = USD
    definition_period = YEAR
