from policyengine_us.model_api import *


class cbo_corporate_income_tax(Variable):
    value_type = float
    entity = Household
    label = "Optional corporate income tax incidence input for CBO analysis"
    documentation = (
        "Optional household share of federal corporate income taxes for "
        "CBO-style analysis. Defaults to zero until an explicit incidence "
        "allocation is provided."
    )
    definition_period = YEAR
    unit = USD
