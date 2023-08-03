from policyengine_us.model_api import *


class e07240(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Retirement savings contributions credit from Form 8880"
    unit = USD


retirement_savings_credit = variable_alias("retirement_savings_credit", e07240)
