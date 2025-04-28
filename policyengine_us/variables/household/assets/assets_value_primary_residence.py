from policyengine_us.model_api import *


class assets_value_primary_residence(Variable):
    value_type          = float
    entity              = Household
    label               = "Value of primary residence. Excludes the part of a farm or ranch used in a farming or ranching business."
    definition_period   = YEAR
    unit                = USD
