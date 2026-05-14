from policyengine_us.model_api import *


class cbo_excise_tax(Variable):
    value_type = float
    entity = Household
    label = "Optional excise tax incidence input for CBO analysis"
    documentation = (
        "Optional household share of federal excise taxes for CBO-style "
        "analysis. Defaults to zero until an explicit incidence allocation is "
        "provided."
    )
    definition_period = YEAR
    unit = USD
