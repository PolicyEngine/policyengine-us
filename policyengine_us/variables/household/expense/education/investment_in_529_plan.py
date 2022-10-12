from policyengine_us.model_api import *


class investment_in_529_plan(Variable):
    value_type = float
    entity = TaxUnit
    label = "529 plan investment"
    unit = USD
    documentation = "Amount invested in a 529 savings plan."
    definition_period = YEAR
