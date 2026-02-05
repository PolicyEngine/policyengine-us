from policyengine_us.model_api import *


class debt_total(Variable):
    value_type          = float
    entity              = Household
    label               = "Total value of debt held by household, includes principal residence debt, debt for other residential property, credit card debt, installment loans, and other debt."
    definition_period   = YEAR
    unit                = USD
