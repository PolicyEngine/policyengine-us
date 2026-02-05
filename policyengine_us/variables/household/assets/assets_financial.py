from policyengine_us.model_api import *


class assets_financial(Variable):
    value_type          = float
    entity              = Household
    label               = "Total value of financial assets held by household"
    definition_period   = YEAR
    unit                = USD
