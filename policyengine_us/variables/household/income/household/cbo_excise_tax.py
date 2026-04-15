from policyengine_us.model_api import *


class cbo_excise_tax(Variable):
    value_type = float
    entity = Household
    label = "Optional excise tax incidence input for CBO analysis"
    documentation = (
        "Optional household federal excise tax incidence input for "
        "CBO-style analysis. This is reserved for future explicit incidence "
        "allocation and is not included in the default PE-US CBO benchmark."
    )
    definition_period = YEAR
    unit = USD
