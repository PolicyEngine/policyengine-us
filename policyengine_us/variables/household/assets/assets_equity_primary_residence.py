from policyengine_us.model_api import *


class assets_equity_primary_residence(Variable):
    value_type          = float
    entity              = Household
    label               = "Difference between value of primary residence and the total amount of debt secured by the primary residence (all mortgages and HELOCs)."
    definition_period   = YEAR
    unit                = USD
