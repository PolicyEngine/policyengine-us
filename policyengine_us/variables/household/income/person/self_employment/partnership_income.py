from policyengine_us.model_api import *


class partnership_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "partnership income"
    unit = USD
    definition_period = YEAR
