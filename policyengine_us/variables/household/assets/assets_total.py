from policyengine_us.model_api import *


class assets_total(Variable):
    value_type          = float
    entity              = Household
    label               = "Total value of all assets held by household"
    definition_period   = YEAR
    unit                = USD
