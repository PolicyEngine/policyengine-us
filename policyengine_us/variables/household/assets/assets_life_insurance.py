from policyengine_us.model_api import *


class assets_life_insurance(Variable):
    value_type          = float
    entity              = Household
    label               = "Total cash value of whole life insurance held by household"
    definition_period   = YEAR
    unit                = USD
