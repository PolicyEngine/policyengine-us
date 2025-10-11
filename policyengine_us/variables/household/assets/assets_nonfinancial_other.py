from policyengine_us.model_api import *


class assets_nonfinancial_other(Variable):
    value_type          = float
    entity              = Household
    label               = "Total value of other nonfinancial assets held by household"
    definition_period   = YEAR
    unit                = USD
