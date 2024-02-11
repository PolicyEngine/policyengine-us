from policyengine_us.model_api import *


class retirement_savings_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Retirement savings credit"
    definition_period = YEAR
    documentation = "Retirement savings contributions credit from Form 8880"
    unit = USD
